import { Client } from 'discord.js';
import { Riffy } from 'riffy';
import { env } from '../config/env.js';
import { logger } from '../utils/logger.js';

export function createMusic(client: Client): Riffy {
  const music = new Riffy(
    client,
    [
      {
        name: 'primary',
        host: env.LAVALINK_HOST,
        port: env.LAVALINK_PORT,
        password: env.LAVALINK_PASSWORD,
        secure: env.LAVALINK_SECURE,
      },
    ],
    {
      send: (payload) => {
        client.guilds.cache.get(payload.d.guild_id)?.shard.send(payload);
      },
      defaultSearchPlatform: 'ytmsearch',
      restVersion: 'v4',
      bypassChecks: { nodeFetchInfo: false },
      migrateOnDisconnect: true,
      migrateOnFailure: true,
    },
  );

  music.on('nodeConnect', (node) => {
    logger.info({ node: node.name }, 'Lavalink node connected');
  });
  music.on('nodeError', (node, error) => {
    logger.error({ node: node.name, err: error }, 'Lavalink node error');
  });
  music.on('nodeDisconnect', (node, reason) => {
    logger.warn({ node: node.name, reason }, 'Lavalink node disconnected');
  });

  return music;
}
