import { randomInt } from 'node:crypto';
import { Events, type Client } from 'discord.js';
import { ensureGuild, ensureUser, prisma } from './database/client.js';
import commands, { executeCommand } from './commands/index.js';
import { logger } from './utils/logger.js';
import { consumeCooldown } from './utils/cooldown.js';

export function registerHandlers(client: Client): void {
  const commandMap = new Map(commands.map((command) => [command.data.name, command]));

  client.on(Events.InteractionCreate, async (interaction) => {
    if (!interaction.isChatInputCommand()) return;

    const command = commandMap.get(interaction.commandName);
    if (!command) {
      await interaction.reply({ content: 'That command is not available.', ephemeral: true });
      return;
    }

    try {
      await executeCommand(command, interaction);
    } catch (error) {
      logger.error(
        { err: error, command: interaction.commandName, userId: interaction.user.id },
        'Command execution failed',
      );
      const content = 'The command failed. Please try again later.';
      if (interaction.deferred || interaction.replied) {
        await interaction.followUp({ content, ephemeral: true });
      } else {
        await interaction.reply({ content, ephemeral: true });
      }
    }
  });

  client.on(Events.MessageCreate, async (message) => {
    if (!message.inGuild() || message.author.bot) return;
    if (consumeCooldown(`xp:${message.guildId}:${message.author.id}`, 60_000) > 0) return;

    try {
      const guild = await ensureGuild(message.guildId);
      const user = await ensureUser(guild.id, message.author.id);
      const amount = randomInt(15, 26);

      await prisma.$transaction(async (transaction) => {
        const level = await transaction.level.upsert({
          where: { guildId_userId: { guildId: guild.id, userId: user.id } },
          create: { guildId: guild.id, userId: user.id, xp: amount },
          update: { xp: { increment: amount } },
        });
        const newLevel = Math.floor(Math.sqrt(level.xp / 100));

        if (newLevel > level.level) {
          await transaction.level.update({
            where: { guildId_userId: { guildId: guild.id, userId: user.id } },
            data: { level: newLevel },
          });
        }

        await transaction.xPEvent.create({
          data: { guildId: guild.id, userId: user.id, amount, source: 'message' },
        });
      });
    } catch (error) {
      logger.error(
        { err: error, guildId: message.guildId, userId: message.author.id },
        'XP award failed',
      );
    }
  });

  client.on(Events.Error, (error) => {
    logger.error({ err: error }, 'Discord client error');
  });
}

export { commands };
