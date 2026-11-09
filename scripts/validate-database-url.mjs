import { requireDatabaseUrl } from '../dist/config/database-url.js';

try {
  requireDatabaseUrl();
} catch (error) {
  console.error(error instanceof Error ? error.message : 'DATABASE_URL is invalid.');
  process.exitCode = 1;
}
