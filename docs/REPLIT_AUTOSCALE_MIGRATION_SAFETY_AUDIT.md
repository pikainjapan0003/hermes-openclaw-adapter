# Replit Autoscale Migration Safety Audit

**Date:** 2026-07-06
**Repo:** hermes-openclaw-adapter
**Auditor:** Claude Code (repo-side audit only)

---

## 1. Current Problem

Reserved VM compute hours are accruing cost while published.

The `hermes-openclaw-adapter` Replit deployment is configured as a Reserved VM, which means
compute hours accumulate continuously â even when the app is idle â as long as the deployment
is published.

## 2. Owner Observation

hermes-openclaw-adapter has high Reserved VM compute hours.

Stopping the Replit editor is not enough.
The Reserved VM deployment itself must be stopped or deleted.

## 3. Recommended Conclusion

Current repo should remain Dashboard preview / observation role only.
Reserved VM is not required for the current mock-only / read-only / dry-run architecture.
Autoscale is the preferred Replit deployment mode for published Dashboard preview.

The web server (`uvicorn app.main:app --host 0.0.0.0 --port 8000`) is a stateless FastAPI
process. It starts no Worker loop, no Hermes runtime, no OpenClaw runtime, and no connector
runtime at startup. It is safe to run under Autoscale, which only allocates compute when
HTTP requests are actively being served.

## 4. Repo-Side Findings

### .replit run command

```
run = "uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

Deployment run command:

```
["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### Web server characteristics

| Property | Value |
|---|---|
| Framework | FastAPI + uvicorn |
| Bind address | 0.0.0.0 |
| Port | 8000 (hardcoded; .replit maps 8000 â external 80) |
| PORT env var | Not currently used; acceptable for Autoscale via .replit port mapping |
| Background Worker started at app startup | NO |
| Hermes runtime started at app startup | NO |
| OpenClaw runtime started at app startup | NO |
| Connector runtime started at app startup | NO |
| Queue consumer loop in web process | NO |
| Background scheduler | NO |
| Long-polling bot | NO |
| Persistent WebSocket requirement | NO |
| Local state required for correctness | NO (queue DB is local data, not a runtime dependency) |
| Production DB write | NO (local SQLite only; mock/dry-run architecture) |

### Worker process

The queue Worker (`app.worker`) is a **separate process** started via `python -m app.worker`
or `scripts/start_worker.sh`. It is NOT started by the web server. It must NOT be run on
Replit. Replit is a remote observation dashboard only.

### Autoscale compatibility verdict

**COMPATIBLE.** The web server process is Dashboard-only, GET-dominant, stateless across
requests, and starts no background runtime at startup. Autoscale will correctly scale to
zero when idle, eliminating idle compute costs.

## 5. Replit Role Definition

```
Replit = remote observation dashboard
Replit is not Worker host
Replit is not Hermes runtime host
Replit is not OpenClaw runtime host
Replit is not connector runtime host
Replit is not production queue DB
```

## 6. Owner Manual Action Required â Replit UI Steps

1. Open Replit Deployments.
2. Find hermes-openclaw-adapter Reserved VM deployment.
3. Stop / Disable / Delete the Reserved VM deployment.
4. Create a new Autoscale deployment.
5. Use the existing web server run command.
6. Set machine power to the lowest usable tier.
7. Set max machines to 1.
8. Publish.
9. Verify /dashboard/system loads.
10. Verify no Worker / Hermes / OpenClaw / connector runtime is started.

**Important:** Stopping the editor is not enough.
The Reserved VM deployment itself must be stopped or deleted.

## 7. Safety Boundary Confirmation

Reserved VM shutdown is not runtime feature change.
Autoscale migration is not Hermes activation.
Autoscale migration is not OpenClaw activation.
Autoscale migration is not Worker execution.
Autoscale migration is not connector activation.
Dashboard publish is not execution permission.
Dashboard publish is not Blackboard write.
Dashboard publish is not queue write.
Dashboard publish is not audit trail write.
Replit remains a remote observation dashboard.
External side effects remain forbidden by default.

---

*This document is a repo-side audit only. No Replit API was called. No deployment was
modified. No runtime was activated. All findings are derived from static analysis of
`.replit`, `app/main.py`, `pyproject.toml`, and `requirements.txt`.*
