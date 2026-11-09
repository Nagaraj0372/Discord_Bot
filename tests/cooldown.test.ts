import { beforeEach, describe, expect, it } from 'vitest';
import { clearCooldowns, consumeCooldown } from '../src/utils/cooldown.js';
import { requireDatabaseUrl } from '../src/config/database-url.js';

describe('consumeCooldown', () => {
  beforeEach(() => clearCooldowns());

  it('allows the first action and reports remaining time for a repeat', () => {
    expect(consumeCooldown('user:command', 1_500, 1_000)).toBe(0);
    expect(consumeCooldown('user:command', 1_500, 1_200)).toBe(2);
  });

  describe('requireDatabaseUrl', () => {
    it('rejects empty or whitespace-only values', () => {
      expect(() => requireDatabaseUrl({ DATABASE_URL: '' })).toThrow(
        'DATABASE_URL is missing.',
      );
      expect(() => requireDatabaseUrl({ DATABASE_URL: '  \t' })).toThrow(
        'DATABASE_URL is missing.',
      );
    });

    it('rejects non-PostgreSQL URLs without exposing their contents', () => {
      expect(() =>
        requireDatabaseUrl({ DATABASE_URL: 'https://example.invalid/path' }),
      ).toThrow('DATABASE_URL must be a valid PostgreSQL connection URL.');
    });

    it('rejects a missing URL with safe Railway setup guidance', () => {
      expect(() => requireDatabaseUrl({})).toThrow(
        'DATABASE_URL is missing.\nConfigure the Railway PostgreSQL connection reference in the bot service.',
      );
    });

    it('returns a configured URL without modifying it', () => {
      const url = 'postgresql://db.example.invalid:5432/bot?schema=public';
      expect(requireDatabaseUrl({ DATABASE_URL: url })).toBe(url);
    });
  });

  it('allows an action after its cooldown expires', () => {
    expect(consumeCooldown('user:command', 1_000, 1_000)).toBe(0);
    expect(consumeCooldown('user:command', 1_000, 2_000)).toBe(0);
  });

  it('rejects invalid cooldown durations', () => {
    expect(() => consumeCooldown('user:command', 0)).toThrow(RangeError);
  });
});
