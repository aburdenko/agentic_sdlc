#!/bin/bash
set -e

# Load project variables from .env
PROJECT_ID="kallogjeri-project-345114"
SA_EMAIL="kallogjeri-project-345114@appspot.gserviceaccount.com"
KEY_FILE="/home/user/service_account.json"
PROJECT_NUMBER="273872083706"

echo "=== Step 1: Authenticating gcloud with Service Account ==="
if [ -f "$KEY_FILE" ]; then
    gcloud auth activate-service-account "$SA_EMAIL" --key-file="$KEY_FILE"
    gcloud config set project "$PROJECT_ID"
    echo "Successfully authenticated with service account: $SA_EMAIL"
else
    echo "ERROR: Service account key file not found at $KEY_FILE"
    exit 1
fi

echo "=== Step 2: Enabling Google Cloud APIs ==="
gcloud services enable \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com \
  discoveryengine.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com

echo "=== Step 3: Setting Up IAM Role Bindings ==="
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Compute Engine / Cloud Run SA Permissions
echo "Binding roles/aiplatform.user to Compute SA..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${COMPUTE_SA}" \
  --role="roles/aiplatform.user"

echo "Binding roles/logging.logWriter to Compute SA..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${COMPUTE_SA}" \
  --role="roles/logging.logWriter"

# Cloud Build SA Permissions
echo "Binding roles/run.invoker to Cloud Build SA..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${CLOUDBUILD_SA}" \
  --role="roles/run.invoker"

echo "=== Setup Completed Successfully ==="
