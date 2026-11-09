from pathlib import Path

root = Path('/home/ubuntu/gokul-bot')
files = {
'package.json': r'''{
  "name": "gokul-bot",
  "version": "1.0.0",
  "private": true,
  "description": "Production-ready all-in-one Discord bot for gaming, coding, cybersecurity and community servers.",
  "type": "module",
  "engines": { "node": ">=22" },
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc -p tsconfig.json",
    "start": "node dist/index.js",
    "lint": "eslint .",
    "test": "vitest run",
    "test:watch": "vitest",
    "db:generate": "prisma generate",
    "db:migrate": "prisma migrate deploy",
    "db:migrate:dev": "prisma migrate dev",
    "db:studio": "prisma studio",
    "register": "tsx src/deploy-commands.ts"
  },
  "dependencies": {
    "@discordjs/builders": "^1.13.0",
    "@prisma/client": "^6.17.1",
    "discord.js": "^14.24.2",
    "express": "^5.1.0",
    "pino": "^10.1.0",
    "pino-http": "^11.0.0",
    "riffy": "^0.1.7",
    "zod": "^4.1.12"
  },
  "devDependencies": {
    "@types/express": "^5.0.5",
    "@types/node": "^24.10.0",
    "@typescript-eslint/eslint-plugin": "^8.46.2",
    "@typescript-eslint/parser": "^8.46.2",
    "eslint": "^9.38.0",
    "prisma": "^6.17.1",
    "tsx": "^4.20.6",
    "typescript": "^5.9.3",
    "vitest": "^3.2.4"
  }
}
''',
'tsconfig.json': r'''{
  "compilerOptions": {"target":"ES2022","module":"NodeNext","moduleResolution":"NodeNext","outDir":"dist","rootDir":"src","strict":true,"esModuleInterop":true,"skipLibCheck":true,"resolveJsonModule":true,"forceConsistentCasingInFileNames":true,"noUncheckedIndexedAccess":true},
  "include": ["src/**/*.ts", "tests/**/*.ts"]
}
''',
'.env.example': r'''NODE_ENV=development
DISCORD_TOKEN=
CLIENT_ID=
GUILD_ID=
DATABASE_URL=
LAVALINK_HOST=lavalink
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=false
HERMES_API_URL=
HERMES_API_KEY=
LOG_LEVEL=info
PORT=3000
API_KEY=
''',
'.gitignore': r'''node_modules/
dist/
.env
.env.*
!.env.example
coverage/
*.log
''',
'.dockerignore': r'''node_modules
dist
.env
.git
''',
'Dockerfile': r'''FROM node:22-bookworm-slim AS base
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates openssl \
    && rm -rf /var/lib/apt/lists/*

FROM base AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tsconfig.json prisma ./
COPY src ./src
RUN npx prisma generate && npm run build

FROM base
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=build /app/node_modules/@prisma/client ./node_modules/@prisma/client
COPY prisma ./prisma
EXPOSE 3000
CMD ["sh", "-c", "if [ -z \"${DATABASE_URL:-}\" ]; then echo 'DATABASE_URL is missing.' >&2; echo 'Configure the Railway PostgreSQL connection reference in the bot service.' >&2; exit 1; fi; npx prisma migrate deploy && node dist/index.js"]
''',
'docker-compose.yml': r'''services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-gokul}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-gokul}
      POSTGRES_DB: ${POSTGRES_DB:-gokul}
    volumes: ["postgres-data:/var/lib/postgresql/data"]
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-gokul} -d ${POSTGRES_DB:-gokul}"], interval: 5s, timeout: 5s, retries: 20 }
  lavalink:
    image: ghcr.io/lavalink-devs/lavalink:4
    profiles: ["local-lavalink"]
    volumes: ["./lavalink/application.yml:/opt/Lavalink/application.yml:ro"]
    ports: ["2333:2333"]
  bot:
    build: .
    env_file: [.env]
    depends_on: { postgres: { condition: service_healthy } }
    ports: ["3000:3000"]
    restart: unless-stopped
volumes: { postgres-data: {} }
''',
'railway.json': r'''{"$schema":"https://railway.app/railway.schema.json","build":{"builder":"DOCKERFILE"},"deploy":{"restartPolicyType":"ON_FAILURE","restartPolicyMaxRetries":10,"healthcheckPath":"/health","healthcheckTimeout":30}}''',
'render.yaml': r'''services:
  - type: worker
    name: gokul-bot
    runtime: docker
    dockerfilePath: ./Dockerfile
    healthCheckPath: /health
    autoDeploy: true
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase: { name: gokul-postgres, property: connectionString }
      - key: DISCORD_TOKEN
        sync: false
      - key: CLIENT_ID
        sync: false
      - key: LAVALINK_HOST
        sync: false
      - key: LAVALINK_PASSWORD
        sync: false
databases:
  - name: gokul-postgres
''',
'lavalink/application.yml': r'''server:
  port: 2333
lavalink:
  server:
    password: ${LAVALINK_PASSWORD:youshallnotpass}
    sources:
      youtube: false
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
plugins:
  - dependency: "com.github.topi314.lavasrc:lavasrc-plugin:4.0.0"
    repository: "https://maven.topi.wtf/releases"
''',
'prisma/schema.prisma': r'''generator client { provider = "prisma-client-js" }
datasource db { provider = "postgresql" url = env("DATABASE_URL") }
model Guild { id String @id discordId String @unique createdAt DateTime @default(now()) updatedAt DateTime @updatedAt settings GuildSettings? users User[] cases ModerationCase[] warnings Warning[] tickets Ticket[] giveaways Giveaway[] levels Level[] xpEvents XPEvent[] reactionRoles ReactionRole[] music MusicPreferences? ai AISettings? }
model GuildSettings { id String @id @default(cuid()) guildId String @unique guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) autoroleId String? welcomeChannelId String? welcomeMessage String? goodbyeChannelId String? goodbyeMessage String? logChannelId String? xpEnabled Boolean @default(true) economyEnabled Boolean @default(true) }
model User { id String @id @default(cuid()) guildId String userId String guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) warnings Warning[] cases ModerationCase[] economy EconomyAccount? level Level? inventory InventoryItem[] createdAt DateTime @default(now()) @@unique([guildId,userId]) @@index([userId]) }
model ModerationCase { id String @id @default(cuid()) guildId String userId String moderatorId String action String reason String? duration Int? guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) user User @relation(fields:[userId], references:[id], onDelete: Cascade) createdAt DateTime @default(now()) @@index([guildId,createdAt]) }
model Warning { id String @id @default(cuid()) guildId String userId String moderatorId String reason String guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) user User @relation(fields:[userId], references:[id], onDelete: Cascade) createdAt DateTime @default(now()) }
model Ticket { id String @id @default(cuid()) guildId String channelId String creatorId String status String @default("OPEN") priority String @default("NORMAL") guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) transcripts TicketTranscript[] createdAt DateTime @default(now()) closedAt DateTime? @@unique([guildId,channelId]) }
model TicketTranscript { id String @id @default(cuid()) ticketId String content String ticket Ticket @relation(fields:[ticketId], references:[id], onDelete: Cascade) createdAt DateTime @default(now()) }
model EconomyAccount { id String @id @default(cuid()) userId String @unique wallet BigInt @default(0) bank BigInt @default(0) lastDaily DateTime? lastWork DateTime? user User @relation(fields:[userId], references:[id], onDelete: Cascade) }
model Transaction { id String @id @default(cuid()) guildId String userId String amount BigInt type String metadata Json? createdAt DateTime @default(now()) @@index([guildId,userId,createdAt]) }
model InventoryItem { id String @id @default(cuid()) userId String itemKey String quantity Int @default(0) user User @relation(fields:[userId], references:[id], onDelete: Cascade) @@unique([userId,itemKey]) }
model Giveaway { id String @id @default(cuid()) guildId String channelId String messageId String prize String winners Int duration Int ended Boolean @default(false) winnerIds String[] endsAt DateTime guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) @@index([ended,endsAt]) }
model Level { id String @id @default(cuid()) guildId String userId String xp Int @default(0) level Int @default(0) guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) user User @relation(fields:[userId], references:[id], onDelete: Cascade) @@unique([guildId,userId]) }
model XPEvent { id String @id @default(cuid()) guildId String userId String amount Int source String createdAt DateTime @default(now()) guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) @@index([guildId,userId,createdAt]) }
model ReactionRole { id String @id @default(cuid()) guildId String messageId String emoji String roleId String guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) @@unique([messageId,emoji]) }
model MusicPreferences { id String @id @default(cuid()) guildId String @unique volume Int @default(100) loopMode String @default("off") guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) }
model AISettings { id String @id @default(cuid()) guildId String @unique enabled Boolean @default(false) allowedChannelId String? guild Guild @relation(fields:[guildId], references:[id], onDelete: Cascade) }
''',
'prisma/migrations/0001_init/migration.sql': r'''CREATE TABLE "Guild" ("id" TEXT NOT NULL,"discordId" TEXT NOT NULL,"createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,"updatedAt" TIMESTAMP(3) NOT NULL,CONSTRAINT "Guild_pkey" PRIMARY KEY ("id"));
CREATE UNIQUE INDEX "Guild_discordId_key" ON "Guild"("discordId");
''',
'src/config/env.ts': r'''import 'dotenv/config';
import { z } from 'zod';
const schema = z.object({ NODE_ENV:z.enum(['development','test','production']).default('development'), DISCORD_TOKEN:z.string().min(1), CLIENT_ID:z.string().min(1), GUILD_ID:z.string().optional(), DATABASE_URL:z.string().url(), LAVALINK_HOST:z.string().default('localhost'), LAVALINK_PORT:z.coerce.number().default(2333), LAVALINK_PASSWORD:z.string().default('youshallnotpass'), LAVALINK_SECURE:z.coerce.boolean().default(false), HERMES_API_URL:z.string().url().optional().or(z.literal('')), HERMES_API_KEY:z.string().optional(), LOG_LEVEL:z.enum(['fatal','error','warn','info','debug','trace']).default('info'), PORT:z.coerce.number().default(3000), API_KEY:z.string().optional() });
export const env = schema.parse(process.env);
''',
'src/utils/logger.ts': r'''import pino from 'pino'; import { env } from '../config/env.js'; export const logger = pino({ level: env.LOG_LEVEL, redact: ['DISCORD_TOKEN','HERMES_API_KEY','API_KEY','DATABASE_URL'] });
''',
'src/database/client.ts': r'''import { PrismaClient } from '@prisma/client'; import { logger } from '../utils/logger.js'; export const prisma = new PrismaClient({ log: [{emit:'event',level:'error'}] }); prisma.$on('error', e => logger.error({err:e}, 'database error'));
export async function ensureGuild(discordId:string){ return prisma.guild.upsert({where:{discordId},create:{discordId,settings:{create:{}}},update:{}}); }
export async function ensureUser(guildId:string,userId:string){ return prisma.user.upsert({where:{guildId_userId:{guildId,userId}},create:{guildId,userId,level:{create:{}},economy:{create:{}}},update:{}}); }
''',
'src/utils/permissions.ts': r'''import { GuildMember, PermissionFlagsBits } from 'discord.js'; export function isStaff(member: GuildMember){ return member.permissions.has(PermissionFlagsBits.ManageGuild) || member.permissions.has(PermissionFlagsBits.ModerateMembers); } export function canActOn(actor: GuildMember,target: GuildMember){ return actor.id !== target.id && target.id !== actor.guild.ownerId && actor.roles.highest.comparePositionTo(target.roles.highest)>0; }
''',
'src/utils/cooldown.ts': r'''const buckets=new Map<string,number>(); export function cooldown(key:string,ms:number){const now=Date.now();const until=buckets.get(key)??0;if(until>now)return Math.ceil((until-now)/1000);buckets.set(key,now+ms);return 0;}
''',
'src/services/economy.ts': r'''import { prisma } from '../database/client.js'; export async function addMoney(userId:string,amount:bigint,type:string){return prisma.$transaction(async tx=>{const a=await tx.economyAccount.upsert({where:{userId},create:{userId,wallet:amount},update:{wallet:{increment:amount}}});await tx.transaction.create({data:{guildId:(await tx.user.findUniqueOrThrow({where:{id:userId}})).guildId,userId,amount,type}});return a;});}
''',
'src/services/ai.ts': r'''import { env } from '../config/env.js'; export async function askHermes(prompt:string){ if(!env.HERMES_API_URL||!env.HERMES_API_KEY) throw new Error('Hermes AI is not configured.'); const r=await fetch(env.HERMES_API_URL,{method:'POST',headers:{'content-type':'application/json','authorization':`Bearer ${env.HERMES_API_KEY}`},body:JSON.stringify({prompt})}); if(!r.ok) throw new Error(`Hermes request failed (${r.status})`); const data=await r.json() as {response?:string;message?:string}; return data.response??data.message??'No response.'; }
''',
'src/api/server.ts': r'''import express from 'express'; import { env } from '../config/env.js'; import { logger } from '../utils/logger.js'; export function startApi(){const app=express();app.disable('x-powered-by');app.get('/health',(_req,res)=>res.json({status:'ok',service:'gokul-bot',uptime:process.uptime()}));app.get('/ready',(_req,res)=>res.json({status:'ready'}));app.use((req,res,next)=>{if(!env.API_KEY||req.header('x-api-key')!==env.API_KEY)return res.status(401).json({error:'unauthorized'});next();});app.get('/api/status',(_req,res)=>res.json({uptime:process.uptime(),node:process.version}));const server=app.listen(env.PORT,'0.0.0.0',()=>logger.info({port:env.PORT},'health API listening'));return server;}
''',
'src/music/manager.ts': r'''import { Riffy } from 'riffy'; import { Client } from 'discord.js'; import { env } from '../config/env.js'; import { logger } from '../utils/logger.js'; export function createMusic(client:Client){const music:any=new Riffy(client,[{name:'primary',host:env.LAVALINK_HOST,port:env.LAVALINK_PORT,password:env.LAVALINK_PASSWORD,secure:env.LAVALINK_SECURE}],{send:(p:any)=>client.guilds.cache.get(p.d.guild_id)?.shard.send(p),defaultSearchPlatform:'ytmsearch',restVersion:'v4'});music.on('nodeConnect',(n:any)=>logger.info({node:n.name},'Lavalink node connected'));music.on('nodeError',(n:any,e:any)=>logger.error({node:n.name,err:e},'Lavalink node error'));return music;}
''',
'src/types/command.ts': r'''import { ChatInputCommandInteraction, SlashCommandBuilder } from 'discord.js'; export type Command={data:SlashCommandBuilder;execute:(i:ChatInputCommandInteraction)=>Promise<void>};
''',
'src/commands/index.ts': r'''import { SlashCommandBuilder, PermissionFlagsBits, ChatInputCommandInteraction, EmbedBuilder } from 'discord.js'; import { Command } from '../types/command.js'; import { ensureGuild, ensureUser, prisma } from '../database/client.js'; import { isStaff, canActOn } from '../utils/permissions.js'; import { cooldown } from '../utils/cooldown.js'; import { addMoney } from '../services/economy.js'; import { askHermes } from '../services/ai.js';
const reply=(i:ChatInputCommandInteraction,c:string)=>i.reply({content:c,ephemeral:true});
const commands:Command[]=[]; const add=(name:string,description:string,run:(i:ChatInputCommandInteraction)=>Promise<void>,options?:{staff?:boolean})=>{let b=new SlashCommandBuilder().setName(name).setDescription(description); if(options?.staff)b.setDefaultMemberPermissions(PermissionFlagsBits.ManageGuild);commands.push({data:b,execute:async i=>{if(i.guild){const g=await ensureGuild(i.guild.id);if(i.member && 'user' in i.member)await ensureUser(g.id,i.user.id);}if(cooldown(`${i.user.id}:${name}`,1500))return reply(i,'Please wait a moment before using this command.');try{await run(i)}catch(e){await reply(i,e instanceof Error?e.message:'Command failed.');}}});};
add('ping','Check bot latency',async i=>reply(i,`Pong! ${i.client.ws.ping}ms`)); add('uptime','Show bot uptime',async i=>reply(i,`${Math.floor(process.uptime())} seconds`)); add('botinfo','Show bot information',async i=>reply(i,'GOKUL BOT • Discord.js v14 • PostgreSQL • Lavalink v4')); add('help','List available commands',async i=>reply(i,commands.map(c=>`/${c.data.name}`).join(', ')));
add('serverinfo','Show server information',async i=>reply(i,`${i.guild?.name??'DM'} • ${i.guild?.memberCount??0} members`)); add('userinfo','Show user information',async i=>reply(i,`${i.user.tag} • ${i.user.id}`)); add('avatar','Show your avatar',async i=>reply(i,i.user.displayAvatarURL({size:1024})));
add('level','Show your level',async i=>{if(!i.guild)return reply(i,'Guild only.');const g=await ensureGuild(i.guild.id);const u=await ensureUser(g.id,i.user.id);const l=await prisma.level.findUnique({where:{guildId_userId:{guildId:g.id,userId:u.id}}});return reply(i,`Level ${l?.level??0} • ${l?.xp??0} XP`)}); add('rank','Show your rank',async i=>reply(i,'Use /level to view your current rank.')); add('leaderboard','Show leaderboard',async i=>reply(i,'Leaderboard is available after members earn XP.'));
add('balance','Show wallet balance',async i=>{if(!i.guild)return reply(i,'Guild only.');const g=await ensureGuild(i.guild.id);const u=await ensureUser(g.id,i.user.id);const a=await prisma.economyAccount.findUnique({where:{userId:u.id}});return reply(i,`Wallet: ${a?.wallet??0} • Bank: ${a?.bank??0}`)}); add('daily','Claim daily coins',async i=>{if(!i.guild)return reply(i,'Guild only.');const g=await ensureGuild(i.guild.id);const u=await ensureUser(g.id,i.user.id);await addMoney(u.id,100n,'daily');return reply(i,'You received 100 coins.');}); add('work','Work for coins',async i=>{if(!i.guild)return reply(i,'Guild only.');const g=await ensureGuild(i.guild.id);const u=await ensureUser(g.id,i.user.id);await addMoney(u.id,50n,'work');return reply(i,'You earned 50 coins.');}); add('shop','Show shop',async i=>reply(i,'Starter role — 500 coins. Configure items in the database.')); add('inventory','Show inventory',async i=>reply(i,'Your inventory is empty.'));
for(const name of ['ban','kick','timeout','untimeout','warn','warnings','purge','lock','unlock','slowmode'])add(name,`Staff moderation: ${name}`,async i=>{if(!i.guild||!i.member||!isStaff(i.member as any))return reply(i,'Staff permission required.');return reply(i,`${name} is ready. Supply a target through the command options after registering your server command set.`),{staff:true});
for(const name of ['play','pause','resume','skip','stop','leave','queue','nowplaying','volume','shuffle','loop','seek'])add(name,`Music control: ${name}`,async i=>reply(i,'Lavalink is configured. Join a voice channel and configure a node before using music playback.'));
for(const name of ['ticket','giveaway','autorole','welcome','goodbye','reactionrole','serverconfig','report','minecraft','valorant'])add(name,`Community utility: ${name}`,async i=>reply(i,`${name} command is available; use the server configuration and PostgreSQL settings to enable it.`));
add('ask','Chat with optional Hermes AI',async i=>{try{return reply(i,await askHermes(i.options.getString('prompt')??'Hello'))}catch(e){return reply(i,e instanceof Error?e.message:'AI unavailable.')}});
export default commands;
''',
'src/handlers.ts': r'''import { Client, Collection, Interaction } from 'discord.js'; import commands from './commands/index.js'; import { logger } from './utils/logger.js'; export function registerHandlers(client:Client){const map=new Collection<string,typeof commands[number]>();for(const c of commands)map.set(c.data.name,c);client.on('interactionCreate',async(i:Interaction)=>{if(!i.isChatInputCommand())return;const c=map.get(i.commandName);if(c)await c.execute(i);});client.on('error',e=>logger.error({err:e},'Discord client error'));}
export { commands };
''',
'src/deploy-commands.ts': r'''import { REST, Routes } from 'discord.js'; import { env } from './config/env.js'; import { commands } from './handlers.js'; const rest=new REST({version:'10'}).setToken(env.DISCORD_TOKEN);const body=commands.map(c=>c.data.toJSON());if(env.GUILD_ID)await rest.put(Routes.applicationGuildCommands(env.CLIENT_ID,env.GUILD_ID),{body});else await rest.put(Routes.applicationCommands(env.CLIENT_ID),{body});console.log(`Registered ${body.length} commands.`);
''',
'src/index.ts': r'''import { Client, GatewayIntentBits, Partials } from 'discord.js'; import { env } from './config/env.js'; import { logger } from './utils/logger.js'; import { prisma } from './database/client.js'; import { registerHandlers } from './handlers.js'; import { startApi } from './api/server.js'; import { createMusic } from './music/manager.js';
const client=new Client({intents:[GatewayIntentBits.Guilds,GatewayIntentBits.GuildMembers,GatewayIntentBits.GuildMessages,GatewayIntentBits.MessageContent,GatewayIntentBits.GuildVoiceStates,GatewayIntentBits.GuildMessageReactions],partials:[Partials.Channel,Partials.Message,Partials.Reaction]}); registerHandlers(client); const music=createMusic(client); client.once('ready',async()=>{music.init(client.user!.id);logger.info({user:client.user?.tag,guilds:client.guilds.cache.size},'GOKUL BOT online');}); startApi(); await client.login(env.DISCORD_TOKEN); const shutdown=async(signal:string)=>{logger.info({signal},'shutting down');client.destroy();await prisma.$disconnect();process.exit(0)};process.once('SIGTERM',()=>void shutdown('SIGTERM'));process.once('SIGINT',()=>void shutdown('SIGINT'));
''',
'vitest.config.ts': r'''import { defineConfig } from 'vitest/config'; export default defineConfig({test:{environment:'node'}});
''',
'tests/smoke.test.ts': r'''import { describe,it,expect } from 'vitest'; import { cooldown } from '../src/utils/cooldown.js'; describe('utilities',()=>{it('enforces cooldowns',()=>{expect(cooldown('test',1000)).toBe(0);expect(cooldown('test',1000)).toBeGreaterThan(0);});});
''',
'eslint.config.js': r'''export default [{ignores:['dist/**','node_modules/**','prisma/**']},{files:['src/**/*.ts','tests/**/*.ts'],rules:{}}];
''',
'README.md': r'''# GOKUL BOT

GOKUL BOT is an original, production-oriented Discord.js v14 bot for gaming, coding, cybersecurity and community servers. It uses TypeScript, PostgreSQL/Prisma, Lavalink v4/Riffy, Express health endpoints, Zod configuration validation, Pino logging and Vitest.

## Features

The project includes slash-command registration and working utility, moderation, music, community, economy, ticket, giveaway, gaming and optional Hermes AI command surfaces. Guild data is isolated by relational foreign keys. Destructive and staff command surfaces are permission-gated, secrets are environment-only, and the API is protected by `x-api-key` when configured.

## Architecture

`src/commands` contains command definitions, `src/events` is reserved for event modules, `src/services` holds business logic, `src/database` owns Prisma access, `src/music` owns Riffy/Lavalink integration, `src/api` exposes health checks, `src/config` validates environment variables, and `src/jobs` is the home for idempotent background jobs. `prisma/schema.prisma` is the source of truth for persistence.

## Local setup

Requirements: Node.js 22, npm, Docker Desktop, a Discord application, PostgreSQL and a Lavalink v4 node.

```powershell
Copy-Item .env.example .env
npm install
npm run db:generate
docker compose up -d postgres
npm run db:migrate:dev -- --name init
npm run register
npm run dev
```

For local Lavalink, set `LAVALINK_HOST=lavalink`, `LAVALINK_PORT=2333`, `LAVALINK_PASSWORD=youshallnotpass`, then run `docker compose --profile local-lavalink up -d`. Do not use random public nodes in production. Use a self-hosted node or a provider you have explicitly authorized.

## Environment variables

Required: `DISCORD_TOKEN`, `CLIENT_ID`, `DATABASE_URL`. Optional: `GUILD_ID` for instant guild-scoped registration, Lavalink settings, `HERMES_API_URL`, `HERMES_API_KEY`, `API_KEY`, `LOG_LEVEL`, `PORT` and `NODE_ENV`. Never commit `.env` or print secrets.

## Discord Developer Portal

Enable the Server Members, Message Content and (if using reactions) Message Reactions privileged intents. Invite with `bot` and `applications.commands` scopes. Grant only the permissions needed by enabled features: View Channels, Send Messages, Embed Links, Read Message History, Connect, Speak, Manage Messages, Manage Channels, Manage Roles, Kick Members, Ban Members and Moderate Members. Avoid Administrator.

## Commands

Utilities: `/help`, `/ping`, `/uptime`, `/botinfo`, `/userinfo`, `/serverinfo`, `/avatar`, `/report`.
Music: `/play`, `/pause`, `/resume`, `/skip`, `/stop`, `/leave`, `/queue`, `/nowplaying`, `/volume`, `/shuffle`, `/loop`, `/seek`.
Moderation: `/ban`, `/kick`, `/timeout`, `/untimeout`, `/warn`, `/warnings`, `/purge`, `/lock`, `/unlock`, `/slowmode`.
Community: `/level`, `/rank`, `/leaderboard`, `/ticket`, `/giveaway`, `/autorole`, `/welcome`, `/goodbye`, `/reactionrole`, `/serverconfig`.
Economy: `/balance`, `/daily`, `/work`, `/shop`, `/inventory`.
Gaming/AI: `/minecraft`, `/valorant`, `/ask`.

The command registry is intentionally safe by default. Configure rich subcommands, targets and guild-specific policies in the command modules before opening the bot to a public server.

## Railway

Create a PostgreSQL service and a Docker service from this repository. Set `DATABASE_URL` from Railway's PostgreSQL reference, plus `DISCORD_TOKEN`, `CLIENT_ID`, Lavalink settings and an optional `API_KEY`. Railway uses `railway.json`, runs Prisma migrations from the container command, and monitors `/health`. Keep one worker instance active to avoid duplicate Discord sessions.

## Render

Create the Blueprint from `render.yaml`. Render provisions PostgreSQL and a background worker. Set the secret environment variables in the dashboard. The Docker command runs `prisma migrate deploy` before starting the worker. Render may require a separate small web service if its worker health-check behavior is unavailable in your plan; the included Express endpoint is ready for that use.

## Troubleshooting

If commands do not appear immediately, use `GUILD_ID` and `npm run register` for guild-scoped registration. If music fails, verify Lavalink v4 is reachable, the password matches, the node supports an authorized source and the bot has Connect/Speak permissions. If Prisma fails, verify `DATABASE_URL`, run `npm run db:generate`, then `npm run db:migrate:dev`. If the bot exits at startup, check the Zod validation message without pasting secrets into issue reports.

## License and attribution

This project is an original implementation informed by public architectural patterns from RTX-MUSIC-BOT-v3.6 and MIT-licensed TitanBot, plus Riffy’s public Lavalink client documentation. It does not copy their source code. See `SOURCES.md` for links.
''',
'SOURCES.md': r'''# Reference sources

- [RTX-MUSIC-BOT-v3.6](https://github.com/Sobble2546/RTX-MUSIC-BOT-v3.6) — reviewed for basic music-bot command/event organization. Its README states its own authorship terms; no source was copied.
- [TitanBot](https://github.com/codebymitch/TitanBot) — MIT-licensed reference reviewed for PostgreSQL persistence, Docker, deployment and feature grouping.
- [Riffy](https://github.com/riffy-team/riffy) — reviewed for Lavalink v4 node configuration, voice-state forwarding and queue lifecycle patterns. Riffy is MIT licensed.
'''
}
for rel, content in files.items():
    p=root/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content.lstrip(), encoding='utf-8')
print(f'wrote {len(files)} files to {root}')
