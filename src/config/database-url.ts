const missingDatabaseUrlMessage = [
  'DATABASE_URL is missing.',
  'Configure the Railway PostgreSQL connection reference in the bot service.',
].join('\n');
const invalidDatabaseUrlMessage =
  'DATABASE_URL must be a valid PostgreSQL connection URL.';

export function requireDatabaseUrl(
  environment: NodeJS.ProcessEnv = process.env,
): string {
  const databaseUrl = environment.DATABASE_URL?.trim();
  if (!databaseUrl) {
    throw new Error(missingDatabaseUrlMessage);
  }

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(databaseUrl);
  } catch {
    throw new Error(invalidDatabaseUrlMessage);
  }

  if (
    !['postgres:', 'postgresql:'].includes(parsedUrl.protocol) ||
    !parsedUrl.hostname
  ) {
    throw new Error(invalidDatabaseUrlMessage);
  }

  return databaseUrl;
}
