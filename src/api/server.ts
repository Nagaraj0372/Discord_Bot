import express from 'express';
import { timingSafeEqual } from 'node:crypto';
import type { Server } from 'node:http';
import { env } from '../config/env.js';
import { prisma } from '../database/client.js';
import { logger } from '../utils/logger.js';

export function startApi(): Server {
  const app = express();
  app.disable('x-powered-by');

  app.get('/health', (_request, response) => {
    response.json({ status: 'ok', service: 'gokul-bot', uptime: process.uptime() });
  });

  app.get('/ready', async (_request, response) => {
    try {
      await prisma.$queryRaw`SELECT 1`;
      response.json({ status: 'ready' });
    } catch (error) {
      logger.error({ err: error }, 'Readiness check failed');
      response.status(503).json({ status: 'not_ready' });
    }
  });

  app.use('/api', (request, response, next) => {
    const suppliedKey = request.header('x-api-key');
    if (!env.API_KEY || !suppliedKey) {
      response.status(401).json({ error: 'unauthorized' });
      return;
    }

    const supplied = Buffer.from(suppliedKey);
    const expected = Buffer.from(env.API_KEY);
    if (supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) {
      response.status(401).json({ error: 'unauthorized' });
      return;
    }
    next();
  });

  app.get('/api/status', (_request, response) => {
    response.json({ uptime: process.uptime(), node: process.version });
  });

  const server = app.listen(env.PORT, '0.0.0.0', () => {
    logger.info({ port: env.PORT }, 'Health API listening');
  });
  server.on('error', (error) => {
    logger.error({ err: error }, 'Health API server error');
  });
  return server;
}
