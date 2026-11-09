import 'dotenv/config';
import { z } from 'zod';
import { requireDatabaseUrl } from './database-url.js';

const databaseUrl = requireDatabaseUrl();

const booleanFromEnv = z.preprocess((value) => {
  if (typeof value !== 'string') return value;
  if (value.toLowerCase() === 'true') return true;
  if (value.toLowerCase() === 'false') return false;
  return value;
}, z.boolean());

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  DISCORD_TOKEN: z.string().min(1),
  CLIENT_ID: z.string().min(1),
  GUILD_ID: z.string().optional(),
  DATABASE_URL: z.string().url(),
  LAVALINK_HOST: z.string().min(1).default('localhost'),
  LAVALINK_PORT: z.coerce.number().int().min(1).max(65535).default(2333),
  LAVALINK_PASSWORD: z.string().min(1),
  LAVALINK_SECURE: booleanFromEnv.default(false),
  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),
  API_KEY: z.string().optional(),
});

const result = envSchema.safeParse({ ...process.env, DATABASE_URL: databaseUrl });

if (!result.success) {
  const issues = result.error.issues
    .map((issue) => `${issue.path.join('.') || 'environment'}: ${issue.message}`)
    .join('; ');
  throw new Error(`Invalid environment configuration: ${issues}`);
}

export const env = result.data;
