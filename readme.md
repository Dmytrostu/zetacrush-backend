# Book Summarizing Application Backend

> **[August 2025 Update]** Added Google Drive integration for persistent file storage in serverless environments, improved Vercel deployment configuration, and fixed file handling issues in serverless contexts.

## Overview
This backend application is built with FastAPI and provides an automated solution for summarizing the content of a book. It analyzes uploaded files (PDF, TXT, DOC) and extracts:

- **Main Characters/Places/Things:**
  - Identifies and lists the most important names, places, or objects by analyzing capitalized words/phrases that are not common dictionary words.
- **Synopsis:**
  - Searches for and displays key passages containing impactful or dramatic keywords to provide a rough synopsis of the book.
- **Easter Egg:**
  - Extracts a random, interesting passage containing the word "first" and one of the main characters/places/things.

## Features
- **API Endpoint:** Upload book files (PDF, TXT, DOC) and receive summarized data in JSON format.
- **Authentication:** Secure access to the API using JWT authentication.
- **Subscription:** Monthly payment system for users to access the service, with a free 3-day trial for registered accounts.
- **Vercel Deployment:** Optimized for serverless deployment on Vercel with proper file handling.
- **Google Drive Integration:** Optional support for Google Drive file storage in serverless environments.

## Installation
1. Clone the repository or copy the backend folder to your machine.
2. Install Python 3.12 or later.
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. (Optional) Set environment variables in `.env` (e.g., `SECRET_KEY`).

## Usage
### Start the FastAPI Server
Run the following command from the project root:
```sh
uvicorn main:app --reload
```

### API Endpoints
#### 1. Register a New User
- **POST** `/api/v1/users/register`
- Request Body:
  ```json
  {
    "email": "your_email@example.com",
    "name": "Your Name",
    "password": "your_password"
  }
  ```
- Response: User object with trial subscription

#### 2. Login and Get JWT Token
- **POST** `/api/v1/users/login`
- Request Body:
  ```json
  {
    "email": "your_email@example.com",
    "password": "your_password"
  }
  ```
- Response: `{ "access_token": "...", "token_type": "bearer" }`

#### 3. Get Current User Profile
- **GET** `/api/v1/users/me`
- Header: `Authorization: Bearer <JWT_TOKEN>`
- Response: 
  ```json
  {
    "id": "1",
    "email": "your_email@example.com",
    "name": "Your Name",
    "created_at": "2023-08-29T12:00:00.000Z",
    "trial_active": true,
    "trial_expires_at": "2023-09-01T12:00:00.000Z",
    "subscription_active": false,
    "subscription_plan": null,
    "subscription_expires_at": null,
    "upload_count": 0,
    "max_uploads": 5
  }
  ```

#### 4. Subscribe to Monthly Plan
- **POST** `/api/v1/subscriptions/subscribe`
- Header: `Authorization: Bearer <JWT_TOKEN>`
- Request Body:
  ```json
  {
    "plan": "basic"
  }
  ```
- Response: 
  ```json
  {
    "message": "Basic subscription activated for 30 days.",
    "plan": "basic",
    "active": true,
    "expires_at": "2023-09-28T12:00:00.000Z"
  }
  ```

#### 5. Upload Book File for Summarization
- **POST** `/api/v1/upload`
- Header: `Authorization: Bearer <JWT_TOKEN>`
- Form Data: `file` (PDF, TXT, DOC)
- Response: 
  ```json
  {
    "main_characters": ["Elizabeth", "Darcy", "Jane"],
    "synopsis": ["Key passage 1", "Key passage 2"],
    "easter_egg": "Random interesting passage with 'first'",
    "upload_info": {
      "filename": "book.pdf",
      "upload_count": 1,
      "max_uploads": 5,
      "remaining_uploads": 4
    }
  }
  ```

### API Documentation
Interactive API docs are available at:
- [http://zetacrush-backend.vercel.app/docs](http://zetacrush-backend.vercel.app/docs)

## Requirements
- Python 3.12+
- FastAPI
- Uvicorn
- PyJWT
- passlib
- PyPDF2 (for PDF processing)
- python-docx (for DOCX processing, optional)

### Google Drive Integration Requirements
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- Service Account with Google Drive API access
- (See `requirements.txt` for full list)

## Environment Variables

The application uses the following environment variables, which can be set in a `.env` file for local development or through platform environment settings for deployment:

### Core Settings
| Variable | Description | Default |
|----------|-------------|---------|
| ENVIRONMENT | Environment type (development/production) | development |
| DEBUG | Enable debug mode | true in development |
| API_HOST | Host for the API server | 0.0.0.0 |
| API_PORT | Port for the API server | 8000 |
| IS_SERVERLESS | Flag for serverless environment detection | false (auto-detected) |
| IS_VERCEL | Flag for Vercel environment detection | false (auto-detected) |

### Security Settings
| Variable | Description | Default |
|----------|-------------|---------|
| JWT_SECRET_KEY | Secret key for JWT token generation | your_secret_key |
| JWT_ALGORITHM | Algorithm for JWT token | HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration in minutes | 30 |

### Database Settings
| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | Database connection string | postgresql://... |

### Upload Settings
| Variable | Description | Default |
|----------|-------------|---------|
| UPLOAD_FOLDER | Directory for uploaded files | ./uploads (or /tmp/uploads in serverless) |
| MAX_FILE_SIZE | Maximum file size in bytes | 10485760 (10MB) |

### Rate Limiting
| Variable | Description | Default |
|----------|-------------|---------|
| ENABLE_RATE_LIMITING | Enable rate limiting | false |
| RATE_LIMIT_WINDOW_SECONDS | Time window for rate limits | 60 |
| RATE_LIMIT_MAX_REQUESTS | Maximum requests in window | 30 |

### Google Drive Integration
| Variable | Description | Default |
|----------|-------------|---------|
| USE_CLOUD_STORAGE | Enable Google Drive storage | false |
| GOOGLE_DRIVE_FOLDER_ID | ID of Google Drive folder | (required if enabled) |
| GOOGLE_CREDENTIALS_FILE | Path to service account credentials | credentials.json |

## Purpose
This backend is designed for quick, automated summarization and character extraction from literary texts, making it useful for book analysis, research, or entertainment purposes. It supports secure access and subscription management for scalable deployment.

## Security Considerations

### Sensitive Data Protection
- **Environment Variables**: Never commit `.env` files to version control
- **Git Protection**: The project includes `.gitignore` settings to prevent accidental commits of:
  - `.env` files containing secrets
  - `__pycache__` directories and `.pyc` files
  - Credentials and authentication files

### Credential Management
- Use environment variables for all secrets and credentials
- For Vercel deployment, store sensitive information in Vercel's environment variables
- Rotate JWT secrets and database credentials periodically
- If credentials were accidentally committed to git history, consider using BFG Repo-Cleaner

### File Upload Security
- File uploads are validated for type and size
- Files are stored securely with randomized names
- In serverless environments, files are stored in isolated `/tmp` directory
- Google Drive integration provides additional isolation of uploaded content

## CORS Configuration
The API includes Cross-Origin Resource Sharing (CORS) middleware to allow frontend applications hosted on different domains to communicate with the backend.

### Default Configuration
- By default, the following origins are allowed:
  - `http://localhost:3000` (React default port)
  - `http://zetacrush-backend.vercel.app` (FastAPI server)
  - `http://127.0.0.1:3000`
  - `http://127.0.0.1:8000`

### Customizing CORS
- Modify allowed origins in `.env` file or directly in `core/config.py`
- Additional origins should be added before deployment to production

### Testing CORS
1. Access the CORS test page at `/static/cors_test.html`
2. Test API connectivity from different origins
3. Use the `/api/v1/cors-test` endpoint to verify CORS headers
4. View CORS configuration at `/api/v1/cors-config`

## Deployment Options

### Vercel Deployment

The application is optimized for deployment on Vercel's serverless platform with specialized handling for file uploads and storage limitations:

1. **Environment Setup**:
   - Add environment variables through the Vercel dashboard or CLI
   - Sensitive information (database credentials, JWT secret) should be set as environment variables
   - Non-sensitive configuration is included in `vercel.json`
   - Environment variables automatically configure optimal settings for serverless operation

2. **File Storage Solutions**:
   - In serverless environments, files are temporarily stored in `/tmp` directory
   - The application automatically detects Vercel environment and adjusts storage paths
   - **Important:** Files in `/tmp` are ephemeral and will be deleted when the function completes
   - For persistent storage, enable Google Drive integration (highly recommended)
   - The application uses a specialized upload service (`upload_service_vercel.py`) in Vercel environments

3. **Deployment Steps**:
   ```sh
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy to Vercel
   vercel
   
   # For production deployment
   vercel --prod
   ```

4. **Environment Configuration**:
   - Key settings in `vercel.json`:
   ```json
   {
     "env": {
       "ENVIRONMENT": "production",
       "DEBUG": "false",
       "UPLOAD_FOLDER": "/tmp/uploads",
       "IS_SERVERLESS": "true"
     }
   }
   ```

5. **Environment Health Check**:
   - After deployment, access `/api/v1/health/env` to verify environment settings
   - This endpoint tests the filesystem, environment variables, and configuration
   - Check for "Vercel environment detected" in the health check response
   - Verify file system write access is working in the `/tmp` directory

### Google Drive Integration

For persistent file storage in serverless environments, the application integrates with Google Drive:

1. **Why Use Google Drive Storage**:
   - Provides permanent storage for uploaded files in serverless environments
   - Solves the `/tmp` directory limitations in Vercel and other serverless platforms
   - Enables sharing or direct access to files via Google Drive links
   - No local server storage management required

2. **Setup Instructions**:
   - See comprehensive instructions in `docs/google_drive_setup.md`
   - Create a Google Cloud project and enable the Google Drive API
   - Create a service account and download credentials as JSON
   - Create a folder in Google Drive and share it with the service account email
   - Upload your `credentials.json` file to Vercel or keep it in your project root locally

3. **Configuration**:
   Add to your `.env` file or Vercel environment variables:
   ```
   USE_CLOUD_STORAGE=true
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
   GOOGLE_CREDENTIALS_FILE=credentials.json
   ```

4. **Testing Google Drive Setup**:
   ```sh
   # Run the setup validation script
   python scripts/setup_google_drive.py
   
   # If successful, you'll see confirmation and a test file in your Google Drive folder
   ```

5. **Vercel Deployment with Google Drive**:
   - For Vercel, encode the entire `credentials.json` content as a single line and set it as `GOOGLE_CREDENTIALS_JSON` environment variable
   - Example:
   ```
   GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}
   ```
   - The application will automatically create a credentials file in the `/tmp` directory when running in Vercel

## File Handling Architecture

The application uses a multi-tier approach to file handling to support both traditional servers and serverless environments:

### Upload Service Selection
- **Environment-aware Service Selection**: The application automatically chooses the appropriate upload service based on the detected environment:
  - `upload_service.py`: Standard upload service for traditional server environments
  - `upload_service_vercel.py`: Specialized service optimized for Vercel's serverless environment

### Storage Strategy
The application implements a tiered storage strategy:
1. **Local Temporary Storage**:
   - Regular servers: Files stored in `./uploads` directory
   - Serverless: Files stored in `/tmp/uploads` directory (ephemeral storage)

2. **Cloud Storage** (when enabled):
   - Google Drive storage for permanent file retention
   - Files uploaded to a designated Google Drive folder
   - File access via Google Drive links or API

3. **Fallback Mechanisms**:
   - If cloud storage fails, files remain in local storage
   - Error messages include detailed diagnostics for troubleshooting

### Implementation Details
- Dynamic file path generation based on environment
- Automatic directory creation if not exists
- Stream-based file processing to handle large files efficiently
- File metadata tracking in database

## API Health Monitoring
- Basic health check endpoint at `/api/v1/health`
- Database health check at `/api/v1/health/db` 
- Environment check at `/api/v1/health/env` with detailed information about:
  - Runtime environment detection (Vercel, serverless)
  - File system access tests (critical for serverless environments)
  - Environment variable validation
  - Storage configuration status
- Basic test endpoint at `/api/v1/test-api`

## Complete API Endpoints Reference

### User Management

#### Authentication Endpoints
| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| POST | `/api/v1/users/register` | Register a new user | No |
| POST | `/api/v1/users/login` | Login and get JWT token | No |
| POST | `/api/v1/users/logout` | Logout current user | Yes |

#### User Profile Endpoints
| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/api/v1/users/me` | Get current user profile | Yes |
| PUT | `/api/v1/users/profile` | Update user profile | Yes |
| GET | `/api/v1/users/subscription` | Get user's subscription status | Yes |

### Subscription Management

#### Subscription Endpoints
| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/api/v1/subscriptions/plans` | Get available subscription plans | No |
| POST | `/api/v1/subscriptions/subscribe` | Subscribe to a plan | Yes |
| POST | `/api/v1/subscriptions/cancel` | Cancel current subscription | Yes |
| PUT | `/api/v1/subscriptions` | Update subscription plan | Yes |

### Book Management

#### Upload and Processing Endpoints
| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| POST | `/api/v1/upload` | Upload book file for summarization | Yes |

#### Book History and Details Endpoints
| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/api/v1/books/history` | Get book upload history with pagination | Yes |
| GET | `/api/v1/books/{book_id}` | Get detailed information about a book | Yes |
| GET | `/api/v1/books/{book_id}/summary` | Get summary for a specific book | Yes |
| DELETE | `/api/v1/books/{book_id}` | Delete a book from history | Yes |

### System and Diagnostics

#### Health Check and Testing Endpoints
| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/api/v1/health` | Check API health status | No |
| GET | `/api/v1/test-api` | Simple test endpoint | No |

#### CORS Testing Endpoints
| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|------------------------|
| GET | `/api/v1/cors-test` | Test CORS configuration | No |
| GET | `/api/v1/cors-config` | View current CORS settings | No |

### API Documentation
For interactive API documentation with detailed request and response schemas, visit:
- Swagger UI: [http://zetacrush-backend.vercel.app/docs](http://zetacrush-backend.vercel.app/docs)
- ReDoc: [http://zetacrush-backend.vercel.app/redoc](http://zetacrush-backend.vercel.app/redoc)
