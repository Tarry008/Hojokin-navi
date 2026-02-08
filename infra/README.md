
## Artifact Registry

Use `infra/push-artifact-image.ps1` to build this repo's Docker image and push it to Artifact Registry.

### Prerequisites

- Docker Desktop is running.
- `gcloud` CLI is installed and authenticated (`gcloud auth login`).

### Example

```powershell
.\infra\push-artifact-image.ps1 `
  -ProjectId "YOUR_GCP_PROJECT_ID" `
  -Region "asia-northeast1" `
  -Repository "hojokin-navi" `
  -Image "backend"
```

The script will:

1. Set the active GCP project.
2. Configure Docker auth for Artifact Registry.
3. Create the Docker repository if missing.
4. Build from `./Dockerfile`.
5. Push the image.
