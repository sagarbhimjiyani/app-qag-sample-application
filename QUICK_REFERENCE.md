# Quick Reference Card - Test Summary Generator

## 🚀 Get Started in 3 Steps

### Step 1: Install
```bash
pip install -r requirements.txt
```

### Step 2: Run Server
```bash
python app.py
# Server runs at http://localhost:8080
```

### Step 3: Generate Summary
```bash
# Upload Serenity HTML report
curl -X POST -F "file=@serenity_report.html" \
  http://localhost:8080/summary/upload \
  -o summary.html

# Open in browser
open summary.html
```

---

## 📍 Core API Endpoints

### Upload Report File
```bash
POST /summary/upload
# Input: HTML file
# Output: JSON + HTML report

curl -X POST -F "file=@index.html" http://localhost:8080/summary/upload
```

### Send HTML as Text
```bash
POST /summary/text
# Input: JSON with html_content
# Output: JSON + inline HTML

curl -X POST http://localhost:8080/summary/text \
  -H "Content-Type: application/json" \
  -d '{"html_content":"<html>...</html>"}'
```

### Get Metrics
```bash
GET /summary/metrics/{filename}
# Output: Extracted metrics JSON

curl http://localhost:8080/summary/metrics/serenity_report_summary.html
```

---

## 🐍 Python Usage

```python
# Import
from test_summary_agent import generate_summary_from_html

# Generate
metrics, report_html = generate_summary_from_html('serenity_report.html')

# Save
with open('summary.html', 'w') as f:
    f.write(report_html)

# Access metrics
print(f"Pass Rate: {metrics['pass_rate']}%")
print(f"Failed Tests: {metrics['failed']}")
```

---

## 📊 Report Metrics Available

```python
{
  'total_tests': 284,          # Total tests executed
  'passed': 267,               # Passing tests
  'failed': 17,                # Failed tests
  'skipped': 0,                # Skipped tests
  'flaky': 3,                  # Flaky/unstable tests
  'pass_rate': 94.2,           # Pass rate percentage
  'duration': '3m 42s',        # Total execution time
  'run_number': '#142',        # Test run identifier
  'timestamp': '2024-...',     # Generation timestamp
  'failed_tests': [...],       # List of failures
  'test_categories': {...},    # Tests by category
}
```

---

## 🤖 AI Analysis (when available)

```python
{
  'root_causes': [...],        # Failure patterns
  'regressions': [...],        # New failures
  'improvements': [...],       # Resolved issues
  'recommendations': [...],    # Action items
  'summary': '...',            # Executive summary
  'flakiness_analysis': [...]  # Flaky test info
}
```

---

## 🎨 Report Features

| Feature | Description |
|---------|-------------|
| 📈 Charts | Pass/fail donut chart |
| 📊 Metrics | 7 key metric cards |
| 🔄 Compare | Previous run comparison |
| 🤖 AI | Root cause analysis |
| 📋 Details | Failure details table |
| 🌓 Themes | Dark/light mode |
| 📱 Responsive | Mobile-friendly |

---

## 🔧 Configuration

### Environment Variables
```bash
export PORT=8080
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Folder Structure
```
uploads/      # Auto-created: uploaded files
results/      # Auto-created: generated reports
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Use different port
export PORT=8000
python app.py
```

### File not found
```bash
# Use absolute path
curl -F "file=@$(pwd)/report.html" http://localhost:8080/summary/upload
```

### Import error: beautifulsoup4
```bash
# Install missing package
pip install beautifulsoup4
```

---

## 📚 Full Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview & API docs |
| `TEST_SUMMARY_AGENT.md` | Complete agent documentation |
| `QUICKSTART_SUMMARY_GENERATOR.md` | 5-minute setup guide |
| `IMPLEMENTATION_SUMMARY.md` | Technical overview |

---

## 🔗 Integration Examples

### CI/CD: GitHub Actions
```yaml
- name: Generate Summary
  run: |
    curl -X POST -F "file=@serenity/index.html" \
         http://localhost:8080/summary/upload \
         -o summary.html
```

### CI/CD: Jenkins
```groovy
sh '''
  curl -X POST -F "file=@target/serenity/index.html" \
       http://localhost:8080/summary/upload \
       -o test_summary.html
'''
```

### CLI
```bash
python test_summary_agent.py serenity_report.html
# Creates: serenity_report_summary.html
```

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Server running: `python app.py`
- [ ] Test endpoint: `curl http://localhost:8080/health`
- [ ] Generated report opens in browser
- [ ] Report shows pass rate and test metrics
- [ ] Dark/light theme toggle works

---

## 🎯 Common Workflows

### Workflow 1: Single Report
```bash
python app.py &
curl -F "file=@report.html" http://localhost:8080/summary/upload -o summary.html
open summary.html
```

### Workflow 2: Batch Processing
```bash
for html in reports/*.html; do
  curl -F "file=@$html" http://localhost:8080/summary/upload \
       -o "${html%.html}_summary.html"
done
```

### Workflow 3: Extract Metrics
```bash
curl http://localhost:8080/summary/metrics/report_summary.html | jq '.metrics.pass_rate'
```

---

## 📞 Support

- Questions? → See `README.md` or `TEST_SUMMARY_AGENT.md`
- Setup issues? → Check `QUICKSTART_SUMMARY_GENERATOR.md`
- API details? → Review test examples in documentation
- Want to extend? → Edit `test_summary_agent.py`

---

## 🎁 What's Next

1. **Generate your first report** → See Step 3 above
2. **Customize the theme** → Edit CSS in `test_summary_agent.py`
3. **Add to CI/CD** → Use integration examples above
4. **Set up AI analysis** → Configure Google Cloud credentials
5. **Deploy to production** → Follow deployment guide

---

Generated: 2024-01-15
Version: 1.0
Status: ✅ Ready to Use

