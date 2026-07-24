# QA & Test Automation Agent Suite

A comprehensive suite of AI-powered agents for test case generation, test execution analysis, and quality assurance automation.

## Features

🧪 **Gherkin Test Case Generation Agent** - Automatically generates comprehensive Gherkin/Cucumber test cases from Swagger/OpenAPI specifications

📊 **Test Execution Summary Generator** - NEW! Analyzes Serenity test execution reports and generates interactive HTML summaries with AI-powered insights

🤖 **AI-Powered Analysis** - Leverages Google Gemini for intelligent test case recommendations and failure analysis

## Quick Start

### Prerequisites
- Python 3.8+
- Flask
- Google Cloud credentials (for AI features)
- Dependencies: `pip install -r requirements.txt`

### Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Run the Flask server
python app.py
```

### Access the APIs
- **API Base URL:** http://localhost:8080
- **Health Check:** http://localhost:8080/health
- **Gherkin Generation:** /generate/upload, /generate/text
- **Test Summary:** /summary/upload, /summary/text

### Generated Reports
- **Gherkin Test Cases:** Results folder (`.feature` files)
- **Test Summaries:** Results folder (interactive HTML files)

## API Endpoints

### Health Check
```bash
GET /health
```
Returns service health status

### Gherkin Test Case Generation

#### Generate from Swagger/OpenAPI File
```bash
POST /generate/upload
Content-Type: multipart/form-data

file: (Swagger/OpenAPI YAML or JSON file)
```

Response:
```json
{
  "status": "success",
  "message": "Test cases generated successfully",
  "test_cases": "Gherkin feature content...",
  "result_file": "swagger_tests.feature",
  "download_url": "/download/swagger_tests.feature"
}
```

#### Generate from Text Specification
```bash
POST /generate/text
Content-Type: application/json

{
  "specification": "{...OpenAPI spec as JSON string...}"
}
```

Response:
```json
{
  "status": "success",
  "message": "Test cases generated successfully",
  "test_cases": "Gherkin feature content..."
}
```

### Test Execution Summary Generation

#### Generate Summary from Serenity Report (File)
```bash
POST /summary/upload
Content-Type: multipart/form-data

file: (Serenity HTML report file)
```

Response:
```json
{
  "status": "success",
  "message": "Test execution summary generated successfully",
  "metrics": {
    "total_tests": 284,
    "passed": 267,
    "failed": 17,
    "flaky": 3,
    "pass_rate": 94.2,
    "duration": "3m 42s"
  },
  "report_file": "serenity_report_summary.html",
  "download_url": "/download/serenity_report_summary.html"
}
```

#### Generate Summary from HTML Content
```bash
POST /summary/text
Content-Type: application/json

{
  "html_content": "<!DOCTYPE html>...Serenity report...</html>"
}
```

Response:
```json
{
  "status": "success",
  "message": "Test execution summary generated successfully",
  "metrics": {...},
  "report": "<html>...interactive report...</html>"
}
```

#### Get Summary Metrics
```bash
GET /summary/metrics/{filename}
```

### Download Generated Files
```bash
GET /download/{filename}
```

Downloads any generated report or test case file

## Project Structure

```
app-qag-sample-application/
├── main.py                      # Gherkin Test Case Generation Agent
├── test_summary_agent.py        # NEW: Test Execution Summary Generator
├── app.py                       # Flask REST API server
├── summary_generator.py         # Legacy summary generator
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker build configuration
├── README.md                    # This file
├── TEST_SUMMARY_AGENT.md       # Detailed Test Summary Agent docs
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
├── ai-agent/
│   ├── qa_genie.html           # Interactive QA management UI
│   ├── index.html              # Dashboard
│   └── example_swagger.yaml    # Example API specification
└── results/                    # Generated reports and test files
```

## Agents Overview

### 1. Gherkin Test Case Generation Agent
**File:** `main.py`

Analyzes Swagger/OpenAPI specifications and generates comprehensive Gherkin/Cucumber test cases.

**Capabilities:**
- Parses Swagger/OpenAPI specifications
- Generates positive test scenarios
- Generates negative test scenarios (validation, edge cases)
- Supports header and query parameters
- AI-enhanced recommendations

**Usage:**
```bash
# Command line
python main.py swagger_spec.yaml

# Via API
curl -X POST -F "file=@swagger.yaml" http://localhost:8080/generate/upload
```

### 2. Test Execution Summary Generator Agent
**File:** `test_summary_agent.py` (NEW!)

Parses Serenity test execution reports and generates interactive HTML summaries with AI-powered analysis.

**Capabilities:**
- Extracts metrics from Serenity reports
- Generates interactive HTML summaries
- AI-powered analysis:
  - Root cause detection
  - Regression identification
  - Improvement tracking
  - Flakiness analysis
- Visual charts and comparisons
- Dark/Light theme support

**Usage:**
```bash
# Command line
python test_summary_agent.py serenity_report.html

# Via API
curl -X POST -F "file=@index.html" http://localhost:8080/summary/upload
```

See [TEST_SUMMARY_AGENT.md](TEST_SUMMARY_AGENT.md) for detailed documentation.

## Interactive HTML Reports

### Test Summary Report Features
- **Pass Rate Visualization**: Donut charts with color-coded breakdown
- **Metrics Dashboard**: Key performance indicators and trends
- **AI Insights**: Root cause analysis and recommendations
- **Failure Analysis**: Detailed failure tables with severity levels
- **Comparison Charts**: Before/after comparison with previous runs
- **Theme Toggle**: Dark/Light mode support
- **Export Options**: PDF export, metrics export

### Report Example
Open any generated `.html` file in a web browser to view the interactive report with:
- Real-time theme switching
- Responsive design (desktop, tablet, mobile)
- Hoverable tooltips
- Clickable sections for detailed views

## Testing with cURL

### Gherkin Generation Examples

```bash
# Generate from Swagger file
curl -X POST -F "file=@example_swagger.yaml" \
  http://localhost:8080/generate/upload \
  -o generated_tests.feature

# Generate from text specification
curl -X POST http://localhost:8080/generate/text \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "specification": "openapi: 3.0.0\ninfo:\n  title: Test API\nversion: 1.0.0"
}
EOF
```

### Test Summary Examples

```bash
# Upload Serenity report and generate summary
curl -X POST -F "file=@serenity_report.html" \
  http://localhost:8080/summary/upload \
  -o test_summary.html

# Generate from HTML text
curl -X POST http://localhost:8080/summary/text \
  -H "Content-Type: application/json" \
  -d '{"html_content":"<html>...</html>"}' \
  -o response.json

# Get metrics from saved report
curl http://localhost:8080/summary/metrics/serenity_report_summary.html

# Download generated file
curl http://localhost:8080/download/generated_tests.feature \
  -o my_tests.feature
```

## Configuration

### Environment Variables

```bash
# Server configuration
PORT=8080
DEBUG=False

# Google Cloud (for AI features)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

### File Structure for Results

```
uploads/              # Uploaded files
results/              # Generated reports and tests
├── *.feature         # Generated Gherkin test cases
├── *_summary.html    # Generated test summaries
└── *.json            # Extracted metrics
```

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t qa-agents:latest .

# Run container
docker run -d -p 8080:8080 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/service-account-key.json \
  -v /path/to/service-account-key.json:/app/service-account-key.json \
  --name qa-agents qa-agents:latest

# View logs
docker logs -f qa-agents
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment options.

## Dependencies

### Python Packages
```
google-adk              # Google AI Agent Development Kit
google-genai==2.12.1   # Google Generative AI client
pyyaml                 # YAML parser
flask==2.3.0           # Web framework
python-dotenv==1.0.0   # Environment variable management
pydantic               # Data validation
beautifulsoup4         # HTML parsing (for Serenity reports)
```

Install with:
```bash
pip install -r requirements.txt
```

## Advanced Features

### AI-Powered Analysis (Requires Google Cloud Setup)

Both agents leverage Google Gemini for intelligent analysis:

1. **Test Case Generation**: 
   - Semantic understanding of API specifications
   - Intelligent negative test case generation
   - Best practice recommendations

2. **Test Summary Analysis**:
   - Root cause detection from failure patterns
   - Regression identification
   - Flaky test analysis
   - Improvement recommendations

### Fallback Modes

If Google Cloud credentials are unavailable:
- Gherkin generation falls back to deterministic conversion
- Test summary uses template-based analysis
- Core functionality remains available

## Troubleshooting

### Issue: Google Cloud credentials not found
**Solution:**
```bash
# Set credentials path
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Or copy to default location
cp service-account-key.json ~/.config/gcloud/application_default_credentials.json
```

### Issue: HTML report not generated
**Solution:**
1. Verify Serenity HTML format is valid
2. Check file permissions in `results/` folder
3. Review error logs from `/summary/upload` endpoint

### Issue: Test cases generation fails
**Solution:**
1. Validate OpenAPI/Swagger specification format
2. Ensure specification has required fields (openapi/swagger version)
3. Check Python imports: `pip install -r requirements.txt`

### Issue: Port 8080 already in use
**Solution:**
```bash
# Use different port
export PORT=8000
python app.py

# Or kill process on port 8080
# Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

## Integration Examples

### GitHub Actions CI/CD

```yaml
name: Generate Test Summary

on:
  workflow_run:
    workflows: [Run Tests]
    types: [completed]

jobs:
  summary:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Download test results
        uses: actions/download-artifact@v2
        with:
          name: test-report
          
      - name: Generate Summary
        run: |
          curl -X POST -F "file=@index.html" \
               http://qa-agents.example.com:8080/summary/upload \
               -o test_summary.html
               
      - name: Upload Summary
        uses: actions/upload-artifact@v2
        with:
          name: test-summary
          path: test_summary.html
```

### Jenkins Pipeline

```groovy
stage('Generate Test Summary') {
    steps {
        script {
            def response = sh(
                script: '''
                    curl -X POST -F "file=@target/serenity/index.html" \\
                         http://localhost:8080/summary/upload \\
                         -o test_summary.json
                ''',
                returnStdout: true
            ).trim()
            
            echo "Test Summary Generated: $response"
        }
    }
}
```

## Contributing

Contributions are welcome! To extend the agents:

1. **Add new test generation rules**: Modify `main.py`
2. **Customize reports**: Edit HTML templates in `test_summary_agent.py`
3. **Enhance metrics parsing**: Extend `SerenityReportParser` class
4. **Add new API endpoints**: Update `app.py`

## Documentation

- [TEST_SUMMARY_AGENT.md](TEST_SUMMARY_AGENT.md) - Detailed test summary agent documentation
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment guide
- [QUICKSTART.md](ai-agent/QUICKSTART.md) - Quick start guide for QA Genie UI
