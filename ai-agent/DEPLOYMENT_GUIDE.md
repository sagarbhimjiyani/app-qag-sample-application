# Deployment Guide: Gherkin Test Case Generation Agent to Google Cloud Run

Complete step-by-step guide to deploy your AI agent to Google Cloud Platform.

## Prerequisites

- Google Cloud CLI (`gcloud`) installed locally
- Docker installed locally
- Personal Google Cloud account with billing enabled
- Text editor for configuration files

## Step-by-Step Deployment

### STEP 1: Set Up Your Google Cloud Project

#### 1.1 List Your Existing Projects

```bash
gcloud projects list
```

This will show your existing projects. Note down the **PROJECT_ID** you want to use.

#### 1.2 Set Active Project

```bash
gcloud config set project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual project ID (e.g., `my-project-123456`)

#### 1.3 Verify Active Project

```bash
gcloud config get-value project
```

Should output your selected project ID.

---

### STEP 2: Enable Required Google Cloud APIs

The agent needs these APIs enabled in your GCP project:

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Vertex AI API (for Gemini model)
gcloud services enable aiplatform.googleapis.com

# Enable Artifact Registry API (alternative to Container Registry)
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Build API (for building containers)
gcloud services enable cloudbuild.googleapis.com

# Enable Logging API
gcloud services enable logging.googleapis.com
```

**Verification:**
```bash
gcloud services list --enabled | grep -E "run|vertexai|artifact|build|logging"
```

---

### STEP 3: Create a Service Account

The agent needs a service account to call Google APIs.

#### 3.1 Create Service Account

```bash
gcloud iam service-accounts create gherkin-agent-sa \
    --display-name="Gherkin Agent Service Account" \
    --description="Service account for Gherkin test generation agent"
```

#### 3.2 Grant Required Permissions

```bash
# Grant Vertex AI User role (needed for Gemini access)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:gherkin-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Grant basic service account user role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:gherkin-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Grant logs writer role (for Cloud Logging)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:gherkin-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/logging.logWriter"
```

#### 3.3 Verify Service Account

```bash
gcloud iam service-accounts list
```

You should see `gherkin-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`

---

### STEP 4: Authenticate with Your Service Account

#### 4.1 Create and Download Key

```bash
gcloud iam service-accounts keys create ./service-account-key.json \
    --iam-account=gherkin-agent-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

This creates `service-account-key.json` in your `ai-agent` directory.

**⚠️ IMPORTANT: Keep this file secure and never commit it to Git!**

Verify it's in `.gitignore`:
```bash
cat .gitignore | grep credentials
```

---

### STEP 5: Build and Push Docker Image to Container Registry

#### 5.1 Configure Docker Authentication

```bash
gcloud auth configure-docker gcr.io
```

#### 5.2 Set Variables for Convenience

```bash
# Set your variables (replace with your actual values)
$env:PROJECT_ID = "YOUR_PROJECT_ID"
$env:REGION = "us-central1"  # or your preferred region
$env:SERVICE_NAME = "gherkin-agent"
$env:IMAGE_NAME = "gcr.io/$env:PROJECT_ID/$env:SERVICE_NAME"
```

On Linux/Mac:
```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-central1"
export SERVICE_NAME="gherkin-agent"
export IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
```

#### 5.3 Build Docker Image

```bash
docker build -t $env:IMAGE_NAME .
```

Output should end with: `Successfully tagged gcr.io/YOUR_PROJECT_ID/gherkin-agent`

#### 5.4 Push Image to Container Registry

```bash
docker push $env:IMAGE_NAME
```

This uploads your image to Google Container Registry.

**Verify Upload:**
```bash
gcloud container images list --repository-format=VALUE --filter="name:gherkin"
```

---

### STEP 6: Deploy to Cloud Run

#### 6.1 Deploy with Required Configuration

```bash
gcloud run deploy $env:SERVICE_NAME `
    --image=$env:IMAGE_NAME `
    --region=$env:REGION `
    --platform=managed `
    --allow-unauthenticated `
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$env:PROJECT_ID" `
    --service-account="gherkin-agent-sa@$env:PROJECT_ID.iam.gserviceaccount.com" `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --port=5000
```

On Linux/Mac:
```bash
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_NAME \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --service-account="gherkin-agent-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --port=5000
```

#### 6.2 Deployment Output

The command will output something like:
```
Service [gherkin-agent] successfully deployed.
Service URL: https://gherkin-agent-xxx-uc.a.run.app
```

**Copy and save this URL!** This is your agent's public endpoint.

---

### STEP 7: Verify Deployment

#### 7.1 Test Health Endpoint

```bash
$env:SERVICE_URL = "https://gherkin-agent-xxx-uc.a.run.app"
curl "$env:SERVICE_URL/health"
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Gherkin Test Case Generation Agent"
}
```

#### 7.2 View Logs

```bash
gcloud run logs read $env:SERVICE_NAME --region=$env:REGION --limit=50
```

Or use Cloud Console:
https://console.cloud.google.com/run

---

### STEP 8: Test the Agent

#### 8.1 Test with File Upload

```bash
curl -X POST `
    -F "file=@example_swagger.yaml" `
    "$env:SERVICE_URL/generate/upload"
```

Expected response (JSON with generated test cases):
```json
{
  "status": "success",
  "message": "Test cases generated successfully",
  "test_cases": "Feature: User Management API...",
  "result_file": "example_swagger_tests.feature",
  "download_url": "/download/example_swagger_tests.feature"
}
```

#### 8.2 Download Generated File

```bash
curl "$env:SERVICE_URL/download/example_swagger_tests.feature" -o my_tests.feature
cat my_tests.feature
```

#### 8.3 Test with Text Input

```bash
$spec = @"
openapi: 3.0.0
info:
  title: Sample API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get users
      responses:
        200:
          description: Success
"@

curl -X POST `
    -H "Content-Type: application/json" `
    -d "{\"specification\": \"$spec\"}" `
    "$env:SERVICE_URL/generate/text"
```

---

### STEP 9: Configure Auto-Scaling (Optional)

By default, Cloud Run auto-scales. To customize:

```bash
gcloud run services update $env:SERVICE_NAME `
    --region=$env:REGION `
    --min-instances=1 `
    --max-instances=100 `
    --concurrency=80
```

- `min-instances`: Prevents cold starts (costs apply even when idle)
- `max-instances`: Prevents runaway costs
- `concurrency`: Max requests per container instance

---

### STEP 10: Monitor and Manage

#### 10.1 View Service Details

```bash
gcloud run services describe $env:SERVICE_NAME --region=$env:REGION
```

#### 10.2 Update Service (after code changes)

```bash
docker build -t $env:IMAGE_NAME .
docker push $env:IMAGE_NAME
gcloud run deploy $env:SERVICE_NAME `
    --image=$env:IMAGE_NAME `
    --region=$env:REGION
```

#### 10.3 View Metrics

```bash
gcloud run services describe $env:SERVICE_NAME --region=$env:REGION
```

Or visit Cloud Console: https://console.cloud.google.com/run

#### 10.4 Set Up Alerts

Go to: Cloud Console → Monitoring → Alerting → Create Policy

---

## Troubleshooting

### Issue: "Permission denied" when pushing to Container Registry

**Solution:**
```bash
gcloud auth configure-docker gcr.io
```

### Issue: "API X not enabled" error during deployment

**Solution:**
```bash
# Enable the missing API
gcloud services enable MISSING_API_NAME.googleapis.com
```

### Issue: Container won't start / timeout errors

**Check logs:**
```bash
gcloud run logs read $env:SERVICE_NAME --region=$env:REGION --limit=100
```

Likely causes:
- Missing GOOGLE_CLOUD_PROJECT env var
- Service account missing permissions
- Insufficient memory (increase via `--memory` flag)

### Issue: "Model not found" error from Gemini

**Solution:**
- Verify Vertex AI API is enabled
- Verify service account has `roles/aiplatform.user` role
- Verify `GOOGLE_CLOUD_PROJECT` environment variable is set

---

## Cost Management

### Estimated Monthly Costs

For light usage (< 1 million requests/month):
- **Cloud Run**: ~$0.40 (free tier: 2M requests)
- **Vertex AI (Gemini)**: ~$1.50 per million tokens
- **Container Registry storage**: ~$0.10
- **Logging**: Free tier usually sufficient

**Total**: ~$2-5/month for personal use

### Cost Optimization

1. Set `max-instances` to prevent runaway costs
2. Use `min-instances=0` to avoid idle charges
3. Monitor usage: https://console.cloud.google.com/billing
4. Set up billing alerts in GCP Console

---

## Environment Variables Reference

| Variable | Value | Required |
|----------|-------|----------|
| `GOOGLE_CLOUD_PROJECT` | Your GCP Project ID | ✅ |
| `PORT` | 5000 | Default |
| `DEBUG` | False | Default |
| `MODEL_NAME` | gemini-3.5-flash | Default |
| `LOCATION` | global | Default |

---

## Manual Deployment Alternative (Docker Compose)

If you want to run locally with Docker Compose:

```bash
# Set environment
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\service-account-key.json"
$env:GOOGLE_CLOUD_PROJECT = "YOUR_PROJECT_ID"

# Run
docker-compose up
```

Access at: http://localhost:5000

---

## Quick Reference Commands

```bash
# View all deployed services
gcloud run services list --region=$env:REGION

# Delete the service (if needed)
gcloud run services delete $env:SERVICE_NAME --region=$env:REGION

# Redeploy after code changes
docker build -t $env:IMAGE_NAME . && docker push $env:IMAGE_NAME && gcloud run deploy $env:SERVICE_NAME --image=$env:IMAGE_NAME --region=$env:REGION

# Stream logs in real-time
gcloud run logs read $env:SERVICE_NAME --region=$env:REGION --follow

# Get service URL
gcloud run services describe $env:SERVICE_NAME --region=$env:REGION --format='value(status.url)'
```

---

## Security Best Practices

✅ **DO:**
- Keep `service-account-key.json` in `.gitignore`
- Use specific IAM roles (least privilege)
- Enable Cloud Audit Logs
- Monitor service logs regularly
- Keep Docker image updated

❌ **DON'T:**
- Commit credentials to Git
- Use `--allow-unauthenticated` in production (remove if not needed)
- Share service account keys
- Run with excessive permissions

---

## Next Steps

1. ✅ Complete all steps above
2. 📊 Monitor performance and costs
3. 🔄 Set up CI/CD pipeline (optional)
4. 📝 Update DNS / custom domain (optional)
5. 🔐 Add API authentication layer (optional)

---

## Support & Resources

- **GCP Documentation**: https://cloud.google.com/run/docs
- **Vertex AI API**: https://cloud.google.com/vertex-ai/docs
- **Cloud Run Pricing**: https://cloud.google.com/run/pricing
- **GCP IAM Roles**: https://cloud.google.com/iam/docs/understanding-roles

---

**Estimated Time to Complete**: 15-20 minutes

Good luck with your deployment! 🚀
