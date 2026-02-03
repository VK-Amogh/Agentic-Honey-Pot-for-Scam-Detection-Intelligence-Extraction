# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

## Overview

This project implements an AI-driven honeypot system designed to detect fraudulent messages and engage scammers in autonomous, multi-turn conversations. The system aims to extract actionable intelligence (such as bank details, UPI IDs, and phishing links) while maintaining a convincing human persona.

## System Architecture

The application is built using a modern Python stack:

- **Framework**: FastAPI for high-performance, asynchronous API handling.
- **Validation**: Pydantic for strict data structure enforcement.
- **Engagement**: An autonomous agent module responsible for maintaining conversation context and persona.
- **Intelligence**: Dedicated extraction logic to parse critical entities from conversation text.
- **Reporting**: Automated callback service to report findings to the evaluation endpoint.

## Configuration

Setting up the application requires configuring environment variables. Create a `.env` file in the root directory:

```env
API_SECRET_KEY=your_secret_key_here
```

## Running the Application

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Specification

### Endpoint: Process Message
- **URL**: `/api/v1/message`
- **Method**: `POST`
- **Headers**: `x-api-key: <YOUR_KEY>`

Refer to the included documentation or the source code for detailed request/response schemas.

## License

Proprietary and Confidential.
