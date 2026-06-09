---
name: gemini-enterprise-adk-deployment
description: Guide and scripts for deploying an Agent Development Kit (ADK) agent to Gemini Enterprise. Use this when you need to deploy an agent to Cloud Run and register it with Gemini Enterprise, or need information on prerequisites like OAuth setup and IAM permissions.
---

# Gemini Enterprise ADK Deployment

This skill provides a complete workflow for deploying an AI agent to a platform like Cloud Run and registering it with Gemini Enterprise. 

## Prerequisites & Setup

Before running the deployment script, ensure the following steps have been completed:

1. **Install & Authenticate gcloud CLI**: 
   Ensure you have the Google Cloud SDK installed and are authenticated.
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
2. **Google Cloud Project**: Have a project with billing enabled.
3. **Enable APIs**:
   ```bash
   gcloud services enable \
     aiplatform.googleapis.com \
     cloudbuild.googleapis.com \
     artifactregistry.googleapis.com \
     run.googleapis.com \
     logging.googleapis.com \
     discoveryengine.googleapis.com \
     storage.googleapis.com \
     iam.googleapis.com
   ```
4. **Grant IAM Permissions**:
   Ensure your Compute Engine default service account has the required roles.
   ```bash
   # Replace with your PROJECT_ID and SERVICE_ACCOUNT_EMAIL
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/artifactregistry.reader"
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/logging.logWriter"
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/aiplatform.user"
   # Replace with your PROJECT_ID and redacted PII
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:<REDACTED_PII>" \
     --role="roles/run.invoker"
   ```

## Configure OAuth 2.0

Navigate to the Google Auth Platform Clients page in the Google Cloud Console.
1. Create a new OAuth client of type "Web Application".
2. Add the following to "Authorized redirect URIs":
   - `https://vertexaisearch.cloud.google.com/oauth-redirect`
   - `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html`
3. Note down the **Client ID** and **Client Secret**.

## Deploy to Cloud Run

Use the provided deployment script to build and deploy your agent's code to Cloud Run. The script is available at `scripts/deploy_to_cloud_run.sh`.

Usage:
```bash
cp /usr/lib/node_modules/@google/gemini-cli/bundle/builtin/gemini-enterprise-adk-deployment/scripts/deploy_to_cloud_run.sh ./deploy.sh
chmod +x deploy.sh
./deploy.sh <YOUR_PROJECT_ID> <SERVICE_NAME> [MODEL_NAME]
```
Note the **Agent URL** printed at the end of the deployment.

## Create Authorization Resource in Gemini Enterprise

This registers your OAuth client details with Gemini Enterprise. Replace the placeholders with your specific details:
- `YOUR_PROJECT_NUMBER`: Your Google Cloud Project Number.
- `YOUR_LOCATION`: The location of your Gemini Enterprise instance (e.g., global, us).
- `YOUR_AUTH_ID`: A unique ID for this authorization config (e.g., my-gemini-agent-auth).
- `YOUR_OAUTH_CLIENT_ID`: The Client ID from the OAuth step.
- `YOUR_OAUTH_CLIENT_SECRET`: The Client Secret from the OAuth step.

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: YOUR_PROJECT_ID" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/YOUR_PROJECT_NUMBER/locations/YOUR_LOCATION/authorizations?authorizationId=YOUR_AUTH_ID" \
  -d '{
    "name": "projects/YOUR_PROJECT_NUMBER/locations/YOUR_LOCATION/authorizations/YOUR_AUTH_ID",
    "serverSideOauth2": {
      "clientId": "YOUR_OAUTH_CLIENT_ID",
      "clientSecret": "YOUR_OAUTH_CLIENT_SECRET",
      "authorizationUri": "https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_OAUTH_CLIENT_ID&redirect_uri=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fstatic%2Foauth%2Foauth.html&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email&include_granted_scopes=true&response_type=code&access_type=offline&prompt=consent",
      "tokenUri": "https://oauth2.googleapis.com/token"
    }
  }'
```
Copy the full **AUTHORIZATION_RESOURCE_NAME** returned (e.g., `projects/12345/locations/global/authorizations/my-gemini-agent-auth`).

## Register the Agent with Gemini Enterprise

Finally, register your deployed agent. You'll need your Gemini Enterprise Engine ID, found in the Cloud Console UI.

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: YOUR_PROJECT_ID" \
  "https://discoveryengine.googleapis.com/v1alpha/projects/YOUR_PROJECT_NUMBER/locations/YOUR_LOCATION/collections/default_collection/engines/YOUR_ENGINE_ID/assistants/default_assistant/agents" \
  -d '{
    "displayName": "YOUR_DISPLAY_NAME",
    "description": "YOUR_DESCRIPTION",
    "a2aAgentDefinition": {
      "jsonAgentCard": "{\"provider\":{\"organization\":\"MyOrg\",\"url\":\"YOUR_AGENT_URL\"},\"name\":\"YOUR_DISPLAY_NAME\",\"description\":\"YOUR_DESCRIPTION\",\"capabilities\":{},\"defaultInputModes\":[\"text/plain\"],\"defaultOutputModes\":[\"text/plain\"],\"skills\":[{\"description\":\"Chat with the Gemini agent.\",\"examples\":[\"Hello, world!\"],\"id\":\"chat\",\"name\":\"Chat Skill\",\"tags\":[\"chat\"]}],\"version\":\"1.0.0\"}"
    },
    "authorization_config": {
      "agent_authorization": "YOUR_AUTHORIZATION_RESOURCE_NAME"
    }
  }'
```
After these steps, your agent should be discoverable and usable within the Gemini Enterprise Agent Gallery.
