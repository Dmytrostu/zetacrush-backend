# Deploying to Vercel with PostgreSQL

## Problem

When deploying to Vercel, you encountered the error:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) attempt to write a readonly database
```

This occurs because Vercel provides a read-only filesystem in production, which is incompatible with SQLite's requirement to write to its database file.

## Solution: Use PostgreSQL

### Step 1: Set Up a PostgreSQL Database

Options:
- **Supabase** (recommended): Provides a free tier with PostgreSQL 
- **Neon**: PostgreSQL serverless with a generous free tier
- **ElephantSQL**: Simple PostgreSQL as a service

For Supabase:
1. Go to [Supabase](https://supabase.com/) and sign up
2. Create a new project
3. Navigate to Project Settings > Database > Connection String > URI
4. Copy the connection string

### Step 2: Configure Environment Variables

In Vercel dashboard:
1. Go to your project
2. Navigate to Settings > Environment Variables
3. Add the following variable:
   - Name: `DATABASE_URL`
   - Value: Your PostgreSQL connection string (e.g., `postgresql://postgres:password@db.example.supabase.co:5432/postgres`)

For local development, add to your `.env` file:
```
DATABASE_URL=postgresql://postgres:password@db.example.supabase.co:5432/postgres
```

### Step 3: Migrate Data

If you have existing data in SQLite that you want to migrate:

1. Set up your PostgreSQL database URL in your `.env` file
2. Run the migration script:
```
python scripts/migrate_to_postgres.py
```

### Step 4: Deploy to Vercel

```
vercel --prod
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:
1. Check if your IP is allowed in the PostgreSQL server's firewall settings
2. Verify the connection string format
3. Test the connection locally before deploying

### Migration Issues

If data migration fails:
1. Check if tables are created correctly in PostgreSQL
2. Look for data type incompatibilities between SQLite and PostgreSQL
3. Consider manual migration for complex schemas

## Development Workflow

You can still use SQLite for local development by setting different DATABASE_URL values:

- Local: `sqlite:///./app.db`
- Production: PostgreSQL connection string

The application will automatically detect which database to use based on the URL.
