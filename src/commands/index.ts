import {
  ChatInputCommandInteraction,
  SlashCommandBuilder,
} from 'discord.js';
import { ensureGuild, ensureUser, prisma } from '../database/client.js';
import { claimReward, EconomyCooldownError } from '../services/economy.js';
import { consumeCooldown } from '../utils/cooldown.js';
import type { BotCommand } from '../types/command.js';

const commands: BotCommand[] = [];

function add(
  name: string,
  description: string,
  execute: (interaction: ChatInputCommandInteraction) => Promise<void>,
  guildOnly = false,
): void {
  let data = new SlashCommandBuilder().setName(name).setDescription(description);
  if (guildOnly) data = data.setDMPermission(false);
  commands.push({ data, execute });
}

async function getGuildUser(interaction: ChatInputCommandInteraction) {
  if (!interaction.guild) throw new Error('This command can only be used in a server.');

  const guild = await ensureGuild(interaction.guild.id);
  const user = await ensureUser(guild.id, interaction.user.id);
  return { guild, user };
}

add('ping', 'Check the bot response and gateway latency', async (interaction) => {
  await interaction.reply(`Pong! Gateway latency: ${interaction.client.ws.ping} ms.`);
});

add('uptime', 'Show how long the bot has been running', async (interaction) => {
  const seconds = Math.floor(process.uptime());
  await interaction.reply(`Online for ${seconds} seconds.`);
});

add('botinfo', 'Show bot runtime information', async (interaction) => {
  await interaction.reply(
    `GOKUL BOT • Discord.js v14 • Node.js ${process.versions.node} • ${interaction.client.guilds.cache.size} servers`,
  );
});

add('help', 'List implemented commands', async (interaction) => {
  await interaction.reply(commands.map(({ data }) => `/${data.name}`).join(', '));
});

add('serverinfo', 'Show information about this server', async (interaction) => {
  if (!interaction.guild) throw new Error('This command can only be used in a server.');
  await interaction.reply(
    `${interaction.guild.name} • ${interaction.guild.memberCount} members • ID ${interaction.guild.id}`,
  );
});

add('userinfo', 'Show information about yourself', async (interaction) => {
  await interaction.reply(`${interaction.user.tag} • ID ${interaction.user.id}`);
});

add('avatar', 'Show your account avatar', async (interaction) => {
  await interaction.reply(interaction.user.displayAvatarURL({ size: 1024 }));
});

add(
  'level',
  'Show your level and XP in this server',
  async (interaction) => {
    const { guild, user } = await getGuildUser(interaction);
    const level = await prisma.level.findUnique({
      where: { guildId_userId: { guildId: guild.id, userId: user.id } },
    });
    await interaction.reply(`Level ${level?.level ?? 0} • ${level?.xp ?? 0} XP.`);
  },
  true,
);

add(
  'leaderboard',
  'Show the top ten XP earners in this server',
  async (interaction) => {
    const { guild } = await getGuildUser(interaction);
    const levels = await prisma.level.findMany({
      where: { guildId: guild.id },
      orderBy: [{ xp: 'desc' }, { userId: 'asc' }],
      take: 10,
      include: { user: { select: { userId: true } } },
    });

    const description = levels.length
      ? levels.map((entry, index) => `${index + 1}. <@${entry.user.userId}> — ${entry.xp} XP`).join('\n')
      : 'No XP has been earned yet.';
    await interaction.reply({ content: description, allowedMentions: { parse: [] } });
  },
  true,
);

add(
  'balance',
  'Show your wallet and bank balance',
  async (interaction) => {
    const { user } = await getGuildUser(interaction);
    const account = await prisma.economyAccount.findUniqueOrThrow({
      where: { userId: user.id },
    });
    await interaction.reply(`Wallet: ${account.wallet} • Bank: ${account.bank}.`);
  },
  true,
);

add(
  'daily',
  'Claim your daily coins',
  async (interaction) => {
    const { user } = await getGuildUser(interaction);
    try {
      await claimReward(user.id, 'daily', 100n);
    } catch (error) {
      if (error instanceof EconomyCooldownError) {
        await interaction.reply('You have already claimed your daily coins; please try again later.');
        return;
      }
      throw error;
    }
    await interaction.reply('You received 100 coins.');
  },
  true,
);

add(
  'work',
  'Work for coins once per hour',
  async (interaction) => {
    const { user } = await getGuildUser(interaction);
    try {
      await claimReward(user.id, 'work', 50n);
    } catch (error) {
      if (error instanceof EconomyCooldownError) {
        await interaction.reply('You have already worked recently; please try again later.');
        return;
      }
      throw error;
    }
    await interaction.reply('You earned 50 coins.');
  },
  true,
);

export async function executeCommand(
  command: BotCommand,
  interaction: ChatInputCommandInteraction,
): Promise<void> {
  const remaining = consumeCooldown(`${interaction.user.id}:${command.data.name}`, 1_500);
  if (remaining > 0) {
    await interaction.reply({
      content: `Please wait ${remaining} second(s) before using this command again.`,
      ephemeral: true,
    });
    return;
  }

  await command.execute(interaction);
}

export default commands;
