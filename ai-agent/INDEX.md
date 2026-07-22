# 📚 Gherkin Test Case Generation Agent - Complete Package

## 🎯 What You Have

A **production-ready AI agent** that:
- ✅ Reads Swagger/OpenAPI specifications
- ✅ Generates Gherkin/Cucumber test cases (positive & negative)
- ✅ Accepts file uploads via web API
- ✅ Returns test cases in `.feature` format
- ✅ Deploys to Google Cloud Run in minutes
- ✅ Auto-scales to handle load
- ✅ Costs ~$0.50-2.50/month

---

## 🗂️ File Structure & Purpose

```
ai-agent/
│
├─ 📄 APPLICATION CORE
│  ├─ main.py                    # Core AI agent logic (CLI interface)
│  ├─ app.py                     # Flask REST API web server
│  ├─ requirements.txt           # Python dependencies
│  └─ example_swagger.yaml       # Sample API spec for testing
│
├─ 🐳 CONTAINERIZATION
│  ├─ Dockerfile                 # Docker image configuration
│  ├─ docker-compose.yml         # Local Docker Compose setup
│  └─ .gitignore                 # Git ignore rules
│
├─ 🚀 DEPLOYMENT AUTOMATION
│  ├─ deploy.py                  # Automated Python script (recommended)
│  └─ deploy.sh                  # Bash script for Mac/Linux
│
└─ 📚 DOCUMENTATION
   ├─ THIS FILE (INDEX)
   ├─ YOUR_DEPLOYMENT_STEPS.md   # ⭐ START HERE - Step-by-step for your GCP
   ├─ QUICKSTART.md              # 5-minute quick reference
   ├─ DEPLOYMENT_GUIDE.md        # Detailed comprehensive guide
   ├─ DEPLOYMENT_SUMMARY.md      # Visual overview & checklist
   └─ README.md                  # Full API documentation
```

---

## 🚀 Getting Started (Pick One Path)

### 🟢 PATH 1: Fastest - Automated Deployment (5 Minutes)

**Start here if you want to deploy RIGHT NOW with minimal effort**

```powershell
# Windows PowerShell
$env:PROJECT_ID = "your-gcp-project-id"
gcloud config set project $env:PROJECT_ID
python deploy.py
```

```bash
# Mac/Linux
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
chmod +x deploy.sh && ./deploy.sh
```

**Result:** Your service is live! You get a URL like:  
`https://gherkin-agent-xxx-uc.a.run.app`

---

### 🟡 PATH 2: Manual - Step-by-Step Control (15 Minutes)

**Start here if you want to understand each step or troubleshoot**

Read: `YOUR_DEPLOYMENT_STEPS.md` (specifically "METHOD B: Manual Step-by-Step")

---

### 🔵 PATH 3: Test Locally First (No GCloud Needed)

**Start here if you want to test without deploying yet**

```bash
# Requires: Docker + credentials
docker-compose up

# Test at http://localhost:5000
curl http://localhost:5000/health
```

---

## 📖 Documentation Guide

| File | Purpose | Read When |
|------|---------|-----------|
| **YOUR_DEPLOYMENT_STEPS.md** | Your personal deployment guide | **First** - Start deployment |
| **QUICKSTART.md** | 5-min reference | Quick lookups during deployment |
| **DEPLOYMENT_GUIDE.md** | Comprehensive manual | Manual deployment / troubleshooting |
| **DEPLOYMENT_SUMMARY.md** | Visual overview | Understanding the big picture |
| **README.md** | API documentation | After deployment - using the service |

---

## ⚡ Quick Command Reference

### Before Deployment
```powershell
# Check prerequisites
gcloud --version
docker --version

# List your GCP projects
gcloud projects list
```

### Deploy (Automated)
```powershell
# Run deployment script
python deploy.py

# Then follow the prompts
```

### After Deployment
```powershell
# Test health
curl https://your-service-url/health

# Upload file
curl -X POST -F "file=@swagger.yaml" \
  https://your-service-url/generate/upload

# View logs
gcloud run logs read gherkin-agent --follow

# Update code
docker build -t gcr.io/PROJECT/gherkin-agent .
docker push gcr.io/PROJECT/gherkin-agent
gcloud run deploy gherkin-agent --image=gcr.io/PROJECT/gherkin-agent
```

---

## 🎯 Your Next Steps (In Order)

### Step 1️⃣: Read Your Deployment Guide
→ Open: `YOUR_DEPLOYMENT_STEPS.md`

### Step 2️⃣: Run Deployment
```powershell
python deploy.py
```

### Step 3️⃣: Get Service URL
The script outputs your live URL

### Step 4️⃣: Test Your Service
```powershell
curl https://your-service-url/health
```

### Step 5️⃣: Start Using
Upload Swagger files → Generate test cases → Download results

---

## 🔍 Common Questions

### Q: How long does deployment take?
**A:** ~15 minutes total. Most time is Docker build (~5 min). Script does everything automatically.

### Q: How much will it cost?
**A:** ~$0.50-2.50/month for light usage (within free tier for most services).

### Q: Do I need to do anything manual?
**A:** Nope! Run `python deploy.py` and it handles everything.

### Q: Can I test locally first?
**A:** Yes! Run `docker-compose up` to test before deploying to GCloud.

### Q: What if something breaks?
**A:** Check logs with `gcloud run logs read gherkin-agent --follow`

### Q: How do I update the code?
**A:** Rebuild image, push, redeploy (takes ~5 minutes with script).

### Q: Can I delete it later?
**A:** Yes: `gcloud run services delete gherkin-agent`

---

## 📊 Architecture Overview

```
┌──────────────────┐
│   Your Machine   │
├──────────────────┤
│  Python Script   │
│  (deploy.py)     │
└────────┬─────────┘
         │
         ├─→ Builds Docker Image
         ├─→ Uploads to GCP Registry
         │
         ▼
┌──────────────────┐
│   Google Cloud   │
├──────────────────┤
│   Cloud Run      │ ◄─── Your Live Service
│   (Flask App)    │
└──────────────────┘
         │
         ├─→ Health Check: /health
         ├─→ Upload Tests: /generate/upload
         ├─→ Text Tests: /generate/text
         └─→ Download: /download/<file>
```

---

## 🛡️ Security

### What's Secured
✅ HTTPS enabled by default  
✅ Service account with minimal permissions  
✅ Credentials NOT in Git  
✅ Firewall protection included  

### What You Should Do
⚠️ Keep `service-account-key.json` private  
⚠️ Consider removing `--allow-unauthenticated` in production  
⚠️ Monitor usage in Cloud Console  

---

## 💡 Pro Tips

1. **Save Your Service URL**
   ```
   https://gherkin-agent-xxx-uc.a.run.app
   ```
   You'll need it for testing and sharing

2. **Set Up Logging Alert**
   Enables notifications if service has errors
   → Go to: https://console.cloud.google.com/monitoring

3. **Monitor Costs Monthly**
   → Go to: https://console.cloud.google.com/billing
   Set budget alert at ~$5 to be safe

4. **Update Code Easily**
   Make changes → Docker build → Push → Redeploy (~5 min)

5. **Share with Team**
   Just share the URL! Anyone can use it

---

## 🚨 Troubleshooting Map

| Problem | Solution | File |
|---------|----------|------|
| Deployment fails | Check logs | DEPLOYMENT_GUIDE.md |
| API returns 500 | Check `gcloud logs` | README.md |
| Service slow | Increase memory | DEPLOYMENT_GUIDE.md |
| Cost concerns | Check billing | DEPLOYMENT_SUMMARY.md |
| Update code | Rebuild & redeploy | QUICKSTART.md |

---

## 📞 Getting Help

### For Deployment Issues
1. Check logs: `gcloud run logs read gherkin-agent --follow`
2. Read: `YOUR_DEPLOYMENT_STEPS.md` (Troubleshooting section)
3. Read: `DEPLOYMENT_GUIDE.md` (Troubleshooting section)

### For API Usage Issues
1. Read: `README.md` (API Endpoints section)
2. Test with: `curl https://your-service-url/health`

### For GCP Issues
- Google Cloud Docs: https://cloud.google.com/run/docs
- Vertex AI Docs: https://cloud.google.com/vertex-ai/docs

---

## ✅ Success Checklist

- [ ] Read `YOUR_DEPLOYMENT_STEPS.md`
- [ ] Prerequisites installed (gcloud, docker)
- [ ] Ran deployment script
- [ ] Got service URL
- [ ] Health endpoint responds ✅
- [ ] Tested file upload
- [ ] Downloaded test results
- [ ] All working!

---

## 🎉 You're All Set!

You have everything needed to:
1. ✅ Deploy to Google Cloud Run
2. ✅ Test your AI agent
3. ✅ Monitor and manage the service
4. ✅ Update and scale as needed

---

## 🚀 Ready to Deploy?

### Choice A: Start Automated Deployment
```powershell
python deploy.py
```

### Choice B: Read Manual Steps First
→ Open: `YOUR_DEPLOYMENT_STEPS.md`

### Choice C: Test Locally First
```bash
docker-compose up
```

---

**👉 Recommended: Start with `YOUR_DEPLOYMENT_STEPS.md`**

It's tailored specifically for your GCP account and walks through everything step-by-step.

---

## 📝 Final Notes

- This is a **complete, production-ready** deployment package
- No additional configuration needed beyond your GCP project ID
- Estimated deployment time: **15 minutes**
- Estimated monthly cost: **$0.50-2.50**
- All documentation is in this folder
- All troubleshooting guides included

---

**Happy Deploying! 🚀**

Questions? Check the relevant documentation file listed above.
