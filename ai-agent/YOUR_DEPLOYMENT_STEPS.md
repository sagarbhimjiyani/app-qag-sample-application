# 🎯 YOUR STEP-BY-STEP GCP DEPLOYMENT

Complete guide specifically for YOUR personal GCP account.

---

## 📋 Pre-Flight Checklist

Before you start, verify:

```powershell
# Check gcloud is installed
gcloud --version

# Check docker is installed
docker --version

# Check you're logged into GCP
gcloud auth list

# See your GCP projects
gcloud projects list
```

---

## 🚀 STEP-BY-STEP DEPLOYMENT

### STEP 1: Navigate to Project Directory

```powershell
# Windows
cd C:\Users\sagar\IdeaProjects\app-qag-sample-application\ai-agent

# Mac/Linux
cd ~/IdeaProjects/app-qag-sample-application/ai-agent
```

### STEP 2: Set Your Project ID

Replace `YOUR_PROJECT_ID` with your actual GCP project ID (e.g., `my-project-123456`)

**Windows PowerShell:**
```powershell
$env:PROJECT_ID = "YOUR_PROJECT_ID"
gcloud config set project $env:PROJECT_ID

# Verify
gcloud config get-value project
```

**Mac/Linux Bash:**
```bash
export PROJECT_ID="YOUR_PROJECT_ID"
gcloud config set project $PROJECT_ID

# Verify
gcloud config get-value project
```

### STEP 3: Choose Your Deployment Method

#### 🟢 METHOD A: Fully Automated (5 Minutes) - RECOMMENDED

**Windows:**
```powershell
python deploy.py
```

**Mac/Linux:**
```bash
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Ask which project to use
2. Ask for region (default: us-central1)
3. Enable all APIs automatically
4. Create service account
5. Build and push Docker image
6. Deploy to Cloud Run
7. Test the deployment
8. Output your service URL ✅

**Then skip to STEP 5: Verify Deployment**

---

#### 🟡 METHOD B: Manual Step-by-Step (15 Minutes)

If you prefer to do it manually or the script has issues:

**Step 3a: Enable APIs**

```powershell
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable logging.googleapis.com

# Wait for all to be enabled (~2-3 minutes)
```

**Step 3b: Create Service Account**

```powershell
$SA_NAME = "gherkin-agent-sa"
$SA_EMAIL = "$SA_NAME@$env:PROJECT_ID.iam.gserviceaccount.com"

# Create
gcloud iam service-accounts create $SA_NAME `
    --display-name="Gherkin Agent Service Account"

# Grant roles
gcloud projects add-iam-policy-binding $env:PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/aiplatform.user" --quiet

gcloud projects add-iam-policy-binding $env:PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/iam.serviceAccountUser" --quiet

gcloud projects add-iam-policy-binding $env:PROJECT_ID `
    --member="serviceAccount:$SA_EMAIL" `
    --role="roles/logging.logWriter" --quiet
```

**Step 3c: Build and Push Docker Image**

```powershell
# Setup
$IMAGE_NAME = "gcr.io/$env:PROJECT_ID/gherkin-agent"

# Configure Docker
gcloud auth configure-docker gcr.io --quiet

# Build (takes 2-3 minutes)
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Push to registry (takes 1-2 minutes)
echo "Pushing to Container Registry..."
docker push $IMAGE_NAME

# Verify
echo "Image pushed successfully!"
```

**Step 3d: Deploy to Cloud Run**

```powershell
$SERVICE_NAME = "gherkin-agent"
$REGION = "us-central1"

echo "Deploying to Cloud Run..."

gcloud run deploy $SERVICE_NAME `
    --image=$IMAGE_NAME `
    --region=$REGION `
    --platform=managed `
    --allow-unauthenticated `
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$env:PROJECT_ID" `
    --service-account=$SA_EMAIL `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --port=5000 `
    --quiet

echo "✅ Service deployed!"
```

**Step 3e: Get Service URL**

```powershell
$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --format="value(status.url)"

echo "Service URL: $SERVICE_URL"
```

Save this URL - you'll use it to test the service!

---

### STEP 4: First-Time Wait (If Using Automated Script)

After running the script, wait for:
1. **APIs to enable** (~2 min) - You'll see log messages
2. **Docker build** (~3-5 min) - This is normal, takes time
3. **Upload to registry** (~1-2 min) - Pushing image
4. **Cloud Run deployment** (~1-2 min) - Final setup

Total wait: **8-12 minutes**

---

### STEP 5: Verify Deployment ✅

Once deployment completes, you'll get a **Service URL** like:
```
https://gherkin-agent-xxx-uc.a.run.app
```

Test it immediately:

```powershell
$SERVICE_URL = "https://your-service-url-here"

# 1. Health check
curl "$SERVICE_URL/health"

# Should respond:
# {"status": "healthy", "service": "Gherkin Test Case Generation Agent"}
```

If you see the health response → **Deployment Successful! ✅**

---

### STEP 6: Test with Your First API Call

#### Test 1: Upload and Process Swagger File

```powershell
$SERVICE_URL = "https://your-service-url-here"

# Upload the example swagger file
curl -X POST `
    -F "file=@example_swagger.yaml" `
    "$SERVICE_URL/generate/upload"

# You'll get back:
# {
#   "status": "success",
#   "test_cases": "Feature: User Management API...",
#   "result_file": "example_swagger_tests.feature",
#   "download_url": "/download/example_swagger_tests.feature"
# }
```

#### Test 2: Download Generated Tests

```powershell
# Download the generated feature file
curl "$SERVICE_URL/download/example_swagger_tests.feature" `
    -o "my_generated_tests.feature"

# View the results
Get-Content my_generated_tests.feature
```

#### Test 3: Generate from Text

```powershell
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
    -d "{`"specification`": `"$spec`"}" `
    "$SERVICE_URL/generate/text"
```

---

### STEP 7: Monitor Your Service

#### View Real-Time Logs

```powershell
# Stream logs (Ctrl+C to stop)
gcloud run logs read gherkin-agent --follow

# Or view recent logs
gcloud run logs read gherkin-agent --limit=50
```

#### Check Service Details

```powershell
# Get full service info
gcloud run services describe gherkin-agent --region=us-central1

# Get just the URL
gcloud run services describe gherkin-agent `
    --region=us-central1 `
    --format="value(status.url)"
```

#### View in Cloud Console

Open in browser:
```
https://console.cloud.google.com/run
```

---

## 🎯 What You Can Do Now

### 1. Use as REST API

```powershell
# From any tool/language/script:
$url = "https://your-service-url/generate/upload"

# Upload any Swagger/OpenAPI file
# Get back Gherkin test cases
# Download results
```

### 2. Integrate into Workflows

- Use in CI/CD pipelines
- Call from other services
- Schedule regular generations
- Automate test creation

### 3. Share with Team

```powershell
# Anyone with internet can access:
https://your-service-url

# Share the URL, they can use the API immediately
```

### 4. Monitor & Scale

```powershell
# View metrics in Cloud Console
# Set up alerts
# Monitor costs
# View logs anytime
```

---

## 🔄 After Deployment: Common Tasks

### Update Code (After Making Changes)

```powershell
# 1. Rebuild image
docker build -t gcr.io/$env:PROJECT_ID/gherkin-agent .

# 2. Push to registry
docker push gcr.io/$env:PROJECT_ID/gherkin-agent

# 3. Redeploy (uses latest image automatically)
gcloud run deploy gherkin-agent `
    --image=gcr.io/$env:PROJECT_ID/gherkin-agent `
    --region=us-central1 --quiet
```

### Increase Service Capacity

```powershell
# If you need more power:
gcloud run services update gherkin-agent `
    --region=us-central1 `
    --memory=4Gi `
    --cpu=4
```

### Check Costs

```
https://console.cloud.google.com/billing
```

Expected: **$0.50-2.50/month** for light usage

### Delete Service (Clean Up)

```powershell
# If you no longer need it:
gcloud run services delete gherkin-agent --region=us-central1 --quiet
```

---

## 🆘 Troubleshooting

### Issue: "gcloud: command not found"
**Solution:** Install Google Cloud SDK
- Windows: https://cloud.google.com/sdk/docs/install-gcloud-on-windows
- Mac: `brew install --cask google-cloud-sdk`
- Linux: https://cloud.google.com/sdk/docs/install-gcloud-on-linux

### Issue: "API not enabled" error
**Solution:** Run enable APIs command again
```powershell
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Issue: Docker build fails
**Solution:** Make sure Docker is running
```powershell
docker version
# If not running, start Docker Desktop first
```

### Issue: "Permission denied" pushing image
**Solution:** Reconfigure Docker
```powershell
gcloud auth configure-docker gcr.io --quiet
```

### Issue: Service returns 500 errors
**Solution:** Check logs
```powershell
gcloud run logs read gherkin-agent --follow
```

Common causes:
- Missing environment variables
- Service account permissions
- Insufficient memory

### Issue: Service responding very slowly
**Solution:** Increase memory/CPU
```powershell
gcloud run services update gherkin-agent `
    --memory=4Gi --cpu=4 --region=us-central1
```

---

## 📞 Need Help?

1. **Check the logs:**
   ```powershell
   gcloud run logs read gherkin-agent --follow
   ```

2. **Read documentation:**
   - `DEPLOYMENT_GUIDE.md` - Detailed guide
   - `README.md` - API documentation
   - `QUICKSTART.md` - Quick reference

3. **Google Cloud Support:**
   - https://cloud.google.com/support

---

## 🎉 Success Indicators

Your deployment is successful when:

✅ Script completes without errors  
✅ You receive a Service URL  
✅ Health endpoint responds with `"status": "healthy"`  
✅ File upload returns test cases  
✅ You can download generated tests  
✅ Logs appear in `gcloud run logs read`  

---

## 📊 Your Service is Now:

✅ **Live** - Available 24/7  
✅ **Secure** - HTTPS enabled  
✅ **Scalable** - Auto-scales 0-100 instances  
✅ **Monitored** - Logs & metrics available  
✅ **Cost-Effective** - $0.50-2.50/month  

---

## 🚀 Ready?

### Choose Your Path:

**Option A: Fastest (5 minutes)**
```powershell
python deploy.py
```

**Option B: Manual Control (15 minutes)**
Follow "METHOD B: Manual Step-by-Step" above

**Option C: Test Locally First (No GCloud needed)**
```powershell
docker-compose up
# Test at http://localhost:5000
```

---

**Let's deploy your agent! 🚀**
