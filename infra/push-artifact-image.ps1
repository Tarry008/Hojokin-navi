param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [string]$Region = "asia-northeast1",
    [string]$Repository = "hojokin-navi",
    [string]$Image = "backend",
    [string]$Tag = ""
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    & $Command @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Args -join ' ')"
    }
}

if ([string]::IsNullOrWhiteSpace($Tag)) {
    $Tag = Get-Date -Format "yyyyMMdd-HHmmss"
}

$RegistryHost = "$Region-docker.pkg.dev"
$ImageUri = "$RegistryHost/$ProjectId/$Repository/$Image`:$Tag"

Write-Host "Project    : $ProjectId"
Write-Host "Region     : $Region"
Write-Host "Repository : $Repository"
Write-Host "Image URI  : $ImageUri"

Invoke-Checked -Command "gcloud" -Args @("config", "set", "project", $ProjectId)
Invoke-Checked -Command "gcloud" -Args @("auth", "configure-docker", $RegistryHost, "--quiet")

& gcloud artifacts repositories describe $Repository --location $Region *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Repository '$Repository' not found in '$Region'. Creating..."
    Invoke-Checked -Command "gcloud" -Args @(
        "artifacts", "repositories", "create", $Repository,
        "--repository-format=docker",
        "--location=$Region",
        "--description=Docker images for Hojokin Navi"
    )
}

Invoke-Checked -Command "docker" -Args @("build", "-t", $ImageUri, ".")
Invoke-Checked -Command "docker" -Args @("push", $ImageUri)

Write-Host ""
Write-Host "Done."
Write-Host "Pushed image: $ImageUri"
