# Quick Start: Deploy to Google Cloud Run (5 Minutes)

## TL;DR - Fast Path

### For Windows (PowerShell)
```powershell
# 1. Set your project
$env:PROJECT_ID = "your-gcp-project-id"
gcloud config set project $env:PROJECT_ID

# 2. Run automated deployment
python deploy.py
```

### For Mac/Linux (Bash)
```bash
# 1. Set your project
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# 2. Make script executable and run
chmod +x deploy.sh
./deploy.sh
```

---

## What the Script Does

The deployment script automates all these steps:
1. ✅ Checks for gcloud and Docker
2. ✅ Confirms your GCP project
3. ✅ Enables required APIs (Cloud Run, Vertex AI, Container Registry)
4. ✅ Creates service account with permissions
5. ✅ Builds Docker image
6. ✅ Pushes image to Container Registry
7. ✅ Deploys to Cloud Run
8. ✅ Tests the deployment
9. ✅ Outputs service URL

**Time: ~5-10 minutes** (mostly waiting for Docker build)

---

## Manual Step-by-Step (if you prefer)

### Step 1: Prerequisites
```bash
gcloud version
docker version
```

### Step 2: Set Project
```bash
gcloud config set project YOUR_PROJECT_ID
gcloud config get-value project  # Verify
```

### Step 3: Enable APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable logging.googleapis.com
```

### Step 4: Create Service Account
```bash
gcloud iam service-accounts create gherkin-agent-sa \
    --display-name="Gherkin Agent Service Account"

SA_EMAIL="gherkin-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user" --quiet

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser" --quiet

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/logging.logWriter" --quiet
```

### Step 5: Build and Push Docker Image
```bash
gcloud auth configure-docker gcr.io --quiet

IMAGE_NAME="gcr.io/YOUR_PROJECT_ID/gherkin-agent"

docker build -t $IMAGE_NAME .
docker push $IMAGE_NAME
```

### Step 6: Deploy to Cloud Run
```bash
gcloud run deploy gherkin-agent \
    --image=$IMAGE_NAME \
    --region=us-central1 \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" \
    --service-account=$SA_EMAIL \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --port=5000 \
    --quiet
```

### Step 7: Get Service URL
```bash
gcloud run services describe gherkin-agent \
    --region=us-central1 \
    --format="value(status.url)"
```

### Step 8: Test
```bash
# Test health endpoint
curl https://gherkin-agent-XXX.a.run.app/health

# Test file upload
curl -X POST -F "file=@example_swagger.yaml" \
    https://gherkin-agent-XXX.a.run.app/generate/upload
```

---

## After Deployment

### View Service
```bash
# List all services
gcloud run services list

# Get service details
gcloud run services describe gherkin-agent --region=us-central1
```

### View Logs
```bash
# Recent logs
gcloud run logs read gherkin-agent --limit=50

# Stream logs live
gcloud run logs read gherkin-agent --follow

# Filter by error
gcloud run logs read gherkin-agent --limit=100 | grep ERROR
```

### Update Service (after code changes)
```bash
# Rebuild and push
docker build -t gcr.io/YOUR_PROJECT_ID/gherkin-agent .
docker push gcr.io/YOUR_PROJECT_ID/gherkin-agent

# Redeploy (uses latest image)
gcloud run deploy gherkin-agent \
    --image=gcr.io/YOUR_PROJECT_ID/gherkin-agent \
    --region=us-central1 --quiet
```

### Delete Service
```bash
gcloud run services delete gherkin-agent --region=us-central1 --quiet
```

---

## API Endpoints

Once deployed, your service responds to:

### 1. Health Check
```bash
curl https://your-service-url/health
```
Response:
```json
{
  "status": "healthy",
  "service": "Gherkin Test Case Generation Agent"
}
```

### 2. Generate from File Upload
```bash
curl -X POST \
  -F "file=@your_swagger.yaml" \
  https://your-service-url/generate/upload
```

### 3. Generate from Text
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"specification": "openapi: 3.0.0..."}' \
  https://your-service-url/generate/text
```

### 4. Download Results
```bash
curl https://your-service-url/download/filename.feature \
  -o my_tests.feature
```

---

## Troubleshooting

### "Command not found: gcloud"
```bash
# Install Google Cloud SDK
# Windows: https://cloud.google.com/sdk/docs/install-gcloud-on-windows
# Mac: brew install --cask google-cloud-sdk
# Linux: https://cloud.google.com/sdk/docs/install-gcloud-on-linux
```

### "Permission denied" when pushing image
```bash
gcloud auth configure-docker gcr.io --quiet
```

### Service returns 500 errors
```bash
# Check logs
gcloud run logs read gherkin-agent --follow

# Common causes:
# 1. Missing GOOGLE_CLOUD_PROJECT env var
# 2. Service account doesn't have aiplatform.user role
# 3. Insufficient memory (try --memory=4Gi)
```

### "Model not found" error
```bash
# Verify Vertex AI API is enabled
gcloud services list --enabled | grep aiplatform

# Verify service account has role
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:gherkin-agent-sa@*"
```

### Service taking long to respond
```bash
# Increase timeout (default 600s)
gcloud run services update gherkin-agent \
    --timeout=900 --region=us-central1

# Or increase memory/CPU
gcloud run services update gherkin-agent \
    --memory=4Gi --cpu=4 --region=us-central1
```

---

## Monitoring & Costs

### Check Costs
```bash
# View billing in Cloud Console
# https://console.cloud.google.com/billing
```

### Set Billing Alert
```bash
# Via Cloud Console:
# 1. Go to https://console.cloud.google.com/billing/alerts
# 2. Create budget alert
```

### Auto-scaling Settings
```bash
# Set min/max instances
gcloud run services update gherkin-agent \
    --min-instances=1 \
    --max-instances=100 \
    --region=us-central1

# 0 instances = no cost when idle, but cold starts (~5s)
# 1 instance = always running, slight cost
```

---

## Real-World Usage Examples

### Generate tests from a file
```bash
SERVICE_URL="https://gherkin-agent-xxx.a.run.app"

# Upload swagger.yaml and get test cases
curl -X POST \
  -F "file=@./swagger.yaml" \
  "$SERVICE_URL/generate/upload" \
  | jq '.test_cases' > output_tests.feature

# Download the generated file
curl "$SERVICE_URL/download/swagger_tests.feature" \
  -o my_tests.feature
```

### Generate tests from OpenAPI spec as text
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d @- https://gherkin-agent-xxx.a.run.app/generate/text << 'EOF'
{
  "specification": "openapi: 3.0.0\ninfo:\n  title: My API\n  version: 1.0\npaths:\n  /users:\n    get:\n      responses:\n        200:\n          description: Success"
}
EOF
```

### Integrate into CI/CD Pipeline (GitHub Actions)
```yaml
name: Generate Tests
on: [push]

jobs:
  test-generation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Generate Gherkin Tests
        run: |
          curl -X POST \
            -F "file=@./specs/swagger.yaml" \
            ${{ secrets.GHERKIN_AGENT_URL }}/generate/upload \
            -o tests.json
          
          # Extract test cases from response
          jq '.test_cases' tests.json > features/api_tests.feature
      
      - name: Commit changes
        run: |
          git add features/api_tests.feature
          git commit -m "Auto-generated tests"
          git push
```

---

## Support

For detailed information, see:
- **DEPLOYMENT_GUIDE.md** - Comprehensive deployment guide
- **README.md** - Full API documentation
- **GCP Docs**: https://cloud.google.com/run/docs
- **Vertex AI**: https://cloud.google.com/vertex-ai/docs

---

**Ready? Run `python deploy.py` or `./deploy.sh` now! 🚀**
