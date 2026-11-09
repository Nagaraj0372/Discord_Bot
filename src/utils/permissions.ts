import { GuildMember, PermissionFlagsBits } from 'discord.js';

export function isStaff(member: GuildMember): boolean {
  return (
    member.permissions.has(PermissionFlagsBits.ManageGuild) ||
    member.permissions.has(PermissionFlagsBits.ModerateMembers)
  );
}

export function canActOn(actor: GuildMember, target: GuildMember): boolean {
  return (
    actor.id !== target.id &&
    target.id !== actor.guild.ownerId &&
    actor.roles.highest.comparePositionTo(target.roles.highest) > 0
  );
}
