# Book Summarizing Application Backend

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
- [http://localhost:8000/docs](http://localhost:8000/docs)

## Requirements
- Python 3.12+
- FastAPI
- Uvicorn
- PyJWT
- passlib
- (See `requirements.txt` for full list)

## Purpose
This backend is designed for quick, automated summarization and character extraction from literary texts, making it useful for book analysis, research, or entertainment purposes. It supports secure access and subscription management for scalable deployment.

## CORS Configuration
The API includes Cross-Origin Resource Sharing (CORS) middleware to allow frontend applications hosted on different domains to communicate with the backend.

### Default Configuration
- By default, the following origins are allowed:
  - `http://localhost:3000` (React default port)
  - `http://localhost:8000` (FastAPI server)
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

## API Health Monitoring
- Health check endpoint at `/api/v1/health`
- Provides system information, database status, and response times
- Basic test endpoint at `/api/v1/test-api`

## Complete API Endpoints Reference

This section provides a comprehensive list of all available API endpoints in the application.

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
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
