# Conversions API Specification

**Version:** 1.0.0-draft
**Status:** Draft

## Overview

The Conversions API (cAPI) is the feedback mechanism that closes the loop between outcome delivery and verified results. Modeled after Meta's Conversions API for server-side event tracking, cAPI enables:

1. **Accountability**: Providers are evaluated on actual outcomes, not just delivery
2. **Optimization**: Feedback improves matching, pricing, and provider selection
3. **Risk Settlement**: Guarantee claims are verified and settled
4. **Market Intelligence**: Aggregate data informs risk pricing

## Why Server-Side Events?

Unlike client-side tracking (e.g., pixels), server-side events:

| Advantage | Description |
|-----------|-------------|
| **Reliable** | Not blocked by ad blockers or privacy settings |
| **Secure** | Sensitive outcome data stays server-to-server |
| **Rich** | Can include business context unavailable client-side |
| **Timely** | Can be sent exactly when verification occurs |

## Event Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         BUYER SYSTEMS                          │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ CRM         │  │ Ticketing   │  │ Analytics   │            │
│  │ (resolution │  │ (satisfaction│ │ (value      │            │
│  │  confirmed) │  │  scores)    │  │  tracking)  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                     │
│                   ┌──────▼──────┐                              │
│                   │ Event       │                              │
│                   │ Aggregator  │                              │
│                   └──────┬──────┘                              │
└──────────────────────────┼─────────────────────────────────────┘
                           │
                           │ HTTPS POST
                           │ (batched events)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    CONVERSIONS API                            │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ Event       │  │ Validation  │  │ Enrichment  │           │
│  │ Ingestion   │──│ & Dedup     │──│ & Matching  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                           │                   │
│         ┌─────────────────────────────────┼──────────┐        │
│         ▼                                 ▼          ▼        │
│  ┌─────────────┐                   ┌───────────┐ ┌────────┐  │
│  │ Provider    │                   │ Risk      │ │ Billing│  │
│  │ Scoring     │                   │ Settlement│ │ Adjust │  │
│  └─────────────┘                   └───────────┘ └────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Event Types

### Core Events (cAPI-Verified Outcomes)

These events apply to outcomes where success can be objectively measured:

| Event Type | Trigger | Purpose |
|------------|---------|---------|
| `outcome.success` | Outcome verified successful | Confirm delivery, release guarantee, update scoring |
| `outcome.failure` | Outcome verified failed | Trigger refund, update scoring |
| `outcome.partial` | Mixed success on criteria | Nuanced feedback for optimization |
| `outcome.expired` | VH passed, no verification | Default handling (configurable) |

### Core Events (Guarantee-Backed Outcomes)

These events apply to outcomes where success requires judgment or has long verification horizons:

| Event Type | Trigger | Purpose |
|------------|---------|---------|
| `outcome.completed` | Outcome delivered (not verified) | Start guarantee period, record delivery |
| `guarantee.claim` | Defect discovered, claim filed | Initiate claim adjudication |
| `guarantee.evidence` | Evidence submitted for claim | Support claim with documentation |
| `guarantee.approved` | Claim validated | Trigger payout per guarantee terms |
| `guarantee.denied` | Claim rejected | Close claim, provide reason |
| `guarantee.expired` | Claim window closed, no claims | Release risk reserve |

**Key distinction**: For guarantee-backed outcomes, there is no `outcome.success` event at delivery time. The outcome is marked `completed`, and the guarantee period begins. Success is implicit if no valid claims are filed within the claim window.

### Guarantee Events

| Event Type | Trigger | Purpose |
|------------|---------|---------|
| `guarantee.claim` | Buyer submits claim | Initiate claim process |
| `guarantee.evidence` | Supporting documentation | Add evidence to claim |
| `guarantee.withdraw` | Buyer withdraws claim | Close claim without payout |

### Feedback Events

| Event Type | Trigger | Purpose |
|------------|---------|---------|
| `feedback.rating` | Quality rating submitted | Improve provider matching |
| `feedback.correction` | Buyer corrected output | Training signal for improvement |
| `feedback.comment` | Qualitative feedback | Rich context for analysis |

### Lifecycle Events

| Event Type | Trigger | Purpose |
|------------|---------|---------|
| `outcome.viewed` | Buyer viewed result | Engagement tracking |
| `outcome.used` | Buyer used/applied result | Usage confirmation |
| `outcome.superseded` | Outcome replaced | Version tracking |

## Event Schema

### Base Event Structure

```json
{
  "event_id": "evt_a1b2c3d4e5f6",
  "event_type": "outcome.success",
  "event_time": "2025-01-18T15:30:00.000Z",
  "event_source_time": "2025-01-18T15:29:55.000Z",

  "request_id": "req_xyz789",
  "response_id": "resp_abc123",
  "buyer_id": "buyer_456",

  "data": {
    // Event-type specific data
  },

  "context": {
    "source_system": "zendesk",
    "source_event_id": "zd_evt_123",
    "user_agent": "outcomes-sdk/1.0"
  }
}
```

### Outcome Success Event

```json
{
  "event_type": "outcome.success",
  "data": {
    "success": true,
    "success_criteria_results": {
      "resolution_confirmed": {
        "expected": true,
        "actual": true,
        "passed": true
      },
      "customer_satisfaction": {
        "expected": { "operator": "gte", "value": 4 },
        "actual": 5,
        "passed": true
      },
      "response_time_seconds": {
        "expected": { "operator": "lte", "value": 300 },
        "actual": 45,
        "passed": true
      }
    },
    "overall_success": true,
    "verification": {
      "method": "customer_survey",
      "timestamp": "2025-01-18T15:25:00Z",
      "confidence": 0.95
    },
    "outcome_value": {
      "amount": 75.00,
      "currency": "USD",
      "value_type": "ticket_value",
      "calculation_method": "avg_ticket_cost"
    }
  }
}
```

### Outcome Completed Event (Guarantee-Backed)

For guarantee-backed outcomes like contract drafting, this event marks delivery and starts the guarantee period:

```json
{
  "event_type": "outcome.completed",
  "data": {
    "completed": true,
    "artifacts_delivered": [
      {
        "type": "document",
        "name": "NDA_AcmeCorp_WidgetInc.docx",
        "hash": "sha256:abc123..."
      }
    ],
    "guarantee_period": {
      "starts": "2025-01-18T10:00:00Z",
      "ends": "2027-01-18T10:00:00Z",
      "claim_window_days": 730
    },
    "coverage": {
      "max_payout": 10000.00,
      "covered_defects": [
        "Missing required clauses",
        "Non-compliant terms",
        "Ambiguous language causing disputes"
      ]
    },
    "delivery_summary": {
      "outcome_type": "legal.draft_nda",
      "parties": ["Acme Corp", "Widget Inc"],
      "key_terms_included": ["confidentiality", "non-compete", "term_2_years"]
    }
  }
}
```

**Note**: No success/failure determination is made at this point. The outcome is delivered, and the guarantee period begins. If the buyer discovers a defect (e.g., the NDA failed to protect against a disclosure), they file a claim within the guarantee window.

### Outcome Failure Event (cAPI-Verified)

```json
{
  "event_type": "outcome.failure",
  "data": {
    "success": false,
    "success_criteria_results": {
      "resolution_confirmed": {
        "expected": true,
        "actual": false,
        "passed": false,
        "failure_reason": "Customer reopened ticket"
      },
      "customer_satisfaction": {
        "expected": { "operator": "gte", "value": 4 },
        "actual": 2,
        "passed": false
      }
    },
    "overall_success": false,
    "failure_category": "resolution_incomplete",
    "failure_details": "AI provided incorrect refund amount, customer had to follow up",
    "impact": {
      "customer_effort_score": 4,
      "required_human_intervention": true,
      "additional_cost_incurred": 25.00
    },
    "verification": {
      "method": "human_review",
      "reviewer": "support_lead_jane",
      "timestamp": "2025-01-18T16:00:00Z"
    }
  }
}
```

### Guarantee Claim Event

```json
{
  "event_type": "guarantee.claim",
  "data": {
    "claim_type": "outcome_caused_damage",
    "claim_description": "Contract review missed indemnification clause that exposed us to liability",
    "requested_compensation": {
      "amount": 5000.00,
      "currency": "USD",
      "breakdown": {
        "direct_damages": 3500.00,
        "legal_fees": 1500.00
      }
    },
    "evidence_summary": [
      {
        "evidence_id": "evd_001",
        "type": "document",
        "description": "Original contract with missed clause highlighted"
      },
      {
        "evidence_id": "evd_002",
        "type": "invoice",
        "description": "Legal fees for remediation"
      },
      {
        "evidence_id": "evd_003",
        "type": "correspondence",
        "description": "Counterparty demand letter"
      }
    ],
    "timeline": {
      "outcome_delivered": "2025-01-05T10:00:00Z",
      "issue_discovered": "2025-01-15T14:30:00Z",
      "claim_submitted": "2025-01-18T09:00:00Z"
    },
    "related_outcomes": ["resp_abc123"]
  }
}
```

### Guarantee Claim Approved Event

When a claim is validated and payout authorized:

```json
{
  "event_type": "guarantee.approved",
  "data": {
    "claim_id": "clm_xyz789",
    "request_id": "req_abc123",
    "adjudication": {
      "decision": "approved",
      "reviewed_by": "claims_adjudicator",
      "review_date": "2025-01-25T16:00:00Z",
      "findings": "NDA lacked standard non-solicitation clause; defect caused demonstrable harm when key employee was recruited by counterparty."
    },
    "payout": {
      "amount": 4500.00,
      "currency": "USD",
      "breakdown": {
        "direct_damages": 3500.00,
        "legal_fees": 1000.00
      },
      "payout_type": "actual_damages",
      "payment_method": "original_payment_method",
      "estimated_settlement": "2025-01-30T00:00:00Z"
    },
    "guarantee_status": {
      "remaining_coverage": 5500.00,
      "claim_window_remaining_days": 695
    }
  }
}
```

### Guarantee Expired Event

When the claim window closes without any claims:

```json
{
  "event_type": "guarantee.expired",
  "data": {
    "request_id": "req_abc123",
    "outcome_type": "legal.draft_nda",
    "guarantee_period": {
      "started": "2025-01-18T10:00:00Z",
      "ended": "2027-01-18T10:00:00Z"
    },
    "claims_filed": 0,
    "claims_paid": 0,
    "coverage_unused": 10000.00,
    "status": "expired_no_claims",
    "risk_reserve_released": true
  }
}
```

### Feedback Rating Event

```json
{
  "event_type": "feedback.rating",
  "data": {
    "overall_rating": 4,
    "dimension_ratings": {
      "accuracy": 5,
      "speed": 5,
      "clarity": 3,
      "thoroughness": 4
    },
    "nps_score": 8,
    "would_use_again": true,
    "comments": "Fast and accurate, but explanation was too technical for the customer",
    "improvement_suggestions": ["Simpler language option", "Include summary at top"],
    "comparison": {
      "vs_previous_provider": "better",
      "vs_human_baseline": "comparable"
    }
  }
}
```

### Feedback Correction Event

```json
{
  "event_type": "feedback.correction",
  "data": {
    "correction_type": "factual_error",
    "original_content": {
      "field": "refund_amount",
      "value": "$45.00"
    },
    "corrected_content": {
      "field": "refund_amount",
      "value": "$54.00"
    },
    "correction_reason": "Transposed digits in amount",
    "severity": "minor",
    "caught_by": "human_review",
    "customer_impact": "none"
  }
}
```

## API Endpoints

### Send Single Event

```http
POST /v1/events
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "event_id": "evt_...",
  "event_type": "outcome.success",
  ...
}
```

**Response:**
```json
{
  "success": true,
  "event_id": "evt_...",
  "processed_at": "2025-01-18T15:30:01Z",
  "warnings": []
}
```

### Send Batch Events

```http
POST /v1/events/batch
Content-Type: application/json
Authorization: Bearer {api_key}

{
  "events": [
    { "event_id": "evt_1", ... },
    { "event_id": "evt_2", ... },
    { "event_id": "evt_3", ... }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "processed": 3,
  "failed": 0,
  "results": [
    { "event_id": "evt_1", "status": "accepted" },
    { "event_id": "evt_2", "status": "accepted" },
    { "event_id": "evt_3", "status": "accepted" }
  ]
}
```

### Upload Claim Evidence

```http
POST /v1/claims/{claim_id}/evidence
Content-Type: multipart/form-data
Authorization: Bearer {api_key}

--boundary
Content-Disposition: form-data; name="file"; filename="contract.pdf"
Content-Type: application/pdf

[binary content]
--boundary
Content-Disposition: form-data; name="metadata"
Content-Type: application/json

{
  "evidence_type": "document",
  "description": "Original contract with missed clause"
}
--boundary--
```

### Query Event Status

```http
GET /v1/events/{event_id}
Authorization: Bearer {api_key}
```

**Response:**
```json
{
  "event_id": "evt_...",
  "status": "processed",
  "received_at": "2025-01-18T15:30:00Z",
  "processed_at": "2025-01-18T15:30:01Z",
  "actions_triggered": [
    "provider_score_updated",
    "guarantee_released"
  ]
}
```

## Event Processing

### Validation Rules

| Rule | Description | Action on Failure |
|------|-------------|-------------------|
| Schema validation | Event matches JSON schema | Reject with 400 |
| Request ID exists | Referenced request exists | Reject with 404 |
| Within claim window | For claims, within allowed period | Reject with 422 |
| Deduplication | Event ID not already processed | Skip silently |
| Temporal ordering | Event time after outcome delivery | Warn but accept |

### Deduplication

Events are deduplicated by `event_id`:

```
event_id = hash(request_id + event_type + event_source_time + buyer_id)
```

If same `event_id` received multiple times:
- First event: processed normally
- Subsequent events: acknowledged but not reprocessed

### Event Matching

Events are matched to outcomes via:
1. **Primary**: `request_id` + `response_id`
2. **Fallback**: `correlation_id` from original request
3. **Fuzzy**: Buyer ID + time window + outcome type

### Processing Pipeline

```
Event Received
      │
      ▼
┌─────────────┐
│ Validate    │──── Invalid ────► Reject
│ Schema      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Check       │──── Duplicate ──► Skip
│ Dedup       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Match to    │──── Not Found ──► Queue for Retry
│ Outcome     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Enrich      │
│ Context     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Trigger     │
│ Actions     │
└──────┬──────┘
       │
       ▼
   Complete
```

### Triggered Actions

Based on event type and content:

| Event | Condition | Actions |
|-------|-----------|---------|
| `outcome.success` | All criteria passed | Release guarantee, update provider score |
| `outcome.failure` | Any required criterion failed | Flag for claim eligibility, update scoring |
| `guarantee.claim` | Within window, with evidence | Create claim case, notify risk pool |
| `feedback.rating` | Any rating | Update provider quality metrics |
| `feedback.correction` | Error identified | Flag for retraining, update accuracy metrics |

## Integration Patterns

### Direct Integration

For systems that can make HTTP calls:

```python
import requests

def report_outcome_success(request_id, response_id, criteria_results):
    event = {
        "event_id": generate_event_id(),
        "event_type": "outcome.success",
        "event_time": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "response_id": response_id,
        "data": {
            "success": True,
            "success_criteria_results": criteria_results,
            "overall_success": all(c["passed"] for c in criteria_results.values())
        }
    }

    response = requests.post(
        "https://api.outcomes-protocol.com/v1/events",
        json=event,
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return response.json()
```

### Webhook-Based Integration

For event-driven architectures:

```json
{
  "webhook_config": {
    "events": ["ticket.resolved", "survey.completed"],
    "target_url": "https://api.outcomes-protocol.com/v1/webhooks/ingest",
    "transform": {
      "event_type_mapping": {
        "ticket.resolved": "outcome.success",
        "survey.completed": "feedback.rating"
      },
      "field_mapping": {
        "ticket_id": "request_id",
        "satisfaction_score": "data.dimension_ratings.overall"
      }
    }
  }
}
```

### Batch Upload

For systems with delayed data:

```python
# Nightly batch upload
events = []
for resolution in get_todays_resolutions():
    events.append({
        "event_id": f"batch_{resolution.id}",
        "event_type": "outcome.success" if resolution.successful else "outcome.failure",
        "event_time": resolution.resolved_at.isoformat() + "Z",
        "request_id": resolution.outcome_request_id,
        ...
    })

# Send in batches of 100
for batch in chunks(events, 100):
    requests.post(
        "https://api.outcomes-protocol.com/v1/events/batch",
        json={"events": batch},
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
```

## Verification Methods

### Automatic Verification

System-checkable criteria:

| Criterion | Verification Method |
|-----------|---------------------|
| Response time | Timestamp comparison |
| Format compliance | Schema validation |
| No errors thrown | Exception monitoring |
| API calls succeeded | Response code tracking |

### Human Verification

Requires human judgment:

| Criterion | Verification Method |
|-----------|---------------------|
| Customer satisfaction | Survey response |
| Resolution quality | Support lead review |
| Accuracy | Domain expert check |

### Delayed Verification

Long verification horizon:

| Criterion | Verification Method |
|-----------|---------------------|
| No follow-up needed | Ticket monitoring (7-day window) |
| Contract compliance | Periodic audit |
| Code stability | Production monitoring |

## Best Practices

### Event Timing

| Recommendation | Rationale |
|----------------|-----------|
| Send immediately when known | Faster feedback loop |
| Use `event_source_time` for original timestamp | Preserve temporal accuracy |
| Batch for high volume, real-time for high value | Balance efficiency and latency |

### Event Quality

| Recommendation | Rationale |
|----------------|-----------|
| Include all available criteria results | Richer feedback signal |
| Add outcome value when known | Enables ROAS optimization |
| Provide failure details | Actionable improvement data |

### Error Handling

| Scenario | Recommended Action |
|----------|-------------------|
| API unavailable | Queue locally, retry with backoff |
| Event rejected | Log, investigate, don't retry invalid |
| Partial batch failure | Retry failed events only |

## Rate Limits

| Tier | Events/minute | Batch size | Daily limit |
|------|---------------|------------|-------------|
| Standard | 100 | 100 | 50,000 |
| Professional | 1,000 | 500 | 500,000 |
| Enterprise | 10,000 | 1,000 | Unlimited |

## Security

### Authentication

All requests require Bearer token:
```
Authorization: Bearer op_live_abc123...
```

### Encryption

- All traffic over HTTPS (TLS 1.3)
- Evidence files encrypted at rest
- PII fields can be hashed before sending

### Audit Trail

All events are:
- Immutably logged
- Timestamped with server receipt time
- Associated with authenticated buyer
- Retained per data retention policy

## Appendix: Event Type Reference

| Event Type | Required Fields | Optional Fields |
|------------|-----------------|-----------------|
| `outcome.success` | success_criteria_results | outcome_value, verification |
| `outcome.failure` | success_criteria_results, failure_category | impact, failure_details |
| `outcome.partial` | success_criteria_results | partial_value |
| `guarantee.claim` | claim_type, requested_compensation | evidence_summary, timeline |
| `feedback.rating` | overall_rating | dimension_ratings, comments |
| `feedback.correction` | original_content, corrected_content | severity, correction_reason |
