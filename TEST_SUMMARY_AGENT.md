# Test Execution Summary Generator Agent

## Overview

The **Test Execution Summary Generator Agent** is a new AI-powered component that analyzes Serenity test execution reports and generates interactive, user-readable HTML summaries with AI-powered insights and recommendations.

### Features

- **Automated Report Parsing**: Extracts key metrics from Serenity HTML test execution reports
- **Interactive HTML Summaries**: Generates beautiful, theme-aware reports (dark/light mode support)
- **AI-Powered Analysis**: 
  - Root cause analysis of test failures
  - Regression detection
  - Improvement tracking
  - Actionable recommendations
  - Flakiness analysis
- **Comprehensive Metrics**: 
  - Pass/fail rates and breakdowns
  - Test duration tracking
  - Flaky test detection
  - Comparison with previous runs
- **RESTful API Endpoints**: Easy integration with CI/CD pipelines

## Architecture

### Components

1. **test_summary_agent.py**: Core agent module
   - `SerenityReportParser`: Extracts metrics from Serenity HTML
   - `generate_ai_insights()`: AI-powered analysis using Gemini
   - `generate_interactive_html_report()`: Creates interactive HTML summaries

2. **app.py**: Flask API endpoints
   - `/summary/upload` - File upload endpoint
   - `/summary/text` - Text content endpoint
   - `/summary/metrics/<filename>` - Retrieve metrics

## API Endpoints

### 1. Upload Serenity Report (File)

**Endpoint**: `POST /summary/upload`

Upload a Serenity HTML test execution report file.

**Request**:
```bash
curl -X POST -F "file=@serenity_report.html" http://localhost:8080/summary/upload
```

**Response**:
```json
{
  "status": "success",
  "message": "Test execution summary generated successfully",
  "metrics": {
    "total_tests": 284,
    "passed": 267,
    "failed": 17,
    "skipped": 0,
    "flaky": 3,
    "pass_rate": 94.2,
    "duration": "3m 42s",
    "run_number": "#142"
  },
  "report_file": "serenity_report_summary.html",
  "download_url": "/download/serenity_report_summary.html"
}
```

### 2. Generate Summary from HTML Text

**Endpoint**: `POST /summary/text`

Generate summary from Serenity HTML content as text.

**Request**:
```bash
curl -X POST http://localhost:8080/summary/text \
  -H "Content-Type: application/json" \
  -d '{
    "html_content": "<html>...Serenity report HTML...</html>"
  }'
```

**Response**:
```json
{
  "status": "success",
  "message": "Test execution summary generated successfully",
  "metrics": { ... },
  "report": "<html>...generated report...</html>"
}
```

### 3. Get Metrics from Saved Report

**Endpoint**: `GET /summary/metrics/<filename>`

Retrieve metrics from a previously generated summary report.

**Request**:
```bash
curl http://localhost:8080/summary/metrics/serenity_report_summary.html
```

**Response**:
```json
{
  "status": "success",
  "metrics": { ... },
  "report_file": "serenity_report_summary.html"
}
```

## Generated Report Features

### Summary Section
- **Overall Metrics**: Pass rate, total tests, passed/failed/skipped/flaky counts
- **Visual Breakdown**: Donut chart showing pass/fail distribution
- **Comparison Charts**: Compare with previous test runs
- **Duration Analysis**: Test execution time tracking

### AI Analysis Section
- **Root Cause Analysis**: Identifies common failure patterns
- **Regressions**: Detects tests that passed before but failed now
- **Improvements**: Highlights resolved issues
- **Recommendations**: Actionable next steps
- **Flakiness Tracking**: Identifies unstable tests

### Detailed Failure Table
- Test case names and endpoints
- Error messages and categories
- Severity levels (High/Medium/Low)
- Quick actions (create Jira tickets, export)

### Theme Support
- Dark mode (default)
- Light mode
- Persistent theme preference (localStorage)
- High-contrast visual hierarchy

## Metrics Extracted

| Metric | Description |
|--------|-------------|
| total_tests | Total number of tests executed |
| passed | Number of passing tests |
| failed | Number of failing tests |
| skipped | Number of skipped tests |
| flaky | Number of flaky/intermittent tests |
| pass_rate | Percentage of passing tests |
| duration | Total execution time |
| run_number | Test run identifier |
| failed_tests | List of failed test details |
| test_categories | Tests grouped by category |

## AI Analysis Features

When AI/LLM is available, the agent provides:

1. **Root Cause Detection**
   - Pattern matching across failures
   - Infrastructure issue identification
   - Test environment analysis

2. **Regression Detection**
   - Comparison with baseline metrics
   - New failure identification
   - Historical trend analysis

3. **Improvement Tracking**
   - Resolved issue identification
   - Performance improvements
   - Quality trend analysis

4. **Smart Recommendations**
   - Prioritized action items
   - Root cause mitigation steps
   - Quality improvement suggestions

5. **Flakiness Analysis**
   - Test stability scoring
   - Flaky test clustering
   - Data isolation issue detection

## Usage Examples

### Python Integration

```python
from test_summary_agent import generate_summary_from_html

# Generate summary from file
metrics, report_html = generate_summary_from_html('/path/to/serenity_report.html')

# Save report
with open('summary_report.html', 'w') as f:
    f.write(report_html)

# Print metrics
print(f"Pass Rate: {metrics['pass_rate']}%")
print(f"Failed Tests: {metrics['failed']}")
```

### CLI Usage

```bash
python test_summary_agent.py /path/to/serenity_report.html
```

This generates `serenity_report_summary.html` with the interactive summary.

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Generate Test Summary
  run: |
    curl -X POST -F "file=@serenity_report/index.html" \
         http://localhost:8080/summary/upload \
         -o summary_report.html

- name: Upload Artifact
  uses: actions/upload-artifact@v2
  with:
    name: test-summary-report
    path: summary_report.html
```

### Jenkins Example

```groovy
stage('Generate Test Summary') {
    steps {
        sh '''
            curl -X POST -F "file=@target/serenity/index.html" \
                 http://localhost:8080/summary/upload \
                 -o test_summary.html
        '''
    }
}
```

## Customization

### AI Model Configuration

To use a different AI model, modify `test_summary_agent.py`:

```python
# Change model in GlobalGemini
analysis_agent = LlmAgent(
    model=GlobalGemini(model='gemini-3-flash'),  # Or another model
    # ...
)
```

### Report Template Customization

Modify the HTML template in `generate_interactive_html_report()`:
- Colors and theme variables (CSS variables)
- Layout structure (grid templates)
- Chart types and data visualization

### Metrics Extraction

Extend `SerenityReportParser._extract_metrics()` to parse additional metrics from your Serenity report format.

## Troubleshooting

### Issue: AI analysis not working
- Ensure Google Cloud credentials are configured (ADC - Application Default Credentials)
- Check `LLM_AVAILABLE` flag in logs
- Verify `test_summary_agent.py` imports work correctly

### Issue: Report not generated
- Validate Serenity HTML format matches expected structure
- Check file permissions in uploads/results folders
- Review error message for specific parsing failure

### Issue: Metrics not extracted correctly
- Verify Serenity HTML structure matches parser expectations
- Extend `SerenityReportParser` for custom Serenity versions
- Use `/summary/text` endpoint to debug HTML parsing

## Dependencies

- `beautifulsoup4`: HTML parsing
- `flask==2.3.0`: Web framework
- `google-genai==2.12.1`: AI analysis (optional)
- `google-adk`: ADK framework for agents (optional)
- `pyyaml`: Configuration support

## File Structure

```
app-qag-sample-application/
├── test_summary_agent.py       # New: Core agent module
├── app.py                       # Modified: Added /summary/* endpoints
├── main.py                      # Gherkin generation agent
├── summary_generator.py         # Original summary generator
├── requirements.txt             # Dependencies
├── README.md                    # Original README
└── TEST_SUMMARY_AGENT.md       # This file
```

## Related Agents

- **Gherkin Test Case Generation Agent** (`main.py`): Generates test cases from Swagger/OpenAPI
- **Summary Generator** (`summary_generator.py`): Original summary generation (superceded)

## Contributing

To extend the Summary Generator Agent:

1. Modify `SerenityReportParser` to support new report formats
2. Extend `generate_ai_insights()` for additional analysis types
3. Customize HTML template in `generate_interactive_html_report()`
4. Add new endpoints in `app.py`

## License

Same as parent project.

