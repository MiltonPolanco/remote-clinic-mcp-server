# Remote Clinic MCP Server

Stateless Model Context Protocol server developed for the remote-server requirement of the CC3067 Networks project. It publishes a laboratory preparation catalog, evaluates preparation conditions, and returns the server time over Streamable HTTP.

All policies are synthetic and intended only for academic demonstration.

## Features

- Streamable HTTP MCP transport.
- Stateless JSON responses suitable for multiple clients.
- Laboratory policies for GLU, HBA1C, CHOL, CREA, and TSH.
- Validation of fasting, alcohol, and strenuous-exercise preparation.
- Health endpoint for local containers and cloud platforms.
- Automated catalog and time-zone tests.

## Deployed service

| Purpose | URL |
| --- | --- |
| MCP endpoint | `https://remote-clinic-mcp-915028065261.us-central1.run.app/mcp` |
| Health endpoint | `https://remote-clinic-mcp-915028065261.us-central1.run.app/health` |

The MCP endpoint accepts protocol requests with `POST`. The health endpoint accepts `GET` and returns:

```json
{"status": "ok", "server": "remote-clinic-mcp"}
```

The Cloud Run service is public for the classroom interoperability demonstration. It does not store patient data and does not require an API key.

## MCP specification

### Tools

| Tool | Required parameters | Optional parameters | Result |
| --- | --- | --- | --- |
| `list_lab_preparations` | None | `category: string` | Matching test policies and count. |
| `get_lab_preparation` | `test_code: string` | None | Complete preparation policy for one code. |
| `check_lab_preparation` | `test_code: string` | `fasting_hours: number`, `hours_since_alcohol: number`, `hours_since_strenuous_exercise: number` | Readiness flag, unmet requirements, and the applicable policy. |
| `get_remote_server_time` | None | None | UTC time, Guatemala time, and transport name. |

`test_code` is normalized to uppercase. Negative hour values and unknown codes return MCP tool errors. Omitting a preparation value does not satisfy a nonzero requirement.

### Demonstration policies

| Code | Test | Minimum fasting | Avoid alcohol | Avoid strenuous exercise |
| --- | --- | ---: | ---: | ---: |
| `GLU` | Fasting glucose | 8 h | 24 h | 12 h |
| `HBA1C` | Glycated hemoglobin | 0 h | 0 h | 0 h |
| `CHOL` | Lipid profile | 9 h | 24 h | 12 h |
| `CREA` | Creatinine | 0 h | 0 h | 24 h |
| `TSH` | Thyroid-stimulating hormone | 0 h | 0 h | 0 h |

Water is allowed for every policy in the demonstration catalog.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop for container testing
- Google Cloud CLI and a billing-enabled project for deployment

## Local installation

Install the locked environment and start the server:

```powershell
uv sync --locked
uv run remote-clinic-mcp
```

The local MCP endpoint is `http://localhost:8080/mcp` and the health endpoint is `http://localhost:8080/health`. Set `PORT` before startup to use another port.

Run the automated tests with:

```powershell
uv run pytest
```

## Container

Build and run the same image used by the cloud service:

```powershell
docker build -t remote-clinic-mcp .
docker run --rm -p 8080:8080 remote-clinic-mcp
```

In another terminal, verify it:

```powershell
Invoke-RestMethod "http://localhost:8080/health"
```

## Google Cloud Run deployment

Select a Google Cloud project and enable the required services:

```powershell
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

Deploy from the repository directory:

```powershell
gcloud run deploy remote-clinic-mcp `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --port 8080 `
  --min-instances 0 `
  --max-instances 1 `
  --cpu 1 `
  --memory 512Mi `
  --concurrency 20 `
  --timeout 300
```

The zero minimum allows the service to scale down when idle. Verify the URL printed by Cloud Run by appending `/health`.

## Client configuration

The console host reads the complete MCP URL from its `.env` file:

```env
REMOTE_MCP_URL=https://remote-clinic-mcp-915028065261.us-central1.run.app/mcp
```

Any Streamable HTTP MCP client can use the same `/mcp` endpoint. A representative tool scenario is:

1. Call `get_remote_server_time` and verify `transport` is `streamable-http`.
2. Call `get_lab_preparation` with `{"test_code": "GLU"}`.
3. Call `check_lab_preparation` with `{"test_code": "GLU", "fasting_hours": 10, "hours_since_alcohol": 30, "hours_since_strenuous_exercise": 14}`.
4. Verify that `ready_according_to_demo_policy` is `true`.

## Wireshark capture

Cloud Run communicates over TLS on TCP port 443. A capture of a complete MCP session contains:

1. DNS resolution for the Cloud Run hostname.
2. TCP connection establishment.
3. TLS negotiation and encrypted application data.
4. MCP initialization through JSON-RPC.
5. `notifications/initialized` synchronization.
6. `tools/list` discovery.
7. `tools/call` requests and their responses.

The JSON-RPC body remains encrypted unless the client exports TLS session keys and Wireshark is configured to use that key log. Session key files should be kept private and must not be published in the repository.

## Source structure

```text
src/remote_clinic_mcp/
  catalog.py   Preparation policies and validation
  server.py    MCP tools, health route, and HTTP entry point
tests/
Dockerfile
```

## Security and cost controls

- The service is stateless and stores no personal or clinical records.
- The catalog contains demonstration data only.
- Cloud Run is limited to one instance and can scale to zero.
- The public endpoint is appropriate only for this academic demonstration.
- After evaluation, disable or delete the service if it is no longer needed.
