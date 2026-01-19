# Legal Vertical Guide

## Overview

Legal document work has well-defined outputs but requires expert judgment to verify quality. This guide covers implementing the Outcomes Protocol for legal use cases, from contract review to document drafting.

## Why Guarantee-Backed?

All legal outcomes are **guarantee-backed** because quality requires expertise to evaluate:

- **Was the review thorough?** Only an expert can assess if material risks were caught.
- **Is the draft correct?** Defects may only surface when terms are exercised or contracts disputed.
- **Are compliance requirements met?** Regulatory issues may emerge during audits years later.

Unlike customer service where success is clearly measurable (ticket closed, no reopen), legal work involves judgment that can only be validated by experts or time. The AI affirms completion, you pay on delivery, and if defects are discovered within the claim window, you file a claim via the Claims API.

## Verification Model

**All legal outcomes use the guarantee-backed model:**

| Outcome | Claim Window | Typical Coverage |
|---------|--------------|------------------|
| `legal.review` | 2 years | Missed material risks |
| `legal.summarize` | 1 year | Material omissions |
| `legal.compare` | 1 year | Missed material changes |
| `legal.draft_nda` | 2 years | Enforceability defects |
| `legal.draft_msa` | 2 years | Drafting defects |
| `legal.draft_dpa` | 2 years | Compliance defects |

**Claim Windows**: Legal outcomes have longer claim windows because defects may only surface when contract terms are exercised, compliance is audited, or disputes arise.

## Outcome Types

### legal.review - Contract Review

**Verification Model**: Guarantee-backed (2-year claim window)

**Description**: Review contract for risks, problematic clauses, and compliance issues. Guaranteed against missed material risks.

**Typical Flow**:
1. Contract document received
2. AI extracts and analyzes clauses
3. Risk assessment performed
4. Redlines and comments generated
5. Summary with risk score delivered

**Completion**: Agent affirms the review is complete. You pay on delivery.

**Guarantee Coverage** (2-year claim window):

| Defect Type | Coverage |
|-------------|----------|
| Missed Material Risk | Material risk in reviewed contract caused harm |
| Missed Problematic Clause | Problematic clause not flagged caused harm |
| Incorrect Risk Assessment | Risk level materially understated |

**Pricing Range**: $2.00 - $50.00 per review (includes guarantee)
- Standard NDA: $2.00 - $5.00
- Vendor agreement: $5.00 - $15.00
- Complex M&A doc: $25.00 - $50.00

**Delivery Time**:
- Urgent: < 1 hour
- Standard: < 4 hours
- Non-urgent: < 24 hours

---

### legal.summarize - Contract Summary

**Verification Model**: Guarantee-backed (1-year claim window)

**Description**: Extract and summarize key terms, obligations, deadlines, and renewal dates. Guaranteed against material omissions.

**Typical Flow**:
1. Contract received
2. Key terms extracted
3. Obligations identified and attributed
4. Important dates cataloged
5. Executive summary generated

**Completion**: Agent affirms the summary is complete. You pay on delivery.

**Guarantee Coverage** (1-year claim window):

| Defect Type | Coverage |
|-------------|----------|
| Missed Key Term | Material term omitted from summary |
| Missed Deadline | Critical deadline not captured |
| Misinterpretation | Term meaning materially misstated |

**Pricing Range**: $1.00 - $10.00 per summary (includes guarantee)
- Simple agreement: $1.00 - $2.00
- Multi-party contract: $2.00 - $5.00
- Complex commercial: $5.00 - $10.00

**Delivery Time**:
- Urgent: < 30 minutes
- Standard: < 2 hours
- Non-urgent: < 8 hours

---

### legal.draft_nda - Draft NDA

**Verification Model**: Guarantee-backed (2-year claim window)

**Description**: Generate Non-Disclosure Agreement from party information and confidentiality requirements.

**Typical Flow**:
1. Party information and requirements received
2. NDA type selected (mutual/unilateral)
3. Terms populated from inputs
4. Consistency check performed
5. Draft NDA delivered for review

**Success Criteria**:
| Criterion | Typical Target | Verification |
|-----------|---------------|--------------|
| Party info correct | All fields filled | Automatic |
| NDA type appropriate | Matches use case | Human check |
| Terms complete | Required clauses present | Automatic |
| Jurisdiction correct | Matches specification | Automatic |

**Pricing Range**: $8.00 - $20.00 per NDA
- Standard mutual NDA: $8.00 - $12.00
- Customized terms: $12.00 - $20.00

---

### legal.draft_msa - Draft MSA

**Verification Model**: Guarantee-backed (2-year claim window)

**Description**: Generate Master Services Agreement with payment terms, liability caps, and service descriptions.

**Typical Flow**:
1. Service description and terms received
2. MSA template selected
3. Commercial terms populated
4. Liability and indemnity sections configured
5. Draft MSA delivered for attorney review

**Success Criteria**:
| Criterion | Typical Target | Verification |
|-----------|---------------|--------------|
| Services described | Complete SOW | Human review |
| Payment terms correct | Matches inputs | Automatic |
| Liability caps set | Per policy limits | Automatic |
| No internal conflicts | Consistency check | Automatic |

**Pricing Range**: $25.00 - $50.00 per MSA
- Standard services MSA: $25.00 - $35.00
- Complex multi-service: $35.00 - $50.00

---

### legal.draft_dpa - Draft DPA

**Verification Model**: Guarantee-backed (2-year claim window)

**Description**: Generate GDPR/CCPA-compliant Data Processing Agreement with appropriate safeguards.

**Typical Flow**:
1. Data processing details received
2. Applicable regulations identified
3. Standard contractual clauses selected
4. Technical/organizational measures specified
5. DPA delivered with compliance notes

**Success Criteria**:
| Criterion | Typical Target | Verification |
|-----------|---------------|--------------|
| Regulations covered | All applicable | Compliance check |
| SCCs included | Where required | Automatic |
| Sub-processors addressed | List and terms | Human review |
| Security measures specified | Complete | Automatic |

**Pricing Range**: $15.00 - $35.00 per DPA
- Standard DPA: $15.00 - $25.00
- Multi-jurisdiction: $25.00 - $35.00

---

### legal.compare - Contract Comparison

**Verification Model**: Guarantee-backed (1-year claim window)

**Description**: Compare contract versions with detailed change summary. Guaranteed against missed material changes.

**Typical Flow**:
1. Two contract versions received
2. Section-by-section comparison
3. Changes categorized by type and risk
4. Risk implications assessed
5. Summary report with recommendations

**Completion**: Agent affirms the comparison is complete. You pay on delivery.

**Guarantee Coverage** (1-year claim window):

| Defect Type | Coverage |
|-------------|----------|
| Missed Material Change | Significant change between versions not identified |
| Wrong Risk Implication | Change implications materially misstated |

**Pricing Range**: $8.00 - $15.00 per comparison (includes guarantee)
- Simple comparison: $8.00 - $10.00
- Complex with analysis: $10.00 - $15.00

**Delivery Time**:
- Urgent: < 30 minutes
- Standard: < 2 hours
- Non-urgent: < 8 hours

---

## Context Sources

### Buyer-Provided Context (You Configure)

These are data sources you control and connect to the outcome request:

| Source | Purpose | Integration |
|--------|---------|-------------|
| Contract document | Primary content to review/analyze | Document upload |
| Your contract repository | Past agreements for comparison | MCP Server connection |
| Your clause library | Your approved clause templates | MCP Server connection |
| Your negotiation playbook | Your company positions and red lines | Policy database |
| Your company policies | Your legal and compliance policies | Policy database |
| Matter/deal context | Specific deal context | Configuration |

### Agent Resources (Included)

The execution engine has access to these resources. Costs are rolled into the outcome price.

| Resource | Purpose |
|----------|---------|
| Lexis Nexis | Legal research and case law |
| SEC EDGAR | Public company filings |
| Westlaw | Legal precedent database |
| Contract Standards DB | Industry-standard clause language |

You do not configure these resources - the agent uses them at its discretion as needed to complete the outcome.

### Example Context Configuration

```json
{
  "context_sources": [
    {
      "type": "inline",
      "content": "[Contract text]",
      "metadata": {
        "document_type": "vendor_agreement",
        "counterparty": "Acme Corp",
        "governing_law": "Delaware"
      }
    },
    {
      "type": "mcp_server",
      "config": {
        "server": "legal_policies",
        "tools": [
          "get_policy",
          "check_compliance",
          "get_risk_tolerance"
        ]
      }
    },
    {
      "type": "mcp_server",
      "config": {
        "server": "clause_library",
        "tools": [
          "get_preferred_clause",
          "get_fallback_clause",
          "check_clause_approval"
        ]
      }
    }
  ]
}
```

---

## Risk Assessment Framework

### Clause Categories

| Category | Risk Level | Examples |
|----------|------------|----------|
| **Critical** | Requires attorney | Indemnification, liability caps |
| **High** | Flag for review | IP assignment, exclusivity |
| **Medium** | Note but proceed | Payment terms, termination |
| **Low** | Informational | Notices, governing law |

### Risk Scoring

```json
{
  "risk_assessment": {
    "overall_score": 7.2,
    "max_score": 10,
    "category_scores": {
      "liability": 8.5,
      "ip_rights": 6.0,
      "termination": 5.5,
      "payment": 4.0,
      "compliance": 7.0
    },
    "critical_flags": [
      {
        "clause": "Section 8.3 - Indemnification",
        "issue": "Unlimited indemnification for third-party IP claims",
        "recommendation": "Cap at contract value or $X",
        "risk_level": "critical"
      }
    ]
  }
}
```

### Standard Review Checklist

| Area | Check Points |
|------|--------------|
| Liability | Caps, carve-outs, indemnification triggers |
| IP | Ownership, licenses, work product |
| Confidentiality | Scope, duration, exceptions |
| Termination | Rights, notice periods, effects |
| Payment | Terms, late fees, disputes |
| Data | Privacy, security, breach notification |
| Compliance | Regulatory requirements, representations |

---

## Tools & Actions

### Read-Only Tools (Safe)

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `extract_clauses` | Parse contract sections | Clause identification |
| `search_precedents` | Find similar contracts | Comparison |
| `check_policy` | Verify against policies | Compliance check |
| `lookup_statute` | Find relevant law | Legal research |

### Write Tools (Require Configuration)

| Tool | Purpose | Risk Level | Typical Limits |
|------|---------|------------|----------------|
| `add_redline` | Mark up document | Low | N/A |
| `suggest_clause` | Propose language | Medium | Pre-approved only |
| `create_draft` | Generate document | Medium | Template-based |
| `send_for_review` | Route to attorney | Low | N/A |

### Tool Configuration Example

```json
{
  "tools": [
    {
      "name": "clause_suggestion",
      "type": "mcp_server",
      "config": {
        "server": "clause_library",
        "tools": ["suggest_replacement"]
      },
      "guardrails": {
        "only_approved_clauses": true,
        "require_attorney_approval_for": [
          "indemnification",
          "liability_cap",
          "ip_assignment"
        ]
      }
    },
    {
      "name": "document_drafting",
      "type": "mcp_server",
      "config": {
        "server": "legal_drafting",
        "tools": ["create_from_template", "merge_clauses"]
      },
      "guardrails": {
        "template_required": true,
        "approved_templates_only": true,
        "always_draft_status": true
      }
    }
  ]
}
```

---

## Escalation Policies

### When to Escalate

| Scenario | Trigger | Action |
|----------|---------|--------|
| Critical clause identified | Risk level = critical | Escalate to attorney |
| Unusual terms | Confidence < 0.7 | Flag for review |
| Missing standard protections | Expected clause absent | Escalate |
| High-value contract | Value > threshold | Require attorney sign-off |
| Regulatory complexity | Jurisdiction complexity | Legal research escalation |

### Escalation Configuration

```json
{
  "escalation_policy": {
    "enabled": true,
    "triggers": [
      {
        "type": "out_of_scope",
        "conditions": [
          "critical_clause_found",
          "contract_value > 100000",
          "involves_ip_assignment",
          "unusual_jurisdiction"
        ],
        "action": "escalate"
      },
      {
        "type": "confidence_threshold",
        "threshold": 0.75,
        "action": "escalate"
      }
    ],
    "handoff": {
      "destination": {
        "type": "webhook",
        "config": {
          "url": "https://legal.company.com/api/escalations",
          "include_document": true
        }
      },
      "include_summary": true,
      "summary_format": "structured",
      "priority_mapping": {
        "critical_clause": "urgent",
        "high_value": "high",
        "default": "normal"
      }
    },
    "partial_billing": {
      "enabled": true,
      "model": "percentage_complete"
    }
  }
}
```

### Handoff Summary Format

```json
{
  "summary": {
    "document_type": "Master Services Agreement",
    "counterparty": "Acme Corp",
    "contract_value": "$500,000 annual",
    "risk_score": 7.2,
    "critical_findings": [
      {
        "section": "8.3",
        "issue": "Unlimited indemnification",
        "recommended_action": "Negotiate cap at 2x annual fees"
      }
    ],
    "review_completed": {
      "clauses_analyzed": 45,
      "issues_found": 12,
      "redlines_suggested": 8
    },
    "reason_for_escalation": "Critical indemnification clause requires attorney review",
    "recommended_action": "Review Section 8.3 and proposed redline before signing",
    "ai_confidence": 0.82
  }
}
```

---

## Delivery Constraints

### By Document Type

| Type | Max Latency | Preference | VH |
|------|-------------|------------|-----|
| NDA Review | 2 hours | balanced | 30 days |
| Vendor Agreement | 8 hours | balanced | 60 days |
| M&A Document | 24 hours | cost_optimized | 90 days |
| Quick Summary | 30 min | fastest | 7 days |

### Configuration Example

```json
{
  "delivery_constraints": {
    "max_latency_seconds": 7200,
    "latency_preference": "balanced",
    "deadline": "2025-01-19T17:00:00Z",
    "deadline_type": "soft",
    "max_compute_budget": {
      "tokens": 100000,
      "dollars": 10.00
    },
    "checkpoint_interval_seconds": 300
  }
}
```

---

## Guarantee Terms for Legal

### Special Considerations

Legal outcomes have **longer verification horizons** - problems may only surface when contract terms are exercised. This requires:

1. **Extended claim windows**: 30-90 days vs. 7 days for customer service
2. **Higher stakes**: Potential damages can be significant
3. **Clear limitations**: AI review supplements, doesn't replace, attorney

### Guarantee Configuration

```json
{
  "guarantee_terms": {
    "level": "standard",
    "failure_coverage": {
      "enabled": true,
      "max_payout": 10000.00,
      "payout_conditions": [
        {
          "condition": "outcome_failed",
          "description": "Missed clause that was in scope",
          "payout_type": "refund"
        },
        {
          "condition": "outcome_caused_damage",
          "description": "Missed clause caused verifiable loss",
          "payout_type": "actual_damages",
          "amount_cap": 10000.00,
          "verification_required": true,
          "requires_evidence": [
            "Original contract reviewed",
            "Clause that was missed",
            "Documentation of damages"
          ]
        }
      ],
      "claim_window_days": 60,
      "claim_process": "manual_review"
    },
    "risk_pricing": {
      "accept_market_price": true,
      "max_premium_percent": 25,
      "risk_factors": [
        "contract_value",
        "verification_horizon",
        "clause_complexity"
      ]
    },
    "limitations": {
      "disclaimer": "AI review is advisory. Final decisions require attorney review.",
      "excluded": [
        "Matters requiring legal judgment",
        "Litigation strategy",
        "Regulatory filings"
      ]
    }
  }
}
```

---

## Bid Strategies for Legal

### Volume Contracts (Standard Forms)

```json
{
  "bid_strategy": {
    "type": "target_cost",
    "bid_amount": 5.00,
    "budget": {
      "total": 5000.00,
      "period": "monthly"
    }
  },
  "guarantee_terms": {
    "level": "basic"
  }
}
```

### High-Stakes Review

```json
{
  "bid_strategy": {
    "type": "max_outcome_price",
    "bid_amount": 50.00,
    "optimization_goal": "quality"
  },
  "guarantee_terms": {
    "level": "full",
    "failure_coverage": {
      "max_payout": 25000.00,
      "claim_window_days": 90
    }
  }
}
```

---

## Success Metrics & Reporting

### Key Metrics

| Metric | Definition | Good | Excellent |
|--------|------------|------|-----------|
| Issue Detection | Issues found / issues present | > 90% | > 98% |
| False Positive Rate | False flags / total flags | < 10% | < 3% |
| Review Time | Time per standard contract | < 15 min | < 5 min |
| Attorney Satisfaction | Rating from legal team | > 4.0 | > 4.5 |
| Cost per Review | Average cost | < $10 | < $5 |
| Claim Rate | Claims / reviews | < 1% | < 0.1% |

### Conversion Events

```json
{
  "event_type": "outcome.success",
  "data": {
    "success": true,
    "success_criteria_results": {
      "clauses_identified": { "actual": "100%", "passed": true },
      "risk_flags_accurate": { "actual": "97%", "passed": true },
      "no_missed_critical": { "actual": true, "passed": true }
    },
    "verification": {
      "method": "attorney_review",
      "verifier": "legal_team_lead",
      "timestamp": "2025-01-18T15:00:00Z"
    },
    "outcome_value": {
      "amount": 500.00,
      "value_type": "cost_saved",
      "calculation_method": "attorney_hourly_rate * hours_saved"
    }
  }
}
```

---

## Best Practices

### Do's

- Always route critical clauses to attorneys
- Maintain clear disclaimers about AI limitations
- Set appropriate verification horizons per contract type
- Use pre-approved clause libraries
- Report outcome values for optimization

### Don'ts

- Don't represent AI review as legal advice
- Don't auto-approve any legal document
- Don't skip attorney review for high-value contracts
- Don't set claim windows shorter than typical exercise periods
- Don't use for litigation or regulatory filings
