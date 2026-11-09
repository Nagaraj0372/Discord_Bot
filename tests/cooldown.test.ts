import { beforeEach, describe, expect, it } from 'vitest';
import { clearCooldowns, consumeCooldown } from '../src/utils/cooldown.js';

describe('consumeCooldown', () => {
  beforeEach(() => clearCooldowns());

  it('allows the first action and reports remaining time for a repeat', () => {
    expect(consumeCooldown('user:command', 1_500, 1_000)).toBe(0);
    expect(consumeCooldown('user:command', 1_500, 1_200)).toBe(2);
  });

  it('allows an action after its cooldown expires', () => {
    expect(consumeCooldown('user:command', 1_000, 1_000)).toBe(0);
    expect(consumeCooldown('user:command', 1_000, 2_000)).toBe(0);
  });

  it('rejects invalid cooldown durations', () => {
    expect(() => consumeCooldown('user:command', 0)).toThrow(RangeError);
  });
});
