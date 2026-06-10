# Paper 04 — Release-Safe Architecture Diagram

**Authority:** `INTERNAL_RESEARCH`  
**Claim boundary:** `repo_verified_architecture`  
**Posture:** Design proposal / experimental framework — not production security

## System overview

```mermaid
flowchart TB
    subgraph Theater["Mission World (Theater Week Engine)"]
        TW[Theater Tick]
        SW[Swarm Coordinator]
        MP[Mission Planner]
        TW --> SW
        TW --> MP
    end

    subgraph Spacetime["Simulated Spacetime Substrate"]
        AG[Spatial Agents]
        ZN[Geometric Zones]
        FC[Force / Influence Field]
        AG --- ZN
        AG --- FC
    end

    subgraph Tiers["Three-Tier Signal Classification"]
        COOP[Cooperative]
        SHAD[Shadow]
        HOST[Hostile]
    end

    subgraph Route["Operational Routing"]
        IE[Intelligence Engine]
        WE[Workflow Engine]
        QS[Quarantine Sink]
    end

    TW -->|classify trust / jam / threat| Tiers
    Tiers -->|route policy| Route
    TW -->|advance tick| Spacetime
    COOP --> IE
    SHAD --> WE
    HOST --> QS
    QS --> ZN
```

## Zone geometry (release-safe names)

```mermaid
flowchart LR
    subgraph Ops["Operational"]
        CC[command_core]
        FO[field_ops]
    end
    subgraph Inspect["Inspection"]
        SB[shadow_buffer]
        HS[honeypot_surface]
    end
    subgraph Contain["Containment"]
        QH[quarantine_hold]
    end
    CC --> FO
    FO --> SB
    SB --> QH
    HS -.-> SB
```

## Tick pipeline

```mermaid
sequenceDiagram
    participant W as Week Engine
    participant B as Spacetime Bridge
    participant C as Classifier
    participant R as Router
    participant S as Substrate

    W->>B: mission tick context
    B->>C: trust + jam + threat
    C-->>B: cooperative / shadow / hostile
    B->>R: zone policy lookup
    R-->>B: route decision + engine target
    B->>S: advance spatial tick
    S-->>B: zone occupancy + quarantine trace
    B-->>W: spacetime fields on TickRecord
```

## Public claim box

| Element | Safe to publish | Withhold pending IP review |
|---------|-----------------|---------------------------|
| Three-tier model | Yes | Exact threshold tuning |
| Zone role names | Yes (generic) | Operational codenames |
| Agent coordinates | Illustrative only | Live deployment geometry |
| Routing targets | Engine class names | Strategic failover paths |
| Force analogy | Conceptual | Calibrated constants |

## Reproduce

```bash
python scripts/run_spacetime_suite.py
python scripts/run_mission_world_week.py --days 7
```