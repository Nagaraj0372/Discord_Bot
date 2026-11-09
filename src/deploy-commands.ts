import { REST, Routes } from 'discord.js';
import { env } from './config/env.js';
import { commands } from './handlers.js';
import { logger } from './utils/logger.js';

const rest = new REST({ version: '10' }).setToken(env.DISCORD_TOKEN);
const body = commands.map((command) => command.data.toJSON());
const route = env.GUILD_ID
  ? Routes.applicationGuildCommands(env.CLIENT_ID, env.GUILD_ID)
  : Routes.applicationCommands(env.CLIENT_ID);

try {
  await rest.put(route, { body });
  logger.info({ count: body.length }, 'Registered Discord application commands');
} catch (error) {
  logger.error({ err: error }, 'Failed to register Discord application commands');
  process.exitCode = 1;
}
