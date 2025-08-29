# Database Solution for Vercel Deployment

## Problem
The SQLite database cannot be used on Vercel because:
- Vercel provides a read-only filesystem in production
- SQLite requires write access to its database file
- The error `sqlite3.OperationalError: attempt to write a readonly database` occurs when trying to register users

## Solution: PostgreSQL on Supabase

### 1. Create a Supabase Account
1. Go to [Supabase](https://supabase.io) and sign up
2. Create a new project
3. Get your connection string from Database Settings

### 2. Update Database Configuration
Update your database connection to use PostgreSQL:

```python
# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - falls back to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
```

### 3. Update Database Setup
```python
# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL

# Create engine based on DATABASE_URL
engine = create_engine(
    DATABASE_URL, 
    connect_args={} if DATABASE_URL.startswith("postgresql") else {"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

### 4. Add PostgreSQL Dependencies
Add these to requirements.txt:
```
psycopg2-binary==2.9.9
```

### 5. Environment Variables
Set in Vercel dashboard:
- DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
