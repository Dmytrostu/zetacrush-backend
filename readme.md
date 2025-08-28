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
- **POST** `/users/register`
- Request Body:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- Response: User object with trial subscription

#### 2. Login and Get JWT Token
- **POST** `/users/login`
- Request Body:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- Response: `{ "access_token": "...", "token_type": "bearer" }`

#### 3. Subscribe to Monthly Plan
- **POST** `/subscriptions/subscribe`
- Header: `Authorization: Bearer <JWT_TOKEN>`
- Response: Subscription activation message

#### 4. Upload Book File for Summarization
- **POST** `/upload`
- Header: `Authorization: Bearer <JWT_TOKEN>`
- Form Data: `file` (PDF, TXT, DOC)
- Response: JSON summary including main characters, synopsis, and easter egg

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
