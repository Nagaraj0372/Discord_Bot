import { ChatInputCommandInteraction, SlashCommandBuilder } from 'discord.js'; export type Command={data:SlashCommandBuilder;execute:(i:ChatInputCommandInteraction)=>Promise<unknown>};
