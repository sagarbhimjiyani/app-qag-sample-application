#!/bin/bash
# Automated Cloud Run Deployment Script for Linux/Mac

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "\n${BOLD}${BLUE}[STEP $1] $2${NC}"
    echo "============================================================"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
print_step 0 "Checking Prerequisites"

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    exit 1
fi
print_success "gcloud is installed"

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_success "Docker is installed"

# Get GCP configuration
print_step 1 "Configure GCP Project"

CURRENT_PROJECT=$(gcloud config get-value project)
echo "Current GCP project: $CURRENT_PROJECT"

read -p "Use current project? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Available projects:"
    gcloud projects list --format="value(project_id)" | sed 's/^/  - /'
    read -p "Enter project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
    print_success "Project set to: $PROJECT_ID"
else
    PROJECT_ID=$CURRENT_PROJECT
fi

read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

# Enable APIs
print_step 2 "Enable Required APIs"

APIs=(
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "aiplatform.googleapis.com"
    "cloudbuild.googleapis.com"
    "logging.googleapis.com"
)

for api in "${APIs[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api
done

print_success "All APIs enabled"

# Create service account
print_step 3 "Create Service Account"

SA_NAME="gherkin-agent-sa"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
    print_warning "Service account already exists: $SA_EMAIL"
else
    gcloud iam service-accounts create $SA_NAME \
        --display-name="Gherkin Agent Service Account"
    print_success "Service account created: $SA_EMAIL"
fi

# Grant roles
ROLES=(
    "roles/aiplatform.user"
    "roles/iam.serviceAccountUser"
    "roles/logging.logWriter"
)

for role in "${ROLES[@]}"; do
    echo "Granting $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
done

print_success "Service account configured with required roles"

# Build and push image
print_step 4 "Build and Push Docker Image"

IMAGE_NAME="gcr.io/$PROJECT_ID/gherkin-agent"

echo "Configuring Docker authentication..."
gcloud auth configure-docker gcr.io --quiet
print_success "Docker authentication configured"

echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .
print_success "Docker image built successfully"

echo "Pushing image to Container Registry..."
docker push $IMAGE_NAME
print_success "Image pushed to Container Registry"

# Deploy to Cloud Run
print_step 5 "Deploy to Cloud Run"

SERVICE_NAME="gherkin-agent"

echo "Deploying service to Cloud Run ($REGION)..."
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_NAME \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --service-account=$SA_EMAIL \
    --memory=2Gi \
    --cpu=2 \
    --timeout=60000 \
    --port=8080 \
    --quiet

print_success "Service deployed to Cloud Run"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

print_success "Service URL: $SERVICE_URL"

# Test deployment
print_step 6 "Test Deployment"

echo "Testing health endpoint..."
if curl -s "$SERVICE_URL/health" | grep -q "healthy"; then
    print_success "Health check passed"
else
    print_warning "Could not verify health check. Service might still be initializing."
fi

# Display next steps
print_step "NEXT" "Deployment Complete!"

cat << EOF

${BOLD}Your Service is Live!${NC}

Service URL: ${GREEN}$SERVICE_URL${NC}

${BOLD}Usage Examples:${NC}

1. Health Check:
   curl $SERVICE_URL/health

2. Upload Swagger File:
   curl -X POST -F "file=@example_swagger.yaml" $SERVICE_URL/generate/upload

3. Generate from Text:
   curl -X POST \\
     -H "Content-Type: application/json" \\
     -d '{"specification": "openapi: 3.0.0..."}' \\
     $SERVICE_URL/generate/text

4. Download Results:
   curl $SERVICE_URL/download/example_swagger_tests.feature

${BOLD}Monitoring:${NC}
View logs:
  gcloud run logs read gherkin-agent --limit=50

View in Cloud Console:
  https://console.cloud.google.com/run

${BOLD}Troubleshooting:${NC}
If service doesn't respond, check logs:
  gcloud run logs read gherkin-agent --follow

EOF

print_success "✅ Deployment Complete!"
