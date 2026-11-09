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

Deploy this repository as a Docker service and add a Railway PostgreSQL service to the same project and environment. The included `railway.json` selects the Dockerfile and configures a single replica. At startup, the container validates `DATABASE_URL` as a PostgreSQL URL before running `prisma migrate deploy` with the runtime environment; it does not run development migrations.

### Configure the PostgreSQL service and bot reference

1. In Railway, open the `Postgres` service and confirm it is healthy and belongs to the same project and environment as `Discord Bot`.
2. In `Postgres` → **Variables**, verify its generated `DATABASE_URL` is present and nonempty. Check **Connect** for Railway's connection information and inspect the service's deployment logs if the generated value is empty.
3. If `Postgres.DATABASE_URL` is empty, the bot reference will also resolve to an empty value. Repair the source PostgreSQL service/configuration first; do not enter a guessed URL, reset the database, or delete/recreate its volume. For a self-managed PostgreSQL service, use its actual connection details and Railway's supported connection-variable setup. Any credentials placed in a URL must be URL-encoded.
4. In `Discord Bot` → **Variables**, remove an empty/stale `DATABASE_URL` and add a variable reference using Railway's picker: `DATABASE_URL` → `Postgres` → `DATABASE_URL`. The resulting reference is `${{Postgres.DATABASE_URL}}`; it is a reference, not a literal connection URL.
5. Set `NODE_ENV=production`, save the variables, then redeploy `Discord Bot`. Review deployment logs for the startup validation and migration result. Do not copy credentials or the full connection URL into logs or support messages.

### Troubleshooting database startup

- **P1012 / “nonempty URL” / empty `DATABASE_URL`:** confirm the bot's variable reference points to `Postgres.DATABASE_URL`, then confirm the source variable itself is populated. A reference cannot repair an empty source variable.
- **P1001 / “Can't reach database server”:** confirm PostgreSQL is healthy, both services are in the same Railway project/environment, and the connection uses Railway's private/internal address rather than `localhost`. `localhost` inside the bot container refers to the bot container itself.
- If Railway's PostgreSQL service does not provide a populated generated URL, use its **Connect** information and service configuration to restore the supported generated connection variables. Do not invent credentials or assemble a URL from guessed values.

Set these variables on the bot service:

| Variable | Value |
| --- | --- |
| `DISCORD_TOKEN` | Secret from the Discord Developer Portal |
| `CLIENT_ID` | Discord application ID |
| `DATABASE_URL` | Reference to the populated `Postgres.DATABASE_URL` |
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
