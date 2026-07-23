# Test Execution Summary Generator - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd app-qag-sample-application
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app.py
```

Output:
```
Starting Gherkin Test Case Generation Agent on port 8080...
 * Running on http://0.0.0.0:8080
```

### 3. Generate Your First Summary

#### Option A: Using an HTML File
```bash
# Have a Serenity report file (index.html)
curl -X POST -F "file=@index.html" \
  http://localhost:8080/summary/upload \
  -o test_summary.html

# Open in browser
start test_summary.html  # Windows
open test_summary.html   # macOS
xdg-open test_summary.html  # Linux
```

#### Option B: Using Python
```python
from test_summary_agent import generate_summary_from_html

metrics, report = generate_summary_from_html('serenity_report.html')
print(f"Pass Rate: {metrics['pass_rate']}%")
print(f"Tests Run: {metrics['total_tests']}")

# Save report
with open('summary.html', 'w') as f:
    f.write(report)
```

## Key Features at a Glance

### 📊 Generated Reports Include:
- ✅ Pass/Fail breakdown with donut charts
- ✅ Comparison with previous runs
- ✅ AI-powered insights and recommendations
- ✅ Failure details table
- ✅ Dark/Light theme toggle
- ✅ Mobile-responsive design

### 🤖 AI Analysis (when Google Cloud credentials available):
- Root cause detection
- Regression identification
- Flakiness tracking
- Improvement suggestions

## API Endpoints Quick Reference

| Method | Endpoint | Input | Output |
|--------|----------|-------|--------|
| POST | `/summary/upload` | HTML file | JSON + HTML report |
| POST | `/summary/text` | HTML as string | JSON + HTML inline |
| GET | `/summary/metrics/<file>` | filename | Metrics JSON |
| GET | `/download/<file>` | filename | File download |

## Common Use Cases

### 1. CI/CD Integration (GitHub Actions)
```yaml
- name: Generate Test Summary
  run: |
    curl -X POST -F "file=@serenity/index.html" \
         http://localhost:8080/summary/upload \
         -o test_summary.html
    
- name: Upload Artifact
  uses: actions/upload-artifact@v2
  with:
    name: test-summary
    path: test_summary.html
```

### 2. Command Line Report Generation
```bash
# Direct file processing
python test_summary_agent.py serenity_report.html
# Creates: serenity_report_summary.html
```

### 3. Programmatic Extraction
```bash
# Get just the metrics
curl http://localhost:8080/summary/metrics/serenity_report_summary.html | jq

# Extract pass rate
PASS_RATE=$(curl -s http://localhost:8080/summary/metrics/report.html | jq '.metrics.pass_rate')
echo "Pass Rate: ${PASS_RATE}%"
```

### 4. Batch Processing Multiple Reports
```bash
for report in serenity_*/index.html; do
  echo "Processing $report..."
  curl -X POST -F "file=@$report" \
       http://localhost:8080/summary/upload \
       -o "${report%/*}_summary.html"
done
```

## Generated Report Tour

When you open the generated HTML report:

1. **Top Section**: Overview metrics (Pass Rate, Total Tests, etc.)
2. **Middle Section**: Visual charts and comparisons
3. **AI Analysis Card**: Insights and recommendations
4. **Failure Table**: Details of failed tests
5. **Bottom**: Executive summary

**Interactive Features:**
- Click the theme toggle (top-right) to switch dark/light mode
- Hover over charts for details
- Scroll to see all sections
- Export buttons for PDF/metrics

## Troubleshooting

### "File not found" error
```bash
# Ensure file exists and path is correct
ls -la serenity_report.html

# Use absolute path
curl -X POST -F "file=@$(pwd)/serenity_report.html" http://localhost:8080/summary/upload
```

### "HTML content is too short" error
```bash
# Ensure you're providing actual Serenity HTML output
# Not a simple HTML file, but the full report
wc -c serenity_report.html  # Should be > 100KB usually
```

### No results in uploads/results folders
```bash
# Check folder exists and has write permissions
mkdir -p uploads results
chmod 755 uploads results
```

### Server won't start on port 8080
```bash
# Use different port
export PORT=8000
python app.py

# Or kill process using port 8080
# Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/macOS:
lsof -i :8080
kill -9 <PID>
```

## Next Steps

1. **Explore the generated report** in your browser
2. **Customize the theme** - modify CSS variables in `test_summary_agent.py`
3. **Add to CI/CD** - use provided examples in README.md
4. **Configure AI** - set up Google Cloud for advanced analysis
5. **Extend parsing** - customize `SerenityReportParser` for your report format

## Sample Report Metrics

A typical generated report will show:

```json
{
  "total_tests": 284,
  "passed": 267,
  "failed": 17,
  "skipped": 0,
  "flaky": 3,
  "pass_rate": 94.2,
  "duration": "3m 42s",
  "run_number": "#142",
  "timestamp": "2024-01-15T10:30:00",
  "test_categories": {
    "PaymentAPI": 100,
    "AuthService": 87,
    "ReportGeneration": 97
  }
}
```

## Performance Tips

- **Large reports** (>10MB): May take 30+ seconds to parse
- **Multiple reports**: Use batch processing with parallel curl
- **Web server**: Run behind nginx/Apache for better performance
- **Caching**: Save generated reports to avoid reprocessing

## Support & Documentation

- 📖 Full API docs: See `TEST_SUMMARY_AGENT.md`
- 🚀 Deployment guide: See `DEPLOYMENT_GUIDE.md`
- 💡 Implementation details: See `IMPLEMENTATION_SUMMARY.md`
- 🔧 Project structure: See `README.md`

## Example Workflow

```bash
# 1. Start server in background
python app.py &

# 2. Run your tests and get Serenity output
# (your test framework generates index.html)

# 3. Generate summary
curl -X POST -F "file=@target/serenity/index.html" \
     http://localhost:8080/summary/upload \
     -o test_report.html

# 4. View in browser
open test_report.html

# 5. Share or archive
cp test_report.html ./reports/run_$(date +%Y%m%d_%H%M%S).html
```

## Got Questions?

- Check `TEST_SUMMARY_AGENT.md` for detailed documentation
- Review code comments in `test_summary_agent.py`
- See curl examples in `README.md`
- Check troubleshooting section in this guide

