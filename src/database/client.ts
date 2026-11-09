import { PrismaClient } from '@prisma/client';
import { logger } from '../utils/logger.js';

export const prisma = new PrismaClient({
  log: [{ emit: 'event', level: 'error' }],
});

prisma.$on('error', (event) => {
  logger.error({ message: event.message }, 'Database error');
});

export async function ensureGuild(discordId: string) {
  return prisma.guild.upsert({
    where: { discordId },
    create: { discordId, settings: { create: {} } },
    update: {},
  });
}

export async function ensureUser(guildId: string, discordUserId: string) {
  return prisma.$transaction(async (transaction) => {
    const user = await transaction.user.upsert({
      where: { guildId_userId: { guildId, userId: discordUserId } },
      create: { guildId, userId: discordUserId },
      update: {},
    });

    await Promise.all([
      transaction.economyAccount.upsert({
        where: { userId: user.id },
        create: { userId: user.id },
        update: {},
      }),
      transaction.level.upsert({
        where: { guildId_userId: { guildId, userId: user.id } },
        create: { guildId, userId: user.id },
        update: {},
      }),
    ]);

    return user;
  });
}
