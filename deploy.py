#!/usr/bin/env python3
"""
Automated Cloud Run Deployment Script
Deploys the Gherkin Agent to Google Cloud Run with one command
"""

import subprocess
import sys
import os
import json
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(step_num, title):
    """Print a formatted step header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[STEP {step_num}] {title}{Colors.END}")
    print("=" * 60)


def print_success(msg):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_warning(msg):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_error(msg):
    """Print error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def run_command(cmd, description=""):
    """Execute a shell command and handle errors"""
    if description:
        print(f"\n→ {description}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Command failed: {cmd}")
            print(result.stderr)
            return None
        return result.stdout.strip()
    except Exception as e:
        print_error(f"Error executing command: {e}")
        return None


def check_prerequisites():
    """Check if gcloud and docker are installed"""
    print_step(0, "Checking Prerequisites")
    
    tools = {'gcloud': 'gcloud --version', 'docker': 'docker --version'}
    
    for tool, cmd in tools.items():
        output = run_command(cmd)
        if output:
            print_success(f"{tool} is installed")
        else:
            print_error(f"{tool} is NOT installed. Please install it first.")
            sys.exit(1)


def get_gcp_config():
    """Get GCP configuration from user"""
    print_step(1, "Configure GCP Project")
    
    # Get current project
    current_project = run_command('gcloud config get-value project')
    
    print(f"Current GCP project: {current_project}")
    
    use_current = input("\nUse current project? (y/n): ").lower().strip()
    
    if use_current != 'y':
        projects_output = run_command('gcloud projects list --format="value(project_id)"')
        if projects_output:
            print("\nAvailable projects:")
            for proj in projects_output.split('\n'):
                print(f"  - {proj}")
        
        project_id = input("\nEnter project ID: ").strip()
        run_command(f'gcloud config set project {project_id}')
        print_success(f"Project set to: {project_id}")
    else:
        project_id = current_project
    
    region = input("\nEnter deployment region (default: us-central1): ").strip() or "us-central1"
    
    return project_id, region


def enable_apis(project_id):
    """Enable required Google Cloud APIs"""
    print_step(2, "Enable Required APIs")
    
    apis = [
        'run.googleapis.com',
        'containerregistry.googleapis.com',
        'aiplatform.googleapis.com',
        'cloudbuild.googleapis.com',
        'logging.googleapis.com'
    ]
    
    for api in apis:
        print(f"Enabling {api}...")
        run_command(f'gcloud services enable {api}')
    
    print_success("All APIs enabled")


def create_service_account(project_id):
    """Create and configure service account"""
    print_step(3, "Create Service Account")
    
    sa_name = "gherkin-agent-sa"
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    
    # Check if service account exists
    existing = run_command(
        f'gcloud iam service-accounts describe {sa_email} 2>/dev/null',
        "Checking for existing service account..."
    )
    
    if not existing:
        run_command(
            f'gcloud iam service-accounts create {sa_name} '
            '--display-name="Gherkin Agent Service Account"',
            "Creating service account..."
        )
        print_success(f"Service account created: {sa_email}")
    else:
        print_warning(f"Service account already exists: {sa_email}")
    
    # Grant roles
    roles = [
        'roles/aiplatform.user',
        'roles/iam.serviceAccountUser',
        'roles/logging.logWriter'
    ]
    
    for role in roles:
        print(f"Granting {role}...")
        run_command(
            f'gcloud projects add-iam-policy-binding {project_id} '
            f'--member="serviceAccount:{sa_email}" '
            f'--role="{role}" --quiet'
        )
    
    print_success("Service account configured with required roles")
    return sa_email


def build_and_push_image(project_id):
    """Build and push Docker image"""
    print_step(4, "Build and Push Docker Image")
    
    image_name = f"gcr.io/{project_id}/gherkin-agent"
    
    # Configure Docker authentication
    print("Configuring Docker authentication...")
    run_command('gcloud auth configure-docker gcr.io --quiet')
    print_success("Docker authentication configured")
    
    # Build image
    print(f"\nBuilding Docker image: {image_name}...")
    output = run_command(f'docker build -t {image_name} .', "Building image...")
    
    if output is None:
        print_error("Docker build failed")
        sys.exit(1)
    
    print_success("Docker image built successfully")
    
    # Push image
    print(f"\nPushing image to Container Registry...")
    output = run_command(f'docker push {image_name}', "Pushing image...")
    
    if output is None:
        print_error("Docker push failed")
        sys.exit(1)
    
    print_success("Image pushed to Container Registry")
    return image_name


def deploy_to_cloud_run(project_id, region, image_name, sa_email):
    """Deploy to Cloud Run"""
    print_step(5, "Deploy to Cloud Run")
    
    service_name = "gherkin-agent"
    
    deploy_cmd = (
        f'gcloud run deploy {service_name} '
        f'--image={image_name} '
        f'--region={region} '
        f'--platform=managed '
        f'--allow-unauthenticated '
        f'--set-env-vars="GOOGLE_CLOUD_PROJECT={project_id}" '
        f'--service-account={sa_email} '
        f'--memory=2Gi '
        f'--cpu=2 '
        f'--timeout=3600 '
        f'--port=8080 '
        f'--quiet'
    )
    
    print(f"Deploying service to Cloud Run ({region})...")
    output = run_command(deploy_cmd, "Deploying...")
    
    if output is None:
        print_error("Cloud Run deployment failed")
        sys.exit(1)
    
    print_success("Service deployed to Cloud Run")
    
    # Get service URL
    url_output = run_command(
        f'gcloud run services describe {service_name} '
        f'--region={region} '
        f'--format="value(status.url)"',
        "Retrieving service URL..."
    )
    
    return url_output


def test_deployment(service_url):
    """Test the deployed service"""
    print_step(6, "Test Deployment")
    
    print(f"Testing health endpoint: {service_url}/health")
    
    try:
        import requests
        response = requests.get(f"{service_url}/health", timeout=10)
        
        if response.status_code == 200:
            print_success("Health check passed")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_warning(f"Health check returned status {response.status_code}")
            return False
    except ImportError:
        print_warning("requests library not installed. Skipping automatic test.")
        print(f"\nManually test with: curl {service_url}/health")
        return True
    except Exception as e:
        print_warning(f"Could not test endpoint: {e}")
        print(f"Service might still be initializing. Check logs with:")
        print(f"  gcloud run logs read gherkin-agent")
        return True


def display_next_steps(service_url):
    """Display next steps"""
    print_step("NEXT", "Next Steps & Usage Examples")
    
    print(f"""
{Colors.BOLD}Your Service is Live!{Colors.END}

Service URL: {Colors.GREEN}{service_url}{Colors.END}

{Colors.BOLD}Usage Examples:{Colors.END}

1. {Colors.BOLD}Health Check:{Colors.END}
   curl {service_url}/health

2. {Colors.BOLD}Upload Swagger File:{Colors.END}
   curl -X POST -F "file=@example_swagger.yaml" {service_url}/generate/upload

3. {Colors.BOLD}Generate from Text:{Colors.END}
   curl -X POST \\
     -H "Content-Type: application/json" \\
     -d '{{"specification": "openapi: 3.0.0..."}}' \\
     {service_url}/generate/text

4. {Colors.BOLD}Download Results:{Colors.END}
   curl {service_url}/download/example_swagger_tests.feature

{Colors.BOLD}Monitoring & Management:{Colors.END}

View logs:
  gcloud run logs read gherkin-agent --limit=50

View metrics:
  gcloud run services describe gherkin-agent

Update service (after code changes):
  docker build -t gcr.io/YOUR_PROJECT/gherkin-agent . && \\
  docker push gcr.io/YOUR_PROJECT/gherkin-agent && \\
  gcloud run deploy gherkin-agent --image=gcr.io/YOUR_PROJECT/gherkin-agent

View in Cloud Console:
  https://console.cloud.google.com/run

{Colors.BOLD}Estimated Costs:{Colors.END}
- Cloud Run: ~$0.40/month (free tier: 2M requests)
- Vertex AI: ~$1.50 per million tokens
- Total: ~$2-5/month for light usage

{Colors.BOLD}Troubleshooting:{Colors.END}
If service doesn't respond, check logs:
  gcloud run logs read gherkin-agent --follow
""")


def main():
    """Main deployment flow"""
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("=" * 60)
    print("  Gherkin Agent - Cloud Run Deployment")
    print("=" * 60)
    print(f"{Colors.END}\n")
    
    try:
        # Step 0: Check prerequisites
        check_prerequisites()
        
        # Step 1: Get GCP config
        project_id, region = get_gcp_config()
        
        # Step 2: Enable APIs
        enable_apis(project_id)
        
        # Step 3: Create service account
        sa_email = create_service_account(project_id)
        
        # Step 4: Build and push image
        image_name = build_and_push_image(project_id)
        
        # Step 5: Deploy to Cloud Run
        service_url = deploy_to_cloud_run(project_id, region, image_name, sa_email)
        
        # Step 6: Test deployment
        test_deployment(service_url)
        
        # Display next steps
        display_next_steps(service_url)
        
        print_success("\n✅ Deployment Complete!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
