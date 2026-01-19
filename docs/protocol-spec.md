# Outcomes Protocol Specification

**Version:** 1.0.0-draft
**Status:** Draft
**Last Updated:** 2025-01-18

## Abstract

The Outcomes Protocol defines a standardized mechanism for requesting, pricing, delivering, and verifying AI-powered outcomes. It borrows auction/bidding mechanics from ad-tech (Meta Advantage+, Google Performance Max) to solve information asymmetry problems in outcome-based pricing, while providing hooks for future risk market integration.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Core Concepts](#2-core-concepts)
3. [Outcome Taxonomy](#3-outcome-taxonomy)
4. [Outcome Request](#4-outcome-request)
5. [Delivery Constraints](#5-delivery-constraints)
6. [Escalation Policy](#6-escalation-policy)
7. [Bid Strategies](#7-bid-strategies)
8. [Risk & Guarantee Framework](#8-risk--guarantee-framework)
9. [Delivery Response](#9-delivery-response)
10. [Conversions API](#10-conversions-api)
11. [Protocol Flow](#11-protocol-flow)

---

## 1. Introduction

### 1.1 Problem Statement

Current AI deployment faces several challenges:

| Problem | Current Approach | Protocol Solution |
|---------|------------------|-------------------|
| Information asymmetry | Buyers must reveal outcome value | Buyers express WTP through bid caps |
| Price formation | Bespoke negotiation | Systematic auction/bidding mechanics |
| No feedback loop | One-time pricing | Conversions API enables optimization |
| Non-scalable | Per-customer deals | Standardized outcomes create liquidity |
| Risk absorption | Providers self-insure | Risk market hooks enable trading |
| Latency ambiguity | Implicit expectations | Explicit delivery constraints |
| Failure handling | Ad-hoc escalation | Standardized handoff protocol |

### 1.2 Design Principles

1. **Standardization over customization**: Fixed outcome types enable price comparability
2. **Bid-based price discovery**: Market mechanics replace negotiation
3. **Feedback loops**: Conversions API creates accountability
4. **Latency as first-class**: Time constraints are explicit, not implicit
5. **Graceful degradation**: Human handoff is built into the protocol
6. **Risk market ready**: Hooks for future guarantee/insurance markets

### 1.3 Protocol Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      RISK MARKET LAYER                          │
│        (Future: Outcomes Contracts, Risk Pricing ρ_V(L_e))      │
├─────────────────────────────────────────────────────────────────┤
│                    OUTCOMES MARKETPLACE                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Outcome    │    │  Bid/Budget  │    │  Delivery    │       │
│  │   Catalog    │ →  │   Engine     │ →  │  Optimizer   │       │
│  │  (Taxonomy)  │    │  (Auction)   │    │  (Learning)  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                            ↑                                     │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Conversions API (cAPI)                   │       │
│  └──────────────────────────────────────────────────────┘       │
├─────────────────────────────────────────────────────────────────┤
│                    EXECUTION ENGINES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Claude Code  │  │   GPT-5 +    │  │   Gemini +   │           │
│  │  (Anthropic) │  │    Devin     │  │  Custom MCP  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  Models + harnesses bid directly on outcomes                    │
│  (Human fallback available for escalation)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Model-Level Bidding

The protocol uses **model-level bidding** rather than provider-company intermediaries:

**Why?**
- Provider companies are often thin wrappers around model APIs
- Direct model bidding removes unnecessary intermediary layers
- Model vendors can vertically integrate outcomes into their SDKs
- Cleaner market dynamics: models compete on capability, not brand

**Execution Engine = Model + Harness**
- **Model**: The AI model (Claude, GPT-5, Gemini, etc.)
- **Harness**: Tooling layer (Claude Code, Devin, custom MCP servers)
- Together they form an "execution engine" that can bid on outcomes

---

## 2. Core Concepts

### 2.1 Terminology

| Term | Definition |
|------|------------|
| **Outcome** | A discrete, verifiable result that delivers business value |
| **Outcome Type** | A category from the standardized taxonomy |
| **Outcome Request** | A structured specification for desired outcome |
| **Delivery Response** | The execution engine's response including outcome and metadata |
| **Conversion Event** | A signal indicating outcome success or failure |
| **Bid Strategy** | Rules governing price formation and budget allocation |
| **Delivery Constraint** | Time and resource bounds for outcome delivery |
| **Escalation Policy** | Rules for human handoff when AI cannot complete |
| **Guarantee Terms** | Risk allocation between buyer, execution engine, and market |
| **Execution Engine** | A model + harness combination that can bid on and execute outcomes |
| **Execution Preferences** | Buyer constraints on which engines can handle their request |

### 2.2 Participants

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    BUYER     │         │  MARKETPLACE │         │  EXECUTION   │
│              │         │              │         │    ENGINE    │
│ - Submits    │ ──────► │ - Matches    │ ──────► │ - Bids on    │
│   requests   │         │   requests   │         │   outcomes   │
│ - Sets bids  │         │ - Runs       │         │ - Executes   │
│ - Sets exec  │ ◄────── │   auctions   │ ◄────── │   work       │
│   preferences│         │ - Tracks     │         │ - Reports    │
│ - Reports    │         │   performance│         │   delivery   │
│   conversions│         │              │         │ - Escalates  │
└──────────────┘         └──────────────┘         └──────────────┘
                                │
                                ▼
                     ┌──────────────────┐
                     │   RISK MARKET    │
                     │   (Future)       │
                     │                  │
                     │ - Prices risk    │
                     │ - Trades         │
                     │   guarantees     │
                     │ - Settles claims │
                     └──────────────────┘
```

**Execution Engines** are model + harness combinations:
- **Claude Code** = Claude models + Claude Code harness (Anthropic)
- **GPT-5 + Devin** = GPT-5 + Devin code execution (OpenAI/Cognition)
- **Gemini + Custom MCP** = Gemini + custom MCP server harness (Google)

### 2.3 The Work Output Framework

Following Anjali Shrivastava's analysis, work output is characterized by two dimensions:

**Specification Entropy (SE)**: How much stable information required to bound acceptable outcomes
- Low SE: "Summarize this transcript" (clear input → clear output)
- High SE: "Design our product launch strategy" (requires extensive context)

**Verification Horizon (VH)**: Earliest moment success can be determined
- Short VH: Unit test passes immediately
- Long VH: Contract liability surfaces months later

|  | Short VH | Long VH |
|--|----------|---------|
| **Low SE** | **Tool** ✓ | **Template** |
| **High SE** | **Copilot** | **Consulting** |

The protocol enables deployment beyond the "Tool" quadrant by:
- Making SE explicit through structured context
- Making VH explicit through delivery constraints
- Pricing residual uncertainty through guarantee terms

### 2.4 Verification Models

The protocol supports two distinct verification models, determined by whether success can be objectively measured:

#### cAPI-Verified Outcomes

For outcomes where success can be directly measured and reported:

| Characteristic | Description |
|----------------|-------------|
| **Verification** | Success measured via cAPI signals (CSAT scores, test results, accuracy audits) |
| **Feedback Loop** | Continuous optimization based on verified outcomes |
| **Risk Premium** | Lower (uncertainty reduced by verification) |
| **Claim Model** | Standard failure = refund |
| **Examples** | `cs.resolve`, `code.review`, `code.fix`, `legal.review`, `medical.scribe` |

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Outcome    │     │  cAPI       │     │  Scoring &  │
│  Delivered  │ ──► │  Signals    │ ──► │  Optimization│
└─────────────┘     │  (measurable)│     └─────────────┘
                    └─────────────┘
```

**cAPI signals include:**
- Customer satisfaction surveys
- Resolution confirmation (no ticket reopen)
- Test suite pass/fail
- Accuracy audits by domain experts
- System-verifiable metrics (response time, format compliance)

#### Guarantee-Backed Outcomes

For outcomes where success requires judgment or has long verification horizons:

| Characteristic | Description |
|----------------|-------------|
| **Verification** | Success cannot be objectively measured at delivery time |
| **Assurance Model** | Buyer purchases guarantee coverage; provider prices risk |
| **Risk Premium** | Higher (uncertainty priced into guarantee) |
| **Claim Model** | Claims filed when defects discovered; evidence required |
| **Examples** | `legal.draft_nda`, `legal.draft_msa`, `code.generate` |

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Outcome    │     │  Guarantee  │     │  Claim      │
│  Delivered  │ ──► │  Period     │ ──► │  Window     │
└─────────────┘     │  (months/   │     │  (if defect │
                    │   years)    │     │   found)    │
                    └─────────────┘     └─────────────┘
```

**Why guarantee-backed?**
- "Is this NDA good?" requires an oracle (legal judgment)
- Defects may only surface when contract terms are exercised (months/years later)
- No objective cAPI signal exists at delivery time
- Assurance comes from the guarantee contract, not measurement

**Guarantee mechanics:**
1. Provider prices outcome including risk premium
2. Buyer receives guarantee coverage (e.g., 2-year claim window)
3. If defect discovered → file claim via cAPI with evidence
4. Valid claims trigger payout per guarantee terms

#### Choosing the Right Model

| If... | Then... |
|-------|---------|
| Success can be measured within days/weeks | Use cAPI-verified |
| Success requires domain expert judgment | Consider guarantee-backed |
| Verification horizon is months/years | Use guarantee-backed |
| Objective metrics exist (tests, surveys, audits) | Use cAPI-verified |
| "Good enough" is subjective | Use guarantee-backed |

---

## 3. Outcome Taxonomy

### 3.1 Standard Outcome Types

Like Meta's campaign objectives (Awareness, Traffic, Engagement, Leads, Sales), the protocol defines standardized outcome types:

#### Customer Service Outcomes
| Type ID | Name | Description | Verification |
|---------|------|-------------|--------------|
| `cs.resolve` | Resolve Inquiry | Fully resolve customer inquiry end-to-end | cAPI-verified |

*Note: Triage, deflection, and escalation are delivery mechanisms, not outcomes. The execution engine decides how to achieve resolution.*

#### Code Outcomes
| Type ID | Name | Description | Verification |
|---------|------|-------------|--------------|
| `code.review` | Code Review | Review PR for bugs, style, security | cAPI-verified |
| `code.fix` | Bug Fix | Diagnose and fix reported bug | cAPI-verified |
| `code.generate` | Code Generation | Generate code from specification | Guarantee-backed |

#### Legal Outcomes
| Type ID | Name | Description | Verification |
|---------|------|-------------|--------------|
| `legal.review` | Contract Review | Review and redline contract | cAPI-verified |
| `legal.summarize` | Contract Summary | Summarize key terms and risks | cAPI-verified |
| `legal.compare` | Contract Comparison | Compare versions, identify changes | cAPI-verified |
| `legal.draft_nda` | Draft NDA | Generate Non-Disclosure Agreement | Guarantee-backed |
| `legal.draft_msa` | Draft MSA | Generate Master Services Agreement | Guarantee-backed |
| `legal.draft_dpa` | Draft DPA | Generate Data Processing Agreement | Guarantee-backed |

#### Medical Outcomes
| Type ID | Name | Description | Verification |
|---------|------|-------------|--------------|
| `medical.scribe` | Clinical Scribing | Document patient encounter | cAPI-verified |
| `medical.code` | Medical Coding | Assign billing codes | cAPI-verified |
| `medical.summarize` | Record Summary | Summarize patient history | cAPI-verified |
| `medical.triage` | Clinical Triage | Assess urgency and route | cAPI-verified |

### 3.2 Custom Outcome Types

Providers may register custom outcome types following the naming convention:

```
{provider}.{vertical}.{action}
```

Example: `acme.insurance.claim_assessment`

Custom types must include:
- Unique type identifier
- Human-readable name and description
- Success criteria schema
- Suggested bid range
- Typical verification horizon

---

## 4. Outcome Request

### 4.1 Request Structure

```json
{
  "request_id": "string (UUID)",
  "outcome_type": "string (from taxonomy)",
  "verification_model": "capi | guarantee",
  "specification": {
    "objective": "string (what to achieve)",
    "constraints": ["string (must/must not)"],
    "preferences": ["string (should/should not)"]
  },
  "context_sources": [
    {
      "type": "inline | url | mcp_server | file_reference",
      "content": "...",
      "metadata": {}
    }
  ],
  "tools": [
    {
      "name": "string",
      "type": "mcp_server | api | function",
      "config": {}
    }
  ],
  "success_criteria": {
    "required": [
      {
        "metric": "string",
        "operator": "eq | gt | gte | lt | lte | contains | matches",
        "value": "any"
      }
    ],
    "optional": []
  },
  "delivery_constraints": { },
  "escalation_policy": { },
  "bid_strategy": { },
  "guarantee_terms": { },
  "metadata": {
    "buyer_id": "string",
    "correlation_id": "string",
    "tags": ["string"]
  }
}
```

**Note on `verification_model`**: This field is typically inferred from the outcome_type but can be explicitly set. cAPI-verified outcomes report success via measurable signals; guarantee-backed outcomes rely on guarantee coverage for assurance.

### 4.2 Specification Object

The specification captures what the buyer wants, structured to reduce ambiguity:

```json
{
  "specification": {
    "objective": "Review this vendor agreement and identify problematic clauses",
    "constraints": [
      "Must flag any unlimited liability clauses",
      "Must identify IP assignment terms",
      "Must not modify standard boilerplate without flagging"
    ],
    "preferences": [
      "Should prioritize data protection clauses",
      "Should use plain language in summaries"
    ]
  }
}
```

### 4.3 Context Sources

Context can be provided through multiple mechanisms:

| Type | Description | Example |
|------|-------------|---------|
| `inline` | Direct content in request | Contract text |
| `url` | Fetchable URL | Link to document |
| `mcp_server` | MCP server connection | Database access |
| `file_reference` | Reference to uploaded file | File ID from upload API |

```json
{
  "context_sources": [
    {
      "type": "inline",
      "content": "Contract text here...",
      "metadata": {
        "document_type": "vendor_agreement",
        "page_count": 12
      }
    },
    {
      "type": "mcp_server",
      "config": {
        "server": "company-policies",
        "tools": ["get_policy", "check_compliance"]
      }
    }
  ]
}
```

### 4.4 Tools

Tools the provider may use to complete the outcome:

```json
{
  "tools": [
    {
      "name": "jira",
      "type": "mcp_server",
      "config": {
        "server_url": "https://mcp.company.com/jira",
        "auth": { "type": "oauth", "token_ref": "jira_token" }
      },
      "permissions": ["read_issues", "add_comments", "update_status"]
    },
    {
      "name": "send_email",
      "type": "api",
      "config": {
        "endpoint": "https://api.company.com/email",
        "method": "POST"
      }
    }
  ]
}
```

### 4.5 Success Criteria

Explicit, measurable conditions for outcome success:

```json
{
  "success_criteria": {
    "required": [
      { "metric": "resolution_confirmed", "operator": "eq", "value": true },
      { "metric": "customer_satisfaction", "operator": "gte", "value": 4 },
      { "metric": "response_time_seconds", "operator": "lte", "value": 300 }
    ],
    "optional": [
      { "metric": "first_contact_resolution", "operator": "eq", "value": true },
      { "metric": "upsell_opportunity_identified", "operator": "eq", "value": true }
    ]
  }
}
```

### 4.6 Execution Preferences

Buyers can specify which execution engines are allowed to handle their requests:

```json
{
  "execution_preferences": {
    "allowed_engines": ["claude-code", "gpt-5-devin", "gemini-pro-*"],
    "blocked_engines": ["experimental-*", "beta-*"],
    "preferred_engine": "claude-code",
    "require_specific_engine": null,
    "capability_requirements": ["code_execution", "web_browsing"]
  }
}
```

| Field | Description |
|-------|-------------|
| `allowed_engines` | Whitelist of engines (supports wildcards). Empty = all allowed. |
| `blocked_engines` | Blacklist of engines (supports wildcards) |
| `preferred_engine` | Gets tiebreaker advantage in selection |
| `require_specific_engine` | If set, only this engine can handle the request |
| `capability_requirements` | Required capabilities the engine must have |

### 4.7 Selection Algorithm

When an outcome request arrives, the marketplace selects an execution engine:

1. **Filter by execution_preferences**: Remove blocked engines, keep only allowed
2. **Filter by bid constraints**: Remove engines that can't meet budget/latency
3. **Score by optimization_goal** from `bid_strategy`:
   - `cost`: Cheapest engine wins
   - `quality`: Highest historical success rate wins
   - `speed`: Fastest p95 latency wins
4. **Apply preference boost**: Preferred engine gets tiebreaker advantage
5. **Select**: Winning engine executes the outcome

This design cleanly separates:
- **Execution preferences**: "Who CAN do this?" (constraint)
- **Optimization goal**: "Who SHOULD do this?" (tiebreaker)

---

## 5. Delivery Constraints

### 5.1 Overview

Delivery constraints make latency and resource bounds explicit. This is critical because:
- Different use cases have vastly different time sensitivity
- Price should reflect delivery speed requirements
- Providers can optimize scheduling with clear expectations

### 5.2 Constraint Structure

```json
{
  "delivery_constraints": {
    "max_latency_seconds": 300,
    "latency_preference": "fastest | balanced | cost_optimized",
    "deadline": "2025-01-18T15:00:00Z",
    "deadline_type": "hard | soft",
    "max_compute_budget": {
      "tokens": 100000,
      "dollars": 5.00
    },
    "max_attempts": 3,
    "checkpoint_interval_seconds": 60
  }
}
```

### 5.3 Latency Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `fastest` | Minimize time to completion | Live customer chat |
| `balanced` | Optimize cost vs. speed | Standard support ticket |
| `cost_optimized` | Minimize cost, flexible timing | Batch processing |

### 5.4 Deadline Types

| Type | Behavior |
|------|----------|
| `hard` | Must complete by deadline or auto-escalate |
| `soft` | Best effort; late delivery acceptable but noted |

### 5.5 Checkpoints

For long-running outcomes, checkpoints provide progress visibility:

```json
{
  "checkpoint_interval_seconds": 60
}
```

Provider sends checkpoint events:
```json
{
  "event_type": "checkpoint",
  "request_id": "...",
  "timestamp": "...",
  "progress_percent": 45,
  "current_phase": "analyzing_clauses",
  "estimated_completion_seconds": 120
}
```

---

## 6. Escalation Policy

### 6.1 Overview

Escalation policy defines what happens when AI cannot complete the outcome. This is essential for:
- Graceful degradation to human handlers
- Clear handoff with context preservation
- Proper cost attribution for partial work

### 6.2 Policy Structure

```json
{
  "escalation_policy": {
    "enabled": true,
    "triggers": [
      {
        "type": "confidence_threshold",
        "threshold": 0.7,
        "action": "escalate"
      },
      {
        "type": "max_attempts",
        "attempts": 3,
        "action": "escalate"
      },
      {
        "type": "timeout",
        "seconds": 600,
        "action": "escalate"
      },
      {
        "type": "explicit_request",
        "patterns": ["speak to human", "talk to agent"],
        "action": "escalate"
      }
    ],
    "handoff": {
      "destination": {
        "type": "webhook | queue | email",
        "config": {}
      },
      "include_summary": true,
      "include_transcript": true,
      "include_context": true,
      "summary_format": "structured | narrative",
      "priority_mapping": {
        "high_value_customer": "urgent",
        "default": "normal"
      }
    },
    "partial_billing": {
      "enabled": true,
      "model": "percentage_complete | fixed_triage_fee | none"
    }
  }
}
```

### 6.3 Escalation Triggers

| Trigger Type | Description |
|--------------|-------------|
| `confidence_threshold` | AI confidence drops below threshold |
| `max_attempts` | Maximum retry attempts exceeded |
| `timeout` | Time limit exceeded |
| `explicit_request` | User explicitly requests human |
| `policy_violation` | Request violates guardrails |
| `out_of_scope` | Request outside defined capabilities |

### 6.4 Handoff Destinations

| Type | Description | Config |
|------|-------------|--------|
| `webhook` | HTTP POST to endpoint | `url`, `headers`, `auth` |
| `queue` | Message queue | `queue_name`, `connection` |
| `email` | Email to support team | `address`, `template` |
| `zendesk` | Zendesk ticket | `subdomain`, `group_id` |
| `intercom` | Intercom conversation | `workspace_id` |

### 6.5 Handoff Payload

When escalation occurs, the handoff includes:

```json
{
  "handoff_id": "hoff_abc123",
  "request_id": "req_xyz789",
  "escalation_reason": {
    "trigger": "confidence_threshold",
    "details": "Confidence dropped to 0.45 on billing dispute resolution"
  },
  "summary": {
    "issue": "Customer disputing $450 charge from 2024-12-15",
    "attempted_resolution": "Offered 20% credit, customer declined",
    "customer_sentiment": "frustrated",
    "recommended_action": "Review charge details, consider full refund"
  },
  "transcript": [...],
  "context": {
    "customer_id": "cust_123",
    "account_value": "high",
    "previous_escalations": 0
  },
  "work_completed": {
    "percentage": 60,
    "phases_completed": ["greeting", "issue_identification", "initial_offer"],
    "cost_incurred": 0.08
  },
  "priority": "urgent",
  "timestamp": "2025-01-18T10:30:00Z"
}
```

### 6.6 Partial Billing Models

When escalation occurs, partial work may be billed:

| Model | Description |
|-------|-------------|
| `percentage_complete` | Bill proportional to work completed |
| `fixed_triage_fee` | Fixed fee for triage regardless of outcome |
| `none` | No charge if escalated |

---

## 7. Bid Strategies

### 7.1 Strategy Types

Adapted from Meta advertising bid strategies:

| Strategy | Description |
|----------|-------------|
| **Highest volume** | Get the most results for your budget. |
| **Cost per result goal** | Aim for a certain cost per result while maximizing the volume of results. |
| **ROAS goal** | Aim for a certain return on spend while maximizing the value of results. |
| **Bid cap** | Set the highest you want to pay in any auction. |

### 7.2 Strategy Structure

```json
{
  "bid_strategy": {
    "type": "highest_volume | cost_per_result | roas_goal | bid_cap",
    "budget": {
      "total": 1000.00,
      "period": "daily | weekly | monthly | total",
      "currency": "USD"
    },
    "cost_per_result_goal": 5.00,
    "roas_goal": 5.0,
    "bid_cap": 10.00
  }
}
```

### 7.3 Strategy Behaviors

#### Highest Volume
```json
{
  "type": "highest_volume",
  "budget": { "total": 5000, "period": "monthly" }
}
```
Get the most results for your budget. The system optimizes to deliver as many successful outcomes as possible within your budget.

#### Cost Per Result Goal
```json
{
  "type": "cost_per_result",
  "cost_per_result_goal": 5.00
}
```
Aim for a certain cost per result while maximizing volume. Individual outcomes may cost more or less, but the average will trend toward your goal.

#### ROAS Goal
```json
{
  "type": "roas_goal",
  "roas_goal": 5.0,
  "outcome_value_source": "conversion_value"
}
```
Aim for a certain return on spend while maximizing the value of results. Requires reporting outcome values via the conversions API so the system can optimize for value, not just volume.

#### Bid Cap
```json
{
  "type": "bid_cap",
  "bid_cap": 10.00
}
```
Set the highest you want to pay in any auction. This gives you maximum control over costs but may limit delivery if your cap is too low for the market.

### 7.4 Auto-Bidding

When enabled, the system learns optimal bid levels:

```json
{
  "auto_bid": {
    "enabled": true,
    "learning_period_outcomes": 50,
    "adjustment_frequency": "hourly",
    "constraints": {
      "min_bid": 0.50,
      "max_bid": 20.00,
      "max_daily_adjustment_percent": 25
    }
  }
}
```

---

## 8. Risk & Guarantee Framework

### 8.1 Overview

The guarantee framework provides hooks for risk pricing and transfer. While full risk markets are a future extension, this framework enables:
- Explicit guarantee levels buyers can purchase
- Failure compensation terms
- Integration points for risk market pricing

### 8.2 Guarantee Terms Structure

```json
{
  "guarantee_terms": {
    "level": "none | basic | standard | full",
    "failure_coverage": {
      "enabled": true,
      "max_payout": 10000.00,
      "payout_conditions": [
        {
          "condition": "outcome_failed",
          "payout_type": "refund | fixed | actual_damages",
          "amount": 100.00
        }
      ],
      "claim_window_days": 30,
      "claim_process": "automatic | manual_review"
    },
    "risk_pricing": {
      "accept_market_price": true,
      "max_premium_percent": 15,
      "risk_factors": ["context_complexity", "verification_horizon"]
    },
    "sla": {
      "uptime_percent": 99.9,
      "response_time_p95_seconds": 5,
      "breach_compensation": "credit | refund"
    }
  }
}
```

### 8.3 Guarantee Levels

| Level | Coverage | Premium | Use Case |
|-------|----------|---------|----------|
| `none` | No guarantee | 0% | Internal/experimental |
| `basic` | Refund on failure | ~5% | Standard operations |
| `standard` | Refund + SLA credits | ~10% | Business critical |
| `full` | Actual damages up to cap | ~15-25% | High-stakes outcomes |

### 8.4 Failure Coverage

Defines compensation when outcomes fail:

```json
{
  "failure_coverage": {
    "enabled": true,
    "max_payout": 10000.00,
    "payout_conditions": [
      {
        "condition": "outcome_failed",
        "description": "Primary success criteria not met",
        "payout_type": "refund",
        "amount": null
      },
      {
        "condition": "outcome_caused_damage",
        "description": "AI error caused verifiable loss",
        "payout_type": "actual_damages",
        "amount_cap": 10000.00,
        "verification_required": true
      },
      {
        "condition": "sla_breach",
        "description": "Delivery exceeded deadline",
        "payout_type": "fixed",
        "amount": 50.00
      }
    ],
    "claim_window_days": 30,
    "claim_process": "automatic"
  }
}
```

### 8.5 Risk Market Integration (Future)

The `risk_pricing` field provides hooks for future risk market integration:

```json
{
  "risk_pricing": {
    "accept_market_price": true,
    "max_premium_percent": 15,
    "preferred_market": "outcomes_protocol_primary",
    "risk_factors": [
      "context_complexity",
      "verification_horizon",
      "provider_track_record",
      "outcome_type_history"
    ],
    "outcomes_contract": {
      "enabled": false,
      "settlement_oracle": "conversions_api",
      "contract_terms": {}
    }
  }
}
```

When risk markets are active:
- `accept_market_price`: Accept dynamically priced premiums
- `outcomes_contract`: Mint tradeable Outcomes Contract
- Premium reflects market's assessment of failure probability

### 8.6 The Risk-Effort Tradeoff

As described in the risk market theory, total cost combines production and risk:

```
TotalCost(e) = c(e) + ρ_V(L_e)
```

Where:
- `c(e)` = effort/compute cost
- `ρ_V(L_e)` = risk premium for residual uncertainty

The protocol optimizes effort where:
```
c'(e*) = -∂ρ_V(L_e)/∂e
```

In practice, this means providers automatically:
1. Query risk prices for different effort levels
2. Find the effort that minimizes total cost
3. Execute at that optimal effort level

---

## 9. Delivery Response

### 9.1 Response Structure

```json
{
  "response_id": "resp_abc123",
  "request_id": "req_xyz789",
  "status": "completed | failed | escalated | pending",
  "outcome": {
    "type": "cs.resolve",
    "result": {
      // Outcome-specific result data
    },
    "artifacts": [
      {
        "type": "document | code | message | structured_data",
        "content": "...",
        "metadata": {}
      }
    ]
  },
  "success_criteria_results": {
    "required": [
      { "metric": "resolution_confirmed", "value": true, "passed": true },
      { "metric": "customer_satisfaction", "value": 5, "passed": true }
    ],
    "optional": [
      { "metric": "first_contact_resolution", "value": true, "passed": true }
    ],
    "overall_success": true
  },
  "delivery_metrics": {
    "latency_seconds": 45,
    "tokens_used": 8500,
    "cost_breakdown": {
      "compute": 0.08,
      "risk_premium": 0.12,
      "total": 0.20
    },
    "effort_level": "standard",
    "checkpoints": []
  },
  "escalation": null,
  "guarantee": {
    "level": "standard",
    "coverage_active": true,
    "claim_eligible_until": "2025-02-17T10:30:00Z"
  },
  "execution_engine": {
    "engine_id": "claude-code-v2",
    "model": "claude-opus-4",
    "model_version": "claude-opus-4-20250115",
    "harness": "claude-code",
    "harness_version": "2.1.0",
    "vendor": "anthropic",
    "quality_score": 4.8
  },
  "timestamps": {
    "requested_at": "2025-01-18T10:29:15Z",
    "started_at": "2025-01-18T10:29:16Z",
    "completed_at": "2025-01-18T10:30:00Z"
  }
}
```

### 9.2 Status Values

| Status | Description |
|--------|-------------|
| `completed` | Outcome delivered, success criteria evaluated |
| `failed` | Outcome attempted but failed criteria |
| `escalated` | Handed off to human per escalation policy |
| `pending` | Still in progress (for async responses) |
| `cancelled` | Cancelled by buyer or system |

### 9.3 Escalated Response

When status is `escalated`:

```json
{
  "status": "escalated",
  "outcome": null,
  "escalation": {
    "handoff_id": "hoff_abc123",
    "reason": {
      "trigger": "confidence_threshold",
      "confidence": 0.45,
      "details": "Unable to resolve billing dispute with available tools"
    },
    "destination": {
      "type": "zendesk",
      "ticket_id": "12345"
    },
    "summary_provided": true,
    "transcript_provided": true,
    "work_completed_percent": 60
  },
  "delivery_metrics": {
    "cost_breakdown": {
      "compute": 0.05,
      "risk_premium": 0.00,
      "total": 0.05
    }
  }
}
```

---

## 10. Conversions API

### 10.1 Overview

The Conversions API (cAPI) enables outcome verification signals to flow from buyers back to the marketplace. This creates:
- Accountability for providers
- Optimization feedback loops
- Guarantee claim verification
- Risk model training data

### 10.2 Event Types

| Event | Description | Timing |
|-------|-------------|--------|
| `outcome.success` | Outcome verified successful | After VH |
| `outcome.failure` | Outcome verified failed | After VH |
| `outcome.partial` | Partial success | After VH |
| `guarantee.claim` | Requesting failure compensation | Within claim window |
| `feedback.rating` | Quality rating | Any time |
| `feedback.correction` | Correcting AI output | Any time |

### 10.3 Event Structure

```json
{
  "event_id": "evt_abc123",
  "event_type": "outcome.success | outcome.failure | guarantee.claim | ...",
  "event_time": "2025-01-18T10:30:00Z",
  "request_id": "req_xyz789",
  "response_id": "resp_abc123",
  "success": true,
  "success_criteria_results": {
    "resolution_confirmed": true,
    "customer_satisfaction": 5,
    "no_follow_up_needed": true
  },
  "outcome_value": {
    "amount": 50.00,
    "currency": "USD",
    "value_type": "revenue | cost_saved | custom"
  },
  "verification": {
    "method": "automatic | human_review | system_check",
    "verifier": "buyer | third_party | system",
    "evidence": {}
  },
  "metadata": {
    "correlation_id": "...",
    "tags": []
  }
}
```

### 10.4 Guarantee Claims

When an outcome fails and buyer has coverage:

```json
{
  "event_type": "guarantee.claim",
  "event_time": "2025-01-25T14:00:00Z",
  "request_id": "req_xyz789",
  "claim": {
    "type": "outcome_failed | outcome_caused_damage | sla_breach",
    "description": "Contract review missed liability clause that was later triggered",
    "requested_amount": 5000.00,
    "evidence": [
      {
        "type": "document",
        "description": "Contract showing missed clause",
        "url": "..."
      },
      {
        "type": "invoice",
        "description": "Legal fees incurred",
        "amount": 5000.00
      }
    ]
  }
}
```

### 10.5 Feedback Events

Even without claims, feedback improves the system:

```json
{
  "event_type": "feedback.rating",
  "request_id": "req_xyz789",
  "rating": {
    "overall": 4,
    "dimensions": {
      "accuracy": 5,
      "speed": 4,
      "communication": 3
    },
    "would_use_again": true
  },
  "comments": "Good resolution but explanation was too technical"
}
```

---

## 11. Protocol Flow

### 11.1 Standard Flow

```
┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌─────────┐
│  BUYER  │     │ MARKETPLACE │     │ PROVIDER │     │  BUYER  │
└────┬────┘     └──────┬──────┘     └────┬─────┘     └────┬────┘
     │                 │                 │                │
     │ 1. Submit       │                 │                │
     │ Outcome Request │                 │                │
     │ ───────────────►│                 │                │
     │                 │                 │                │
     │                 │ 2. Match &      │                │
     │                 │ Auction         │                │
     │                 │ ───────────────►│                │
     │                 │                 │                │
     │                 │ 3. Accept &     │                │
     │                 │ Execute         │                │
     │                 │ ◄───────────────│                │
     │                 │                 │                │
     │ 4. Delivery     │                 │                │
     │ Response        │                 │                │
     │ ◄───────────────│                 │                │
     │                 │                 │                │
     │                 │                 │     [Time passes - VH]
     │                 │                 │                │
     │                 │                 │ 5. Conversion  │
     │                 │                 │ Event          │
     │                 │ ◄───────────────┼────────────────│
     │                 │                 │                │
     │                 │ 6. Update       │                │
     │                 │ Models &        │                │
     │                 │ Settlement      │                │
     │                 │ ───────────────►│                │
     │                 │                 │                │
```

### 11.2 Escalation Flow

```
┌─────────┐     ┌─────────────┐     ┌──────────┐     ┌─────────┐
│  BUYER  │     │ MARKETPLACE │     │ PROVIDER │     │  HUMAN  │
└────┬────┘     └──────┬──────┘     └────┬─────┘     └────┬────┘
     │                 │                 │                │
     │ 1. Request      │                 │                │
     │ ───────────────►│ ───────────────►│                │
     │                 │                 │                │
     │                 │ 2. Trigger hit  │                │
     │                 │ (confidence/    │                │
     │                 │  timeout/etc)   │                │
     │                 │ ◄───────────────│                │
     │                 │                 │                │
     │                 │ 3. Handoff      │                │
     │                 │ ────────────────┼───────────────►│
     │                 │                 │                │
     │ 4. Escalated    │                 │                │
     │ Response        │                 │                │
     │ ◄───────────────│                 │                │
     │                 │                 │                │
     │                 │                 │ 5. Human       │
     │                 │                 │ Resolution     │
     │ ◄───────────────┼─────────────────┼────────────────│
     │                 │                 │                │
```

### 11.3 Guarantee Claim Flow

```
┌─────────┐     ┌─────────────┐     ┌────────────┐
│  BUYER  │     │ MARKETPLACE │     │ RISK POOL/ │
│         │     │             │     │ MARKET     │
└────┬────┘     └──────┬──────┘     └─────┬──────┘
     │                 │                  │
     │ 1. Claim        │                  │
     │ (within window) │                  │
     │ ───────────────►│                  │
     │                 │                  │
     │                 │ 2. Verify        │
     │                 │ Claim            │
     │                 │ ─────────────────│
     │                 │                  │
     │                 │ 3. If valid,     │
     │                 │ Release funds    │
     │                 │ ◄────────────────│
     │                 │                  │
     │ 4. Payout       │                  │
     │ ◄───────────────│                  │
     │                 │                  │
```

---

## Appendix A: Schema References

- Outcome Request: `schema/outcome-request.schema.json`
- Delivery Response: `schema/delivery-response.schema.json`
- Conversions API: `schema/conversions-api.schema.json`

## Appendix B: Vertical Guides

- Customer Service: `docs/verticals/customer-service.md`
- Code Review: `docs/verticals/code-review.md`
- Legal: `docs/verticals/legal.md`
- Medical Scribing: `docs/verticals/medical-scribing.md`

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **cAPI** | Conversions API - feedback mechanism |
| **SE** | Specification Entropy - complexity of defining task |
| **VH** | Verification Horizon - time until success knowable |
| **WTP** | Willingness To Pay |
| **ROAS** | Return On Ad Spend (adapted: Return On Outcome Spend) |
| **Outcomes Contract** | Tradeable instrument representing outcome risk |
| **ρ_V(L_e)** | Risk price at horizon V for loss L at effort e |
