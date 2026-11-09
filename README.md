# GOKUL BOT

GOKUL BOT is a Discord.js v14 bot built with Node.js 22+, TypeScript, PostgreSQL, Prisma, Express, Pino, Zod, and Riffy for Lavalink v4 connectivity.

## Project layout

- `src/index.ts` starts the Discord client, Lavalink client, and HTTP health API.
- `src/commands/` contains registered slash commands.
- `src/handlers.ts` handles interactions, message XP, and Discord client errors.
- `src/config/` validates environment configuration.
- `src/database/` contains Prisma access and guild/user initialization.
- `src/services/` contains economy operations.
- `src/music/` configures the Riffy Lavalink client.
- `src/api/` serves health, readiness, and API status endpoints.
- `prisma/schema.prisma` defines the PostgreSQL models.
- `prisma/migrations/` contains production migrations.
- `tests/` contains Vitest tests.

## Implemented commands

- `/ping`, `/uptime`, `/botinfo`, `/help`
- `/serverinfo`, `/userinfo`, `/avatar`
- `/level`, `/leaderboard`
- `/balance`, `/daily`, `/work`

Message XP is awarded with a per-user cooldown. Daily and work rewards use atomic database updates to prevent concurrent repeat claims. Commands that require a server are guild-only. The database schema also retains models for moderation, tickets, giveaways, reaction roles, and music preferences; those models do not imply that corresponding commands are currently implemented.

## Local development

Requirements: Node.js 22.12+, npm, PostgreSQL, and a Lavalink v4 node.

```powershell
Copy-Item .env.example .env
npm ci
npm run db:generate
npm run db:migrate
npm run register
npm run dev
```

Set real credentials only in the ignored `.env` file or your deployment secret store. `.env.example` contains placeholders.

Required variables:

- `DISCORD_TOKEN`: Discord bot token.
- `CLIENT_ID`: Discord application ID.
- `DATABASE_URL`: PostgreSQL connection URL.
- `LAVALINK_PASSWORD`: password configured on the Lavalink server.

Optional variables:

- `GUILD_ID`: register slash commands to one server during development.
- `LAVALINK_HOST` (default `localhost`), `LAVALINK_PORT` (default `2333`), and `LAVALINK_SECURE` (default `false`).
- `PORT` (default `3000`), `NODE_ENV` (default `development`), `LOG_LEVEL` (default `info`), and `API_KEY`.

The Discord application needs the `bot` and `applications.commands` scopes. Message XP needs the Guild Messages intent; message content and the privileged Message Content intent are not used.

## Build and tests

```powershell
npm run db:generate
npx prisma validate
npx tsc --noEmit
npm run build
npm test
```

## Railway deployment

Deploy this repository as a Docker service and add a PostgreSQL service to the same Railway project/environment. The included `railway.json` selects the Dockerfile and configures a single replica. The container runs `prisma migrate deploy` before `npm start`; it does not run development migrations.

Set these variables on the bot service:

| Variable | Value |
| --- | --- |
| `DISCORD_TOKEN` | Secret from the Discord Developer Portal |
| `CLIENT_ID` | Discord application ID |
| `DATABASE_URL` | Railway PostgreSQL connection string/reference |
| `LAVALINK_HOST` | `lavalink.railway.internal` when Lavalink is in the same Railway project and environment |
| `LAVALINK_PORT` | `2333` |
| `LAVALINK_PASSWORD` | Same secret as `LAVALINK_SERVER_PASSWORD` on Lavalink |
| `LAVALINK_SECURE` | `false` for Railway private networking |
| `NODE_ENV` | `production` |

Deploy Lavalink as a separate service from its own repository. Keep port 2333 private and do not create a public TCP proxy. The health endpoint is `/health`; `/ready` also checks the PostgreSQL connection. Use one bot replica to avoid multiple Discord sessions.

## HTTP endpoints

- `GET /health`: process health check.
- `GET /ready`: database readiness check.
- `GET /api/status`: requires the `x-api-key` header and a configured `API_KEY`.
