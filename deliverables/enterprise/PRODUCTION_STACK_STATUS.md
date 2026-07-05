# Production Stack Status

**Updated:** 2026-06-30  
**Version:** MESIE **1.2.0**  
**Protocol:** MESIE-PRODUCTION/1.2.0

---

## Persistent virtual servers (never-stop)

| Server | Port | Version | Role |
|--------|------|---------|------|
| Virtual Processor | **8750** | 1.2.0 | embed/match/compute/enterprise |
| Universal MCP | **8765** | 1.0.0 | super-tools + federation |
| Career Hub | **8767** | 1.0.0 | 1000 careers triple protocol |
| ML Recursive | — | 1.0.0 | corpus forge always-on |

**Start:** `.\Start-PersistentServers.ps1` or `.\Start-MESIEProduction.ps1`  
**State:** `deliverables/runtime/PERSISTENT_SERVERS_STATE.json`

---

## Running services

| Service | Status |
|---------|--------|
| **NOVA Runtime** | 70/70 careers, robotics satellite |
| **Virtual Processor** | HTTP `:8750` |
| **Universal MCP** | HTTP `:8765` — 12 super tools |
| **Career Hub** | HTTP `:8767` — 1000 careers |
| **MCP stdio** | 13 servers in `MCP_FULL_CONFIG.json` |

---

## Public GitHub forks (6)

| Repo | Careers |
|------|---------|
| mesie-career-enterprise | 200 |
| mesie-career-cybersecurity | 200 |
| mesie-career-business | 200 |
| mesie-career-engineering | 200 |
| mesie-career-architecture | 200 |
| mesie-career-universal | 1000 |

**Build:** `python scripts/build_career_mcp_forks.py`  
**Git init:** `.\scripts\init_career_fork_repos.ps1`  
**Publish:** `.\scripts\publish_career_forks_github.ps1`

---

## Showcase headline numbers

| Metric | Value |
|--------|-------|
| threat_p50_ms | **0.445** |
| fusion_dims | **256** |
| library_mb | **10.28** |
| careers | **1000** |
| mcp_servers | **13** |

---

## Production boot order

```powershell
.\Start-MESIEProduction.ps1      # full stack
.\Start-PersistentServers.ps1    # virtual servers only
.\Start-NovaRuntime.ps1          # 70 NOVA careers
.\Deploy-MCP-Servers.ps1         # register MCP clients
.\scripts\publish_career_forks_github.ps1
```