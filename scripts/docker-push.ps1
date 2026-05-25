# Build and push Sunculture images to Docker Hub.
# Usage:
#   $env:DOCKERHUB_USER = "your-dockerhub-username"
#   .\scripts\docker-push.ps1

param(
    [string]$DockerUser = $env:DOCKERHUB_USER,
    [string]$Tag = "latest"
)

if (-not $DockerUser) {
    Write-Error "Set DOCKERHUB_USER to your Docker Hub username, e.g. `$env:DOCKERHUB_USER = 'myuser'"
    exit 1
}

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$apiImage = "${DockerUser}/sunculture-api:${Tag}"
$uiImage = "${DockerUser}/sunculture-ui:${Tag}"
$initImage = "${DockerUser}/sunculture-db-init:${Tag}"

Write-Host "Building images..."
docker build -t $apiImage --target api .
docker build -t $uiImage -f Dockerfile.ui .
docker build -t $initImage --target db-init .

Write-Host "Pushing to Docker Hub..."
docker push $apiImage
docker push $uiImage
docker push $initImage

Write-Host "Done."
Write-Host "  API:     $apiImage"
Write-Host "  UI:      $uiImage"
Write-Host "  DB init: $initImage"
