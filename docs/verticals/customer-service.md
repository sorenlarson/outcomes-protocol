# Customer Service Vertical Guide

## Overview

Customer service is one of the most mature verticals for AI outcomes. This guide covers how to implement the Outcomes Protocol for customer support use cases.

## Why One Outcome Type?

Unlike other verticals where the buyer explicitly requests a specific type of work (e.g., "review this contract", "fix this bug"), customer service is **reactive**. When a customer initiates contact, you don't know what they'll need:

- Will they ask a question?
- Request a refund?
- Need help with onboarding?
- Have a complex dispute?

Since the outcome type must be determined at contract time (before the customer interaction), customer service uses a single outcome type: **resolve the inquiry**, whatever it turns out to be.

## Outcome Type

### cs.resolve - Resolve Inquiry

**Verification Model**: cAPI-verified

**Description**: Fully resolve customer inquiry end-to-end. The AI handles whatever the customer needs: questions, transactions, troubleshooting. Takes appropriate actions and confirms resolution.

**Typical Flow**:
1. Customer initiates contact (chat, email, phone)
2. AI identifies issue and gathers context
3. AI takes appropriate actions (answer, lookup, refund, etc.)
4. Conversation ends
5. Buyer reports outcome via cAPI (success if no reopen, failure if escalated or reopened)

**Success Criterion**:

The single success criterion is: **Inquiry resolved without escalation and without customer reopening the issue.**

| Signal | cAPI Event | When Reported |
|--------|------------|---------------|
| Success | `outcome.success` | Ticket closed AND no reopen within 7 days |
| Failure | `outcome.failure` | Escalated to human OR customer reopened |

**Optional Enrichment Signals** (for optimization, not success determination):
- `customer_satisfaction`: CSAT score if customer provides rating
- `handle_time`: Total conversation duration
- `outcome_value`: Value of transaction (e.g., order saved, upsell)

These optional signals help the marketplace optimize provider matching but are not required for outcome verification.

**Pricing Range**: $0.15 - $2.00 per resolution
- Simple inquiries (FAQ, status check): $0.15 - $0.40
- Transactional requests (refund, change): $0.40 - $0.80
- Complex disputes: $0.80 - $2.00

The blended pricing reflects the mix of inquiry types the execution engine will handle.

**Latency SLAs** (AI response time to customer):

| Tier | First Response | Each Subsequent Response |
|------|----------------|--------------------------|
| Streaming | < 2 seconds | < 2 seconds |
| Fast | < 5 seconds | < 5 seconds |
| Standard | < 15 seconds | < 15 seconds |

Channel-specific expectations:
- Chat: Streaming or Fast tier
- Email: Standard tier acceptable
- Phone: Streaming required

---

## Delivery Mechanisms (Not Outcomes)

The following are **delivery mechanisms** that the execution engine chooses, not outcome types the buyer contracts for:

| Mechanism | Description | When Used |
|-----------|-------------|-----------|
| Self-service deflection | Guide to knowledge base or FAQ | Simple, common questions |
| Direct AI resolution | AI completes the request | Most inquiries |
| Intelligent escalation | Hand off to human with context | Complex, sensitive, or out-of-scope |
| Triage & route | Classify and route to specialist | Specialized issues |

The buyer pays for the **outcome** (cs.resolve), not the path taken. The execution engine optimizes which mechanism to use based on the inquiry type, cost efficiency, and success likelihood.

---

## Context Sources

### Required Context

| Source | Purpose | Integration |
|--------|---------|-------------|
| Customer profile | Personalization, history | CRM MCP server |
| Order history | Order-related inquiries | E-commerce MCP server |
| Knowledge base | Policy and FAQ lookup | Knowledge MCP server |

### Recommended Context

| Source | Purpose | Integration |
|--------|---------|-------------|
| Product catalog | Product questions | Catalog API |
| Inventory status | Availability queries | Inventory API |
| Shipping status | Delivery inquiries | Logistics API |
| Previous interactions | Continuity | Conversation history |

### Example Context Configuration

```json
{
  "context_sources": [
    {
      "type": "mcp_server",
      "config": {
        "server": "crm",
        "tools": ["get_customer", "get_order_history", "get_loyalty_status"]
      }
    },
    {
      "type": "mcp_server",
      "config": {
        "server": "knowledge",
        "tools": ["search_articles", "get_policy", "get_faq"]
      }
    },
    {
      "type": "mcp_server",
      "config": {
        "server": "orders",
        "tools": ["get_order", "get_shipment_status", "get_return_status"]
      }
    }
  ]
}
```

---

## Tools & Actions

### Read-Only Tools (Safe)

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `get_order_status` | Check order state | "Where is my order?" |
| `get_account_info` | View account details | "What's my balance?" |
| `search_knowledge` | Find help articles | "How do I return?" |
| `get_product_info` | Product details | "Is this compatible?" |

### Write Tools (Require Configuration)

| Tool | Purpose | Risk Level | Typical Limits |
|------|---------|------------|----------------|
| `process_refund` | Issue refund | Medium | Max $50-100 |
| `apply_discount` | Add promo code | Low | Approved codes only |
| `update_address` | Change shipping | Low | Before shipment |
| `cancel_order` | Cancel order | High | Require approval |
| `create_return` | Initiate return | Medium | Within policy |
| `send_notification` | Email/SMS customer | Low | Templates only |

### Tool Configuration Example

```json
{
  "tools": [
    {
      "name": "process_refund",
      "type": "api",
      "config": {
        "endpoint": "https://api.store.com/refunds",
        "method": "POST"
      },
      "permissions": ["refund_amount_max_100"],
      "guardrails": {
        "max_amount": 100.00,
        "require_reason": true,
        "allowed_reasons": ["damaged", "not_as_described", "late_delivery", "changed_mind"]
      }
    },
    {
      "name": "apply_discount",
      "type": "api",
      "config": {
        "endpoint": "https://api.store.com/discounts",
        "method": "POST"
      },
      "guardrails": {
        "allowed_codes": ["SORRY10", "LOYALTY15", "COMEBACK20"],
        "max_discount_percent": 20
      }
    }
  ]
}
```

---

## Escalation Policies

### When to Escalate

| Scenario | Trigger Type | Typical Threshold |
|----------|--------------|-------------------|
| Low confidence | `confidence_threshold` | < 0.70 |
| Customer frustrated | Sentiment detection | Anger/frustration detected |
| Complex dispute | `out_of_scope` | Billing dispute > $100 |
| Legal threat | `policy_violation` | Legal keywords detected |
| Explicit request | `explicit_request` | "Talk to human" patterns |
| Repeated failures | `max_attempts` | 3 attempts |

### Escalation Configuration

```json
{
  "escalation_policy": {
    "enabled": true,
    "triggers": [
      {
        "type": "confidence_threshold",
        "threshold": 0.70,
        "action": "escalate"
      },
      {
        "type": "explicit_request",
        "patterns": [
          "speak to human",
          "talk to agent",
          "real person",
          "supervisor",
          "manager"
        ],
        "action": "escalate"
      },
      {
        "type": "out_of_scope",
        "conditions": [
          "dispute_amount > 100",
          "legal_threat_detected",
          "fraud_suspected"
        ],
        "action": "escalate"
      },
      {
        "type": "max_attempts",
        "attempts": 3,
        "action": "escalate"
      }
    ],
    "handoff": {
      "destination": {
        "type": "zendesk",
        "config": {
          "subdomain": "acme",
          "group_id": "support_tier2"
        }
      },
      "include_summary": true,
      "include_transcript": true,
      "summary_format": "structured",
      "priority_mapping": {
        "high_value_customer": "urgent",
        "frustrated_customer": "high",
        "default": "normal"
      }
    },
    "partial_billing": {
      "enabled": true,
      "model": "fixed_triage_fee"
    }
  }
}
```

### Handoff Summary Format

```json
{
  "summary": {
    "issue_type": "billing_dispute",
    "issue_description": "Customer disputing $150 charge from Dec 15",
    "customer_sentiment": "frustrated",
    "actions_attempted": [
      "Verified charge is valid subscription renewal",
      "Offered 20% credit, customer declined",
      "Explained cancellation policy"
    ],
    "reason_for_escalation": "Dispute amount exceeds AI authority ($100 limit)",
    "recommended_action": "Review account history, consider goodwill gesture",
    "customer_context": {
      "tenure": "3 years",
      "lifetime_value": "$2,400",
      "previous_escalations": 0
    }
  }
}
```

---

## Delivery Constraints

### By Channel

| Channel | Max Latency | Latency Preference | Checkpoint Interval |
|---------|-------------|-------------------|---------------------|
| Live Chat | 30s | fastest | 10s |
| Phone | Real-time | fastest | N/A |
| Email | 4 hours | balanced | 5 min |
| Social | 15 min | balanced | 2 min |
| SMS | 60s | fastest | N/A |

### Configuration Example

```json
{
  "delivery_constraints": {
    "max_latency_seconds": 30,
    "latency_preference": "fastest",
    "deadline_type": "hard",
    "max_attempts": 3,
    "checkpoint_interval_seconds": 10
  }
}
```

---

## Bid Strategies for Customer Service

### Volume-Focused (High-traffic support)

```json
{
  "bid_strategy": {
    "type": "target_cost",
    "bid_amount": 0.40,
    "budget": {
      "total": 10000.00,
      "period": "monthly"
    },
    "auto_bid": {
      "enabled": true,
      "learning_period_outcomes": 100
    }
  }
}
```

### Quality-Focused (Premium support)

```json
{
  "bid_strategy": {
    "type": "max_outcome_price",
    "bid_amount": 2.00,
    "optimization_goal": "quality"
  },
  "guarantee_terms": {
    "level": "standard",
    "failure_coverage": {
      "enabled": true,
      "max_payout": 50.00
    }
  }
}
```

### Value-Optimized (E-commerce)

```json
{
  "bid_strategy": {
    "type": "return_on_spend",
    "target_roas": 10.0,
    "budget": {
      "total": 5000.00,
      "period": "monthly"
    }
  }
}
```

---

## Success Metrics & Reporting

### Key Metrics

| Metric | Definition | Good | Excellent |
|--------|------------|------|-----------|
| Resolution Rate | % resolved without escalation | > 65% | > 80% |
| CSAT | Customer satisfaction score | > 4.0 | > 4.5 |
| First Response Time | Time to first AI response | < 30s | < 10s |
| Resolution Time | Total time to resolve | < 5 min | < 2 min |
| Cost per Resolution | Average cost per outcome | < $0.50 | < $0.25 |
| Escalation Rate | % requiring human handoff | < 35% | < 20% |

### Conversion Events to Report

```json
{
  "event_type": "outcome.success",
  "data": {
    "success": true,
    "success_criteria_results": {
      "resolution_confirmed": { "passed": true },
      "customer_satisfaction": { "actual": 5, "passed": true },
      "response_time_seconds": { "actual": 23, "passed": true }
    },
    "outcome_value": {
      "amount": 75.00,
      "value_type": "cost_saved",
      "calculation_method": "avoided_human_handle_time"
    }
  }
}
```

---

## Integration Examples

### Zendesk Integration

```json
{
  "context_sources": [
    {
      "type": "mcp_server",
      "config": {
        "server": "zendesk",
        "tools": ["get_ticket", "get_user", "search_tickets", "get_macros"]
      }
    }
  ],
  "tools": [
    {
      "name": "update_ticket",
      "type": "mcp_server",
      "config": { "server": "zendesk", "tool": "update_ticket" }
    },
    {
      "name": "add_comment",
      "type": "mcp_server",
      "config": { "server": "zendesk", "tool": "add_comment" }
    }
  ],
  "escalation_policy": {
    "handoff": {
      "destination": {
        "type": "zendesk",
        "config": {
          "subdomain": "acme",
          "create_ticket": true,
          "assign_group": "tier2_support"
        }
      }
    }
  }
}
```

### Intercom Integration

```json
{
  "context_sources": [
    {
      "type": "mcp_server",
      "config": {
        "server": "intercom",
        "tools": ["get_conversation", "get_contact", "search_articles"]
      }
    }
  ],
  "escalation_policy": {
    "handoff": {
      "destination": {
        "type": "intercom",
        "config": {
          "workspace_id": "abc123",
          "assign_to_inbox": "human_support"
        }
      }
    }
  }
}
```

---

## Best Practices

### Do's

- Start with high-volume, simple inquiries (order status, FAQ)
- Set conservative action limits initially
- Monitor escalation reasons to identify improvement areas
- Report outcome values for ROAS optimization
- Use sentiment detection in escalation triggers

### Don'ts

- Don't enable high-risk actions (cancellation, large refunds) without approval workflows
- Don't skip the human handoff path - some issues need humans
- Don't set latency expectations you can't meet
- Don't ignore customer feedback signals
- Don't deploy without a knowledge base connected
