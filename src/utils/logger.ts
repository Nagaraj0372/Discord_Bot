import pino from 'pino';
import { env } from '../config/env.js';

export const logger = pino({
  level: env.LOG_LEVEL,
  redact: {
    paths: [
      'DISCORD_TOKEN',
      'DATABASE_URL',
      'LAVALINK_PASSWORD',
      'API_KEY',
      'req.headers.authorization',
      'req.headers.x-api-key',
    ],
    censor: '[REDACTED]',
  },
});
