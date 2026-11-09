import {
  Client,
  GatewayIntentBits,
  Events,
} from 'discord.js';
import type { Server } from 'node:http';
import { env } from './config/env.js';
import { prisma } from './database/client.js';
import { registerHandlers } from './handlers.js';
import { startApi } from './api/server.js';
import { createMusic } from './music/manager.js';
import { logger } from './utils/logger.js';

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildVoiceStates,
  ],
});
const music = createMusic(client);
client.on(Events.Raw, (packet) => {
  music.updateVoiceState(packet);
});
registerHandlers(client);

client.once(Events.ClientReady, (readyClient) => {
  music.init(readyClient.user.id);
  logger.info(
    { user: readyClient.user.tag, guilds: readyClient.guilds.cache.size },
    'GOKUL BOT online',
  );
});

let apiServer: Server | undefined;
let shuttingDown = false;

async function shutdown(signal: string): Promise<void> {
  if (shuttingDown) return;
  shuttingDown = true;
  logger.info({ signal }, 'Shutting down');
  for (const nodeName of music.nodeMap.keys()) {
    music.destroyNode(nodeName);
  }
  client.destroy();

  if (apiServer?.listening) {
    await new Promise<void>((resolve, reject) => {
      apiServer?.close((error) => (error ? reject(error) : resolve()));
    });
  }

  await prisma.$disconnect();
}

process.once('SIGTERM', () => {
  void shutdown('SIGTERM').catch((error: unknown) => {
    logger.error({ err: error }, 'Shutdown failed');
    process.exitCode = 1;
  });
});
process.once('SIGINT', () => {
  void shutdown('SIGINT').catch((error: unknown) => {
    logger.error({ err: error }, 'Shutdown failed');
    process.exitCode = 1;
  });
});

try {
  apiServer = startApi();
  await prisma.$connect();
  await client.login(env.DISCORD_TOKEN);
} catch (error) {
  logger.fatal({ err: error }, 'GOKUL BOT startup failed');
  try {
    await shutdown('startup-error');
  } catch (shutdownError) {
    logger.error({ err: shutdownError }, 'Cleanup after startup failure failed');
  }
  process.exitCode = 1;
}
