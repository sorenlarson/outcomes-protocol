# Medical Scribing Vertical Guide

## Overview

Medical scribing generates clinical documentation from patient encounters in real-time. This guide covers implementing the Outcomes Protocol for AI-powered clinical documentation.

## Why Guarantee-Backed?

Medical scribing is **guarantee-backed** because documentation quality requires clinical expertise to verify:

- **Is the note accurate?** Only a clinician can assess if clinical facts are correctly captured.
- **Is it complete?** Material omissions may only surface during care transitions or audits.
- **Are codes correct?** Coding errors affecting reimbursement may be discovered in audits.

The AI generates the documentation, you pay on delivery, and if documentation defects are discovered within the claim window, you file a claim via the Claims API.

## Outcome Type

### medical.scribe - Clinical Scribing

**Verification Model**: Guarantee-backed (90-day claim window)

**Description**: Generate clinical documentation from patient encounter. Guaranteed against documentation errors.

**Typical Flow**:
1. Patient encounter audio/video captured
2. AI transcribes and extracts clinical information
3. Note structured per your template (SOAP, H&P, specialty-specific)
4. Draft integrated into your EHR with linked evidence
5. Physician reviews and signs

**Completion**: Agent affirms documentation is complete. You pay on delivery.

**Guarantee Coverage** (90-day claim window):

| Defect Type | Coverage |
|-------------|----------|
| Factual Documentation Error | Wrong medication, dosage, or clinical fact documented |
| Critical Omission | Material information from encounter not documented |
| Misattribution | Statement attributed to wrong party (patient, provider, family) |
| Coding Error | Incorrect codes affecting reimbursement (if coding included) |

**Not Covered**:
- Clinical judgment errors (documentation was accurate but clinical decision was wrong)
- Downstream treatment decisions based on the note
- Patient harm from treatment (not documentation)
- Malpractice claims against the provider

**Pricing Range**: $1.00 - $8.00 per encounter (includes guarantee)
- Brief visit (< 10 min): $1.00 - $2.00
- Standard visit (10-30 min): $2.00 - $4.00
- Complex visit (> 30 min): $4.00 - $8.00

**Delivery**: Real-time (documentation available during or immediately after encounter)

---

## Context Sources

### Buyer-Provided Context (You Configure)

These are data sources you control and connect:

| Source | Purpose | Integration |
|--------|---------|-------------|
| Your EHR System | Patient context, prior encounters | Epic/Cerner FHIR API |
| Your Note Templates | SOAP, H&P, specialty-specific formats | Template configuration |
| Your Clinician Preferences | Documentation style and terminology | Preference settings |
| Your Clinical Protocols | Organization-specific guidelines | Protocol database |

### Agent Resources (Included)

The execution engine has access to these resources. Costs are rolled into the outcome price.

| Resource | Purpose |
|----------|---------|
| Clinical Knowledge Base | Medical terminology and context |
| ICD-10 Database | Diagnosis code reference |
| CPT Code Database | Procedure code reference |
| Drug Database | Medication information and interactions |

---

## Buyer-Controlled Actions

These are the only actions you configure—what the agent can do with *your* systems:

### Read Access (Your Data)
| Action | Purpose |
|--------|---------|
| Access patient context from your EHR | Pull relevant patient history for context |
| Reference prior encounters | Maintain continuity across visits |
| Use your note templates | Apply your organization's documentation standards |

### Write Access (Your Systems)
| Action | Purpose | Notes |
|--------|---------|-------|
| Save draft to your EHR | Store generated documentation | Draft status until signed |
| Route for physician review | Send to appropriate reviewer | Configurable routing |

---

## Linked Evidence

A key feature of medical scribing is **traceability**—every element of the AI-generated note links back to its source in the conversation:

```json
{
  "note_section": "Chief Complaint",
  "content": "Patient reports chest pain for 2 days",
  "linked_evidence": {
    "source_type": "transcript",
    "timestamp": "00:01:23",
    "speaker": "patient",
    "original_text": "I've had this pain in my chest for about two days now"
  }
}
```

This enables:
- Rapid verification by reviewing physician
- Audit trail for compliance
- Claim substantiation if errors discovered

---

## Escalation Policy

### When to Escalate

| Scenario | Trigger | Action |
|----------|---------|--------|
| Low transcription confidence | Audio quality poor | Flag for manual review |
| Unusual clinical terminology | Confidence < threshold | Request clarification |
| Missing required sections | Template incomplete | Route to physician |

### Configuration

```json
{
  "escalation_policy": {
    "enabled": true,
    "triggers": [
      {
        "type": "confidence_threshold",
        "threshold": 0.80,
        "action": "escalate"
      }
    ],
    "handoff": {
      "destination": {
        "type": "webhook",
        "config": {
          "url": "https://ehr.hospital.com/api/review-queue"
        }
      },
      "include_summary": true,
      "include_transcript": true
    }
  }
}
```

---

## Delivery Constraints

```json
{
  "delivery_constraints": {
    "max_latency_seconds": 30,
    "latency_preference": "fastest",
    "checkpoint_interval_seconds": 10
  }
}
```

| Mode | Latency | Use Case |
|------|---------|----------|
| Real-time | < 30 seconds | During encounter |
| Near real-time | < 2 minutes | Immediately after |
| Batch | < 30 minutes | End of session |

---

## Guarantee Terms

### Special Considerations

Medical documentation has **moderate verification horizons**—errors may surface during:
- Physician review (immediate)
- Care transitions (days to weeks)
- Billing audits (weeks to months)

The 90-day claim window covers the typical audit cycle.

### Configuration

```json
{
  "guarantee_terms": {
    "level": "standard",
    "failure_coverage": {
      "enabled": true,
      "max_payout": 5000.00,
      "payout_conditions": [
        {
          "condition": "outcome_failed",
          "description": "Documentation contained factual error",
          "payout_type": "refund"
        },
        {
          "condition": "outcome_caused_damage",
          "description": "Documentation error caused billing denial or compliance issue",
          "payout_type": "actual_damages",
          "amount_cap": 5000.00
        }
      ],
      "claim_window_days": 90
    },
    "limitations": {
      "disclaimer": "Guarantee covers documentation accuracy, not clinical judgment.",
      "excluded": [
        "Clinical decision-making",
        "Treatment outcomes",
        "Malpractice claims"
      ]
    }
  }
}
```

---

## Compliance

### HIPAA Requirements

| Requirement | Implementation |
|-------------|----------------|
| PHI Protection | End-to-end encryption, BAA required |
| Access Controls | Role-based access, audit logging |
| Data Retention | Per your organization's policy |
| Breach Notification | Included in guarantee terms |

### Audit Trail

Every AI-generated note includes:
- Timestamp of generation
- Model/engine identifier
- Linked evidence to source
- Physician review status
- Edit history

---

## Success Metrics

| Metric | Definition | Good | Excellent |
|--------|------------|------|-----------|
| Documentation Accuracy | Errors per 1000 notes | < 10 | < 2 |
| Completion Rate | Notes completed without escalation | > 95% | > 99% |
| Physician Edit Rate | % of notes requiring edits | < 20% | < 5% |
| Time Saved | Minutes saved per encounter | > 5 min | > 10 min |
| Claim Rate | Claims per 1000 notes | < 5 | < 1 |

---

## Best Practices

### Do's

- Configure templates that match your specialty and workflow
- Connect prior encounter context for continuity
- Set appropriate claim amounts based on typical billing values
- Review linked evidence when verifying AI output

### Don'ts

- Don't rely solely on AI for clinical decision-making
- Don't skip physician review and signature
- Don't set claim windows shorter than your audit cycle
- Don't use for specialties without appropriate template support
