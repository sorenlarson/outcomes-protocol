# Outcomes Protocol

A marketplace-based pricing system for AI outcomes that borrows auction/bidding mechanics from ad-tech (Meta Advantage+, Google Performance Max) to solve information asymmetry problems in outcome-based pricing.

## The Problem

Current AI deployment faces several challenges:

| Problem | Current Approach | Outcomes Protocol Solution |
|---------|------------------|---------------------------|
| Information asymmetry | Buyers must reveal outcome value | Buyers express WTP through bid caps |
| Price formation | Bespoke negotiation | Systematic auction/bidding mechanics |
| No feedback loop | One-time pricing | Conversions API enables optimization |
| Non-scalable | Per-customer deals | Standardized outcomes create liquidity |
| Risk absorption | Providers self-insure | Risk market hooks enable trading |
| Latency ambiguity | Implicit expectations | Explicit delivery constraints |
| Failure handling | Ad-hoc escalation | Standardized handoff protocol |

## Key Concepts

### Outcome Types (Taxonomy)

Like Meta's campaign objectives, the protocol defines standardized outcome types:

- **Customer Service**: `cs.resolve` (single outcome - customer service is reactive, you don't know what the customer will need)
- **Code**: `code.review`, `code.fix`
- **Legal**: `legal.review`, `legal.summarize`, `legal.compare`, `legal.draft_nda`, `legal.draft_msa`, `legal.draft_dpa`
- **Medical**: `medical.scribe` (clinical documentation from patient encounters)

### Verification Models

Outcomes use one of two verification models:

| Model | Description | Examples |
|-------|-------------|----------|
| **cAPI-Verified** | Success measured via cAPI signals (ticket closed, no reopen, no escalation) | `cs.resolve` |
| **Guarantee-Backed** | Quality requires expertise; assurance via guarantee contract | `code.*`, `legal.*`, `medical.scribe` |

For cAPI-verified outcomes, the buyer reports success/failure via the Conversions API based on observable events. For guarantee-backed outcomes, the agent affirms completion, you pay on delivery, and if defects are discovered within the claim window, you file a claim via the Claims API.

### Bid Strategies

Mapped from advertising concepts:

| Meta Concept | Outcomes Equivalent | Description |
|--------------|---------------------|-------------|
| Bid cap | Max outcome price | Never pay more than $X per outcome |
| Cost cap | Target cost | Average cost target per outcome |
| ROAS goal | Return on spend | Target value-to-cost ratio |
| Highest volume | Maximize throughput | Most outcomes within budget |

### Conversions API (cAPI)

Server-side feedback mechanism enabling:
- Outcome verification signals
- Guarantee claim processing
- Provider scoring and optimization
- Risk model training

### Delivery Constraints

First-class latency specification:
- `max_latency_seconds`: Hard time limit
- `latency_preference`: `fastest`, `balanced`, `cost_optimized`
- `deadline` + `deadline_type`: Absolute deadlines

### Escalation Policy

Built-in human handoff:
- Configurable triggers (confidence, timeout, explicit request)
- Structured handoff with summary and context
- Partial billing models

### Guarantee Terms

Risk market hooks:
- Guarantee levels: `none`, `basic`, `standard`, `full`
- Failure coverage with claim windows
- SLA commitments
- Future: tradeable Outcomes Contracts

## Project Structure

```
outcomes-protocol/
├── README.md                          # This file
├── docs/
│   ├── protocol-spec.md              # Full protocol specification
│   ├── conversions-api.md            # cAPI specification
│   ├── bid-strategies.md             # Bid strategy deep dive
│   ├── ui-flows.md                   # UI flow documentation
│   └── verticals/
│       ├── customer-service.md       # CS vertical guide
│       ├── code-review.md            # Code review vertical
│       ├── legal.md                  # Legal vertical
│       └── medical-scribing.md       # Medical scribing vertical
├── schema/
│   ├── outcome-request.schema.json   # Outcome request format
│   ├── conversions-api.schema.json   # cAPI event format
│   ├── delivery-response.schema.json # Provider response format
│   └── examples/
│       ├── customer-service-request.json
│       ├── code-review-request.json
│       ├── legal-request.json
│       ├── legal-draft-nda-request.json  # Guarantee-backed example
│       └── medical-scribing-request.json
├── prototype/
│   ├── index.html                    # Interactive UI prototype
│   ├── styles.css                    # Styling
│   └── app.js                        # Interactive logic
└── sdk/
    ├── README.md                     # SDK integration guide
    ├── outcomes.yml                  # Example .claude/outcomes.yml
    ├── outcomes_provider.py          # Provider harness
    └── examples/
        ├── customer_service_outcome.py
        └── code_review_outcome.py
```

## Quick Start

### 1. View the Interactive Prototype

Open `prototype/index.html` in a browser to explore:
- Outcome type selection (like Meta campaign objectives)
- Configuration wizard for context, tools, success criteria
- Bid strategy interface with real-time cost estimation
- Performance dashboard mockup

### 2. Explore the Schema

Review the JSON schemas in `schema/` to understand the request/response formats:

```json
{
  "outcome_type": "cs.resolve",
  "specification": {
    "objective": "Resolve customer inquiry about order status"
  },
  "success_criteria": {
    "required": [
      { "metric": "resolution_confirmed", "operator": "eq", "value": true },
      { "metric": "customer_satisfaction", "operator": "gte", "value": 4 }
    ]
  },
  "delivery_constraints": {
    "max_latency_seconds": 300,
    "latency_preference": "fastest"
  },
  "escalation_policy": {
    "enabled": true,
    "triggers": [
      { "type": "confidence_threshold", "threshold": 0.7, "action": "escalate" }
    ]
  },
  "bid_strategy": {
    "type": "target_cost",
    "bid_amount": 0.45
  },
  "guarantee_terms": {
    "level": "basic"
  }
}
```

### 3. SDK Integration

For Claude Agent SDK integration, see `sdk/README.md`:

```python
from outcomes_provider import OutcomesProvider

# Load configuration
provider = OutcomesProvider.from_config(".claude/outcomes.yml")

# Execute an outcome
response = await provider.execute(request)

# Response includes:
# - status: completed, failed, escalated
# - outcome: result artifacts
# - success_criteria_results: criterion evaluations
# - delivery_metrics: cost, latency, tool calls
# - guarantee: coverage status
```

## Architecture

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

### Model-Level Bidding

The protocol uses **model-level bidding** rather than provider-company intermediaries:

- **Execution Engine** = Model + Harness (e.g., Claude Code = Claude + Claude Code harness)
- Models compete directly on outcomes based on capability and price
- Buyers can specify **execution preferences** to constrain which engines handle their requests
- The `bid_strategy.optimization_goal` (cost/quality/speed) determines the tiebreaker

### Execution Preferences
```json
{
  "execution_preferences": {
    "allowed_engines": ["claude-code", "gpt-5-devin"],
    "blocked_engines": ["experimental-*"],
    "preferred_engine": "claude-code",
    "capability_requirements": ["code_execution"]
  }
}
```

## Key Features

### Delivery Constraints
```json
{
  "delivery_constraints": {
    "max_latency_seconds": 300,
    "latency_preference": "fastest",
    "deadline": "2025-01-20T17:00:00Z",
    "deadline_type": "hard",
    "max_compute_budget": {
      "tokens": 50000,
      "dollars": 5.00
    }
  }
}
```

### Escalation Policy
```json
{
  "escalation_policy": {
    "enabled": true,
    "triggers": [
      { "type": "confidence_threshold", "threshold": 0.7, "action": "escalate" },
      { "type": "explicit_request", "patterns": ["speak to human"], "action": "escalate" },
      { "type": "timeout", "seconds": 600, "action": "escalate" }
    ],
    "handoff": {
      "destination": { "type": "zendesk", "config": {} },
      "include_summary": true,
      "include_transcript": true
    }
  }
}
```

### Guarantee Terms
```json
{
  "guarantee_terms": {
    "level": "standard",
    "failure_coverage": {
      "enabled": true,
      "max_payout": 10000.00,
      "payout_conditions": [
        { "condition": "outcome_failed", "payout_type": "refund" },
        { "condition": "outcome_caused_damage", "payout_type": "actual_damages" }
      ],
      "claim_window_days": 30
    },
    "risk_pricing": {
      "accept_market_price": true,
      "max_premium_percent": 15
    }
  }
}
```

## Documentation

| Document | Description |
|----------|-------------|
| [Protocol Specification](docs/protocol-spec.md) | Complete protocol definition |
| [Conversions API](docs/conversions-api.md) | Feedback mechanism specification |
| [Bid Strategies](docs/bid-strategies.md) | Pricing strategy deep dive |
| [UI Flows](docs/ui-flows.md) | User interface documentation |
| [Customer Service Guide](docs/verticals/customer-service.md) | CS implementation guide |
| [Code Review Guide](docs/verticals/code-review.md) | Code review implementation |
| [Legal Guide](docs/verticals/legal.md) | Legal vertical implementation |
| [Medical Scribing Guide](docs/verticals/medical-scribing.md) | Healthcare implementation |

## Comparison to Current Approaches

### vs. Vertical AI Companies (Harvey, Intercom)
- **Current**: Each company builds trust, pricing, guarantees independently
- **Protocol**: Standardized outcomes enable marketplace dynamics, risk trading

### vs. API Pricing (Per-token)
- **Current**: Buyer bears all outcome risk, no guarantees
- **Protocol**: Outcome-based with configurable guarantees and escalation

### vs. Manual Warranties (Intercom $1M Guarantee)
- **Current**: Bespoke pricing, company-specific
- **Protocol**: Market-based risk pricing, portable across providers

## Future Extensions

### Risk Markets
The `guarantee_terms.risk_pricing.outcomes_contract` field provides hooks for future risk market integration:

```json
{
  "outcomes_contract": {
    "enabled": true,
    "settlement_oracle": "conversions_api",
    "contract_terms": {
      "loss_cap": 10000,
      "verification_horizon_days": 30
    }
  }
}
```

This enables:
- Tradeable Outcomes Contracts (prediction market style)
- Dynamic risk pricing: ρ_V(L_e)
- Optimal effort selection: c'(e*) = -∂ρ_V(L_e)/∂e

## Contributing

This is a specification and prototype project. Contributions welcome for:
- Schema refinements
- Additional vertical guides
- Prototype improvements
- SDK implementations

## License

MIT License - see LICENSE file for details.
