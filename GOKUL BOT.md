# GOKUL BOT

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
