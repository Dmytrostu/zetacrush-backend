# Deploying to Vercel with Turso Database

This guide explains how to set up and deploy your FastAPI application to Vercel using Turso as the database.

## What is Turso?

[Turso](https://turso.tech/) is a SQLite-compatible edge database that works perfectly with serverless platforms like Vercel. Unlike traditional SQLite which requires file system write access, Turso provides a HTTP API that allows you to use SQLite in read-only environments.

## Why Use Turso for Vercel Deployments?

1. **Compatible with read-only filesystems**: Turso works in Vercel's read-only environment
2. **Edge optimized**: Low latency with global replication
3. **SQLite compatible**: Uses libSQL, a SQLite fork
4. **Generous free tier**: 1GB storage and 1B row reads per month for free
5. **Simple setup**: Minimal configuration changes needed

## Setup Steps

### 1. Create a Turso Account

1. Go to [Turso.tech](https://turso.tech) and sign up
2. Install the Turso CLI:
   ```powershell
   # Using PowerShell
   iwr -useb 'https://get.turso.tech/client/ps1' | iex
   ```

3. Login to Turso:
   ```powershell
   turso auth login
   ```

### 2. Create a Turso Database

1. Create a new database:
   ```powershell
   turso db create zetacrush-db
   ```

2. Get your database URL:
   ```powershell
   turso db show zetacrush-db --url
   ```

3. Create an authentication token:
   ```powershell
   turso db tokens create zetacrush-db
   ```

### 3. Update Environment Variables

Update your `.env` file with your Turso credentials:

```
# Database
DATABASE_URL=turso://[AUTH_TOKEN]@[DATABASE_NAME].turso.io/[DATABASE_NAME]
TURSO_AUTH_TOKEN=[AUTH_TOKEN]
```

For example:
```
DATABASE_URL=turso://eyJhbGciOiJFUzI1NiI@zetacrush-db.turso.io/zetacrush-db
TURSO_AUTH_TOKEN=eyJhbGciOiJFUzI1NiI...
```

### 4. Migrate Data to Turso

If you have existing data in your SQLite database that you want to migrate to Turso:

```powershell
python scripts\migrate_to_turso.py --sqlite-path app.db --turso-url https://zetacrush-db.turso.io --auth-token YOUR_AUTH_TOKEN
```

### 5. Configure Vercel Environment Variables

Add the following environment variables in your Vercel project settings:

1. `DATABASE_URL`: The Turso database URL
2. `TURSO_AUTH_TOKEN`: Your Turso authentication token

### 6. Deploy to Vercel

Deploy your application to Vercel:

```powershell
vercel --prod
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:

1. Verify your AUTH_TOKEN is correct and not expired
2. Check that your database name is correct in the URL
3. Test the connection locally before deploying

### Schema Issues

If you have schema-related errors:

1. Check if all migrations have been applied
2. Verify that your models match the schema in Turso
3. Try running `migrate_to_turso.py` again with the `--force` flag

## Development Workflow

You can use different database configurations for development and production:

- **Development**: Keep using SQLite locally for simplicity
- **Production**: Use Turso in the Vercel environment

The application will automatically detect which database to use based on the DATABASE_URL environment variable.
