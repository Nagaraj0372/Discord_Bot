#!/bin/sh
set -eu

node ./scripts/validate-database-url.mjs
npm run db:migrate
exec npm start
