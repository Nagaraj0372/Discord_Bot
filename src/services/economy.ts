import { prisma } from '../database/client.js';

const DAY_MS = 24 * 60 * 60 * 1000;
const WORK_COOLDOWN_MS = 60 * 60 * 1000;

export class EconomyCooldownError extends Error {
  constructor() {
    super('That reward is still on cooldown.');
    this.name = 'EconomyCooldownError';
  }
}

export async function claimReward(
  userId: string,
  kind: 'daily' | 'work',
  amount: bigint,
  now = new Date(),
): Promise<void> {
  if (amount <= 0n) throw new RangeError('Reward amount must be positive.');

  const field = kind === 'daily' ? 'lastDaily' : 'lastWork';
  const cooldown = kind === 'daily' ? DAY_MS : WORK_COOLDOWN_MS;
  const eligibleBefore = new Date(now.getTime() - cooldown);

  await prisma.$transaction(async (transaction) => {
    const result = await transaction.economyAccount.updateMany({
      where: {
        userId,
        OR: [{ [field]: null }, { [field]: { lte: eligibleBefore } }],
      },
      data: {
        wallet: { increment: amount },
        [field]: now,
      },
    });

    if (result.count !== 1) throw new EconomyCooldownError();

    const user = await transaction.user.findUniqueOrThrow({
      where: { id: userId },
      select: { guildId: true },
    });

    await transaction.transaction.create({
      data: {
        guildId: user.guildId,
        userId,
        amount,
        type: kind,
      },
    });
  });
}
