const expirations = new Map<string, number>();

export function consumeCooldown(key: string, durationMs: number, now = Date.now()): number {
  if (!Number.isFinite(durationMs) || durationMs <= 0) {
    throw new RangeError('Cooldown duration must be a positive finite number.');
  }

  const expiresAt = expirations.get(key) ?? 0;
  if (expiresAt > now) return Math.ceil((expiresAt - now) / 1000);

  expirations.set(key, now + durationMs);

  if (expirations.size > 10_000) {
    for (const [entry, expiration] of expirations) {
      if (expiration <= now) expirations.delete(entry);
    }
  }

  return 0;
}

export function clearCooldowns(): void {
  expirations.clear();
}
