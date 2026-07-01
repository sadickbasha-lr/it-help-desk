#!/usr/bin/env bash
# deploy.sh — Build, push, and deploy the IT Help Desk ADK Agent to Cloud Run.
#
# Usage
# -----
#   chmod +x deploy.sh
#   ./deploy.sh
#
# Prerequisites
# -------------
#   - gcloud CLI installed and authenticated (`gcloud auth login`)
#   - Docker installed and running
#   - Artifact Registry repository already exists (see README.md)
#
# Required environment variables (set before running this script)
# ---------------------------------------------------------------
#   PROJECT_ID        — your GCP project ID
#   REGION            — GCP region, e.g. us-central1
#   API_BASE_URL      — deployed Phase 2 Cloud Run URL
#   GOOGLE_API_KEY    — Gemini API key (leave empty to use ADC)
#
# Example
# -------
#   export PROJECT_ID=my-project
#   export REGION=us-central1
#   export API_BASE_URL=https://it-help-desk-api-xxxxx-uc.a.run.app
#   export GOOGLE_API_KEY=AIza...
#   ./deploy.sh

set -euo pipefail

: "${PROJECT_ID:?'PROJECT_ID is not set'}"
: "${REGION:?'REGION is not set'}"
: "${API_BASE_URL:?'API_BASE_URL is not set'}"

REPO_NAME="${REPO_NAME:-it-help-desk}"
IMAGE_NAME="${IMAGE_NAME:-it-help-desk-agent}"
SERVICE_NAME="${SERVICE_NAME:-it-help-desk-agent}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "==> Configuring Docker auth for Artifact Registry..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo "==> Building agent image: ${FULL_IMAGE}"
docker build -t "${FULL_IMAGE}" "$(dirname "$0")"

echo "==> Pushing image to Artifact Registry..."
docker push "${FULL_IMAGE}"

echo "==> Deploying agent to Cloud Run..."
ENV_VARS="API_BASE_URL=${API_BASE_URL}"
if [[ -n "${GOOGLE_API_KEY:-}" ]]; then
  ENV_VARS="${ENV_VARS},GOOGLE_API_KEY=${GOOGLE_API_KEY}"
fi
if [[ -n "${GOOGLE_CLOUD_PROJECT:-}" ]]; then
  ENV_VARS="${ENV_VARS},GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}"
fi

gcloud run deploy "${SERVICE_NAME}" \
  --image "${FULL_IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "${ENV_VARS}"

echo ""
echo "==> Done! Agent service URL:"
gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --format "value(status.url)"
