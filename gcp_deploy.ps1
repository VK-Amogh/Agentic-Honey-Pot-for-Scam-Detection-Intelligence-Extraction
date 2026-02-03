# Google Cloud Run Automated Deployment Script
# Usage: .\gcp_deploy.ps1 [ProjectId]

param (
    [string]$ProjectId = ""
)

$ErrorActionPreference = "Stop"

Write-Host "--- A G E N T I C   H O N E Y - P O T   D E P L O Y E R ---" -ForegroundColor Cyan

# 1. Check for GCloud SDK
if (-not (Get-Command "gcloud" -ErrorAction SilentlyContinue)) {
    Write-Error "Google Cloud SDK (gcloud) is not installed or not in PATH."
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# 2. Get Project ID
if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    Write-Host "You did not provide a Project ID."
    $activeProject = gcloud config get-value project 2>$null
    if (-not [string]::IsNullOrWhiteSpace($activeProject)) {
        Write-Host "Detected active project: $activeProject"
        $choice = Read-Host "Use this project? (Y/N)"
        if ($choice -eq 'Y' -or $choice -eq 'y') {
            $ProjectId = $activeProject
        }
    }
}

if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    $ProjectId = Read-Host "Please enter your Google Cloud Project ID"
}

if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    Write-Error "Project ID is required."
    exit 1
}

Write-Host "Using Project ID: $ProjectId" -ForegroundColor Yellow

# 3. Enable Services
Write-Host "Enabling Cloud Build and Cloud Run services..."
cmd /c "gcloud services enable cloudbuild.googleapis.com run.googleapis.com --project $ProjectId"

# 4. Build Container
$ImageName = "gcr.io/$ProjectId/scam-honey-pot"
Write-Host "Building Container Image: $ImageName"
cmd /c "gcloud builds submit --tag $ImageName --project $ProjectId"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed."
    exit 1
}

# 5. Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..."
cmd /c "gcloud run deploy scam-honey-pot --image $ImageName --platform managed --region us-central1 --allow-unauthenticated --project $ProjectId"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed."
    exit 1
}

Write-Host "--- D E P L O Y M E N T   S U C C E S S ! ---" -ForegroundColor Green
Write-Host "Your API is live at the URL above."
Write-Host "Don't forget to set your Secrets (API Key, Groq Key) in the Cloud Run Console:"
Write-Host "   https://console.cloud.google.com/run/detail/us-central1/scam-honey-pot/revisions"
