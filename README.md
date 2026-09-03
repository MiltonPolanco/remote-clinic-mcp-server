# Remote Clinic MCP Server

A stateless Streamable HTTP MCP server for the remote-server requirement of CC3067 Project 1. It provides a laboratory preparation catalog, checks preparation requirements, and returns the remote server time.

Academic demonstration project for CC3067 Redes using synthetic preparation policies.

## Tools

| Tool | Purpose |
| --- | --- |
| `list_lab_preparations` | Lists demonstration policies, optionally by category. |
| `get_lab_preparation` | Returns the policy for one test code. |
| `check_lab_preparation` | Reports unmet requirements from supplied preparation facts. |
| `get_remote_server_time` | Returns UTC and Guatemala timestamps plus the HTTP transport name. |

The MCP endpoint is `POST /mcp`; `GET /health` is available for platform checks. The server is stateless and returns JSON responses over Streamable HTTP.

## Local installation

```powershell
uv sync
uv run remote-clinic-mcp
```

Then connect an MCP Inspector or client to `http://localhost:8080/mcp`.

Run automated tests with:

```powershell
uv run pytest
```

## Container

```powershell
docker build -t remote-clinic-mcp .
docker run --rm -p 8080:8080 remote-clinic-mcp
```

## Google Cloud Run deployment

The following commands require the Google Cloud CLI, an authenticated account, and a project with Cloud Run enabled:

```powershell
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud run deploy remote-clinic-mcp `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --port 8080
```

Cloud Run prints the service URL. The MCP endpoint is that URL followed by `/mcp`. Verify it with:

```powershell
Invoke-RestMethod https://YOUR-SERVICE-URL/health
```

Set `REMOTE_MCP_URL` in the chatbot `.env`, for example:

```env
REMOTE_MCP_URL=https://remote-clinic-mcp-xxxxx-uc.a.run.app/mcp
```

For this academic demonstration the service allows unauthenticated requests for testing.

## Wireshark preparation

The deployed connection uses TLS over TCP port 443. Capture traffic while starting the chatbot and invoking `get_remote_server_time`. Wireshark can show the DNS, TCP, TLS, and HTTPS exchange, but the JSON-RPC body remains encrypted unless TLS key logging is configured.
