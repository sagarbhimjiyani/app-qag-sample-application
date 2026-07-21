# Gherkin Test Case Generation Agent

An AI-powered agent that reads Swagger/OpenAPI specifications and automatically generates comprehensive positive and negative Gherkin/Cucumber test cases.

## Features

- **Swagger/OpenAPI Support**: Accepts both JSON and YAML specifications
- **File Upload**: Web API for uploading Swagger files
- **Direct Text Input**: Send specifications as JSON in API requests
- **Comprehensive Test Coverage**: Generates positive and negative test cases
- **Gherkin Format**: Outputs valid Gherkin syntax for Cucumber/Behave frameworks
- **Google Gemini 3.5 Flash**: Uses advanced LLM for intelligent test generation

## Prerequisites

- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Service account credentials for Google Cloud
- pip/poetry for dependency management

## Installation

### 1. Set up Google Cloud

```bash
# Set up Google Cloud project
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Install Dependencies

```bash
cd ai-agent
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Google Cloud project ID and settings
```

## Usage

### Command Line

Generate test cases from a Swagger file:

```bash
python main.py path/to/swagger.yaml
```

Output will be saved to `swagger_tests.feature`

### Web API

#### Start the server

```bash
python app.py
```

Server will start on `http://localhost:5000`

#### Generate from File Upload

```bash
curl -X POST \
  -F "file=@path/to/swagger.yaml" \
  http://localhost:5000/generate/upload
```

#### Generate from Text Input

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "specification": "openapi: 3.0.0\ninfo:\n  title: Sample API\n  version: 1.0.0\npaths:\n  /users:\n    get:\n      summary: Get users\n      responses:\n        200:\n          description: Success"
  }' \
  http://localhost:5000/generate/text
```

#### Download Results

```bash
curl http://localhost:5000/download/swagger_tests.feature -o my_tests.feature
```

#### Health Check

```bash
curl http://localhost:5000/health
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/generate/upload` | Generate from uploaded file |
| POST | `/generate/text` | Generate from text input |
| GET | `/download/<filename>` | Download test cases |

## Test Case Generation

The agent generates Gherkin test cases covering:

### Positive Tests
- Happy path scenarios
- Valid requests with expected responses
- All documented endpoints and methods
- Standard status codes (200, 201, etc.)

### Negative Tests
- Invalid input validation
- Missing required fields
- Wrong data types
- Out-of-range values
- Authentication/authorization failures
- Rate limiting scenarios
- Edge cases and boundary values
- Error status codes (400, 401, 403, 404, 500, etc.)

## Example Output

Generated `.feature` file:

```gherkin
Feature: User Management API
  As a user
  I want to manage user accounts
  So that I can perform user operations

  Scenario: Successfully retrieve all users
    Given the API is available
    When I send a GET request to /users
    Then the response status should be 200
    And the response should contain a list of users

  Scenario: Retrieve users with invalid token
    Given the API is available
    When I send a GET request to /users without authentication
    Then the response status should be 401
    And the response should indicate missing authentication
```

## Project Structure

```
ai-agent/
├── main.py              # Core agent logic
├── app.py               # Flask web application
├── requirements.txt     # Python dependencies
├── .env.example         # Environment configuration template
├── README.md            # This file
├── uploads/             # Uploaded Swagger files
├── results/             # Generated test cases
└── .gitignore           # Git ignore rules
```

## Troubleshooting

### Google Cloud Authentication Error

Ensure you have valid credentials:
```bash
gcloud auth application-default login
```

### File Upload Size Limit

Default limit is 10MB. Modify `MAX_FILE_SIZE` in `app.py` if needed.

### Invalid Swagger/OpenAPI File

Ensure your file is valid YAML or JSON and follows OpenAPI 3.0 or Swagger 2.0 specification.

## Environment Variables

- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `PORT`: Server port (default: 5000)
- `DEBUG`: Enable debug mode (default: False)
- `MODEL_NAME`: LLM model to use (default: gemini-3.5-flash)
- `LOCATION`: Google AI location (default: global)

## Docker Deployment

Build and run with Docker:

```bash
docker build -t gherkin-agent .
docker run -p 5000:5000 \
  -e GOOGLE_CLOUD_PROJECT=your-project \
  -e GOOGLE_APPLICATION_CREDENTIALS=/etc/secrets/credentials.json \
  -v /path/to/credentials.json:/etc/secrets/credentials.json \
  gherkin-agent
```

## Performance

- Small specs (<1MB): ~10-30 seconds
- Medium specs (1-5MB): ~30-60 seconds
- Large specs (5-10MB): ~60-120 seconds

## Limitations

- Maximum file size: 10MB
- Supports OpenAPI 3.0 and Swagger 2.0 formats
- Requires valid Google Cloud credentials
- Rate limited by Google Vertex AI API

## License

MIT

## Support

For issues or questions, please submit an issue in the repository.
