# PostgreSQL Setup Guide

This guide explains how to set up and use PostgreSQL with your FastAPI application.

## Local Development Setup

### 1. Install PostgreSQL

#### Windows
1. Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. During installation, set a password for the `postgres` user
3. Remember the port (default is 5432)

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create a Database

#### Using pgAdmin (GUI)
1. Open pgAdmin (installed with PostgreSQL)
2. Connect to your PostgreSQL server
3. Right-click on "Databases" and select "Create" > "Database"
4. Name your database "zetacrush"

#### Using Command Line
```bash
# Connect as postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE zetacrush;

# Create application user (optional)
CREATE USER zetacrush_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE zetacrush TO zetacrush_user;

# Exit
\q
```

### 3. Update Your .env File

Make sure your `.env` file has the correct PostgreSQL connection string:

```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/zetacrush
```

Replace `your_password` with the password you set for the `postgres` user.

### 4. Run the Setup Script

```bash
python scripts/setup_postgres.py
```

To import data from an existing SQLite database:

```bash
python scripts/setup_postgres.py --import-sqlite --sqlite-path app.db
```

## Production Setup

For production, you'll want to use a managed PostgreSQL service:

### Supabase (Recommended)

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Project Settings > Database > Connection String > URI
4. Copy the connection string and update your environment variables

### Railway

1. Sign up at [railway.app](https://railway.app)
2. Create a new PostgreSQL database
3. Connect to your GitHub repository
4. Set environment variables for your project

### Neon

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string and update your environment variables

## Environment Variables

Set these in your deployment platform (Vercel, Railway, etc.):

```
DATABASE_URL=postgresql://username:password@hostname:port/database
```

## Database Migration

When making model changes, you'll need to migrate your database:

1. Create a migration script in the `scripts` directory
2. Update the models
3. Run the migration script to alter tables in the database

## Backup and Restore

### Backup

```bash
pg_dump -U postgres -d zetacrush -f backup.sql
```

### Restore

```bash
psql -U postgres -d zetacrush -f backup.sql
```

## Connection Pooling

For high-traffic applications, consider using a connection pooling service like PgBouncer or Supabase's built-in connection pooling.
