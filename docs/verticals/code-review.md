# Code Review Vertical Guide

## Overview

Code review and bug fixing are well-defined outcome verticals where AI can provide immediate value. This guide covers implementing the Outcomes Protocol for automated code review and bug fixes.

## Why Guarantee-Backed?

Unlike customer service where success is clearly measurable (did the customer's issue get resolved?), code quality involves judgment:

- **Was the review thorough?** Hard to know until a bug slips through.
- **Is the fix complete?** Tests pass now, but did it introduce subtle issues?
- **Did it miss security vulnerabilities?** Only discovered when exploited.

Because "good enough" is partially subjective and defects may only surface later, code outcomes are **guarantee-backed**. The AI completes the work, and if defects are discovered within the claim window, the buyer can file a guarantee claim.

## Outcome Types

### code.review - Pull Request Review

**Verification Model**: Guarantee-backed (30-day claim window)

**Description**: Review pull request for bugs, security issues, and improvements. Guaranteed against missed critical issues.

**Typical Flow**:
1. PR submitted or updated
2. AI fetches diff, file context, and repo standards
3. Analysis performed across multiple dimensions
4. Review comments posted inline
5. Summary with approval/request changes decision

**Completion**: Agent affirms the review is complete. You pay on delivery.

**Guarantee Coverage** (30-day claim window):

| Defect Type | Coverage |
|-------------|----------|
| Missed critical bug | Bug in reviewed code found in production |
| Missed security vulnerability | CVE or exploit in reviewed code |
| False approval | Approved PR that should have been blocked |

**Pricing Range**: $0.50 - $5.00 per review (includes guarantee)
- Small PR (< 100 lines): $0.50 - $1.00
- Medium PR (100-500 lines): $1.00 - $2.50
- Large PR (> 500 lines): $2.50 - $5.00

**Delivery Time**:
- Blocking: < 15 minutes
- Standard: < 1 hour
- Non-urgent: < 4 hours

---

### code.fix - Bug Fix

**Verification Model**: Guarantee-backed (30-day claim window)

**Description**: Diagnose and fix reported bug. Guaranteed against regression or incomplete fix.

**Typical Flow**:
1. Bug report received (issue, error log, reproduction)
2. AI locates relevant code
3. Root cause analysis performed
4. Fix generated and tested
5. PR created with fix

**Completion**: Agent affirms the fix is complete (PR submitted). You pay on delivery.

**Guarantee Coverage** (30-day claim window):

| Defect Type | Coverage |
|-------------|----------|
| Incomplete fix | Original bug still reproducible |
| Regression | Fix introduced new bugs |
| Wrong root cause | Fix addressed symptom, not cause |

**Pricing Range**: $1.00 - $20.00 per fix (includes guarantee)
- Simple fix (typo, off-by-one): $1.00 - $3.00
- Medium fix (logic error): $3.00 - $8.00
- Complex fix (architecture issue): $8.00 - $20.00

**Delivery Time**:
- Urgent: < 1 hour
- Standard: < 4 hours
- Non-urgent: < 24 hours

---

## Context Sources

### Required Context

| Source | Purpose | Integration |
|--------|---------|-------------|
| Repository | Code access | Git/GitHub MCP server |
| PR/Diff | Changes to review | GitHub API |
| CI Status | Build/test results | CI/CD webhook |

### Recommended Context

| Source | Purpose | Integration |
|--------|---------|-------------|
| Code conventions | Style enforcement | `.editorconfig`, linter configs |
| Architecture docs | Context for decisions | Documentation files |
| Issue tracker | Bug context | Jira/GitHub Issues |
| Test coverage | Coverage requirements | Coverage reports |
| Security policies | Security standards | Security config files |

### Example Context Configuration

```json
{
  "context_sources": [
    {
      "type": "mcp_server",
      "config": {
        "server": "github",
        "tools": [
          "get_pull_request",
          "get_diff",
          "get_file_contents",
          "get_repo_tree",
          "get_commit_history"
        ]
      }
    },
    {
      "type": "mcp_server",
      "config": {
        "server": "codebase",
        "tools": [
          "search_code",
          "get_definitions",
          "get_references",
          "get_symbols"
        ]
      }
    },
    {
      "type": "file_reference",
      "config": {
        "paths": [
          ".eslintrc.json",
          "CONTRIBUTING.md",
          "docs/architecture.md"
        ]
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
| `get_file` | Read file contents | Understanding context |
| `search_code` | Find code patterns | Locating related code |
| `get_definitions` | Find symbol definitions | Understanding types |
| `get_references` | Find symbol usage | Impact analysis |
| `run_linter` | Check style | Style violations |
| `run_tests` | Execute tests | Verification |

### Write Tools (Require Configuration)

| Tool | Purpose | Risk Level | Typical Limits |
|------|---------|------------|----------------|
| `add_review_comment` | Post review comment | Low | N/A |
| `approve_pr` | Approve pull request | Medium | Require conditions |
| `request_changes` | Request changes | Low | N/A |
| `create_commit` | Commit changes | Medium | Branch protection |
| `create_pr` | Create pull request | Low | Draft by default |
| `merge_pr` | Merge pull request | High | Require approval |

### Tool Configuration Example

```json
{
  "tools": [
    {
      "name": "github_review",
      "type": "mcp_server",
      "config": {
        "server": "github",
        "tools": ["create_review", "add_comment", "approve", "request_changes"]
      },
      "guardrails": {
        "auto_approve": {
          "enabled": true,
          "conditions": [
            "lines_changed < 50",
            "no_security_findings",
            "all_tests_pass",
            "author_is_trusted"
          ]
        },
        "require_human_for": [
          "changes_to_security_critical",
          "changes_to_auth",
          "large_prs > 500_lines"
        ]
      }
    },
    {
      "name": "create_fix_pr",
      "type": "mcp_server",
      "config": {
        "server": "github",
        "tools": ["create_branch", "commit_changes", "create_pull_request"]
      },
      "guardrails": {
        "target_branch": "main",
        "pr_status": "draft",
        "require_tests": true
      }
    }
  ]
}
```

---

## Review Dimensions

### Bug Detection

| Category | Examples | Priority |
|----------|----------|----------|
| Logic errors | Off-by-one, null reference | Critical |
| Race conditions | Concurrent access issues | Critical |
| Resource leaks | Unclosed handles, memory | High |
| Error handling | Missing catches, swallowed errors | High |
| Edge cases | Boundary conditions | Medium |

### Security

| Category | Examples | Priority |
|----------|----------|----------|
| Injection | SQL, command, XSS | Critical |
| Authentication | Weak auth, missing checks | Critical |
| Authorization | Missing access control | Critical |
| Data exposure | Logging secrets, PII | High |
| Dependencies | Vulnerable packages | High |

### Style & Maintainability

| Category | Examples | Priority |
|----------|----------|----------|
| Naming | Unclear names, conventions | Medium |
| Complexity | High cyclomatic complexity | Medium |
| Duplication | Copy-paste code | Low |
| Documentation | Missing docs on public API | Low |
| Formatting | Style guide violations | Low |

### Performance

| Category | Examples | Priority |
|----------|----------|----------|
| N+1 queries | Database access patterns | High |
| Unnecessary work | Redundant computation | Medium |
| Memory usage | Large allocations | Medium |
| Algorithm choice | Suboptimal algorithms | Low |

---

## Escalation Policies

### When to Escalate

| Scenario | Trigger | Action |
|----------|---------|--------|
| Critical security finding | Severity = critical | Escalate + block merge |
| Complex architecture decision | Confidence < 0.7 | Request human review |
| Breaking changes | API compatibility issue | Escalate to API owner |
| Unfamiliar codebase area | No training data | Request human review |

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
        "type": "out_of_scope",
        "conditions": [
          "security_finding_critical",
          "architecture_decision_required",
          "breaking_api_change"
        ],
        "action": "escalate"
      }
    ],
    "handoff": {
      "destination": {
        "type": "github",
        "config": {
          "request_review_from": ["@senior-devs"],
          "add_label": "needs-human-review"
        }
      },
      "include_summary": true,
      "summary_format": "structured"
    }
  }
}
```

### Handoff Summary Format

```json
{
  "summary": {
    "pr_overview": "Adds new payment processing endpoint",
    "review_findings": {
      "critical": [],
      "high": [
        {
          "type": "security",
          "location": "src/payments/handler.ts:45",
          "description": "Potential SQL injection in query construction",
          "confidence": 0.85
        }
      ],
      "medium": [
        {
          "type": "maintainability",
          "location": "src/payments/handler.ts:20-80",
          "description": "Function too long (60 lines), consider splitting"
        }
      ]
    },
    "reason_for_escalation": "Security finding requires human verification",
    "recommended_action": "Verify SQL injection finding before merge"
  }
}
```

---

## Delivery Constraints

### By Review Type

| Type | Max Latency | Preference | Checkpoint |
|------|-------------|------------|------------|
| PR Review (blocking) | 5 min | fastest | 1 min |
| PR Review (async) | 30 min | balanced | 5 min |
| Bug Fix | 2 hours | balanced | 15 min |
| Code Generation | 1 hour | balanced | 10 min |
| Refactoring | 4 hours | cost_optimized | 30 min |

### Configuration Example

```json
{
  "delivery_constraints": {
    "max_latency_seconds": 300,
    "latency_preference": "fastest",
    "deadline_type": "soft",
    "max_compute_budget": {
      "tokens": 50000,
      "dollars": 2.00
    },
    "max_attempts": 2
  }
}
```

---

## Bid Strategies for Code Review

### High-Throughput (CI Integration)

```json
{
  "bid_strategy": {
    "type": "target_cost",
    "bid_amount": 1.00,
    "budget": {
      "total": 2000.00,
      "period": "monthly"
    },
    "auto_bid": {
      "enabled": true
    }
  }
}
```

### Quality-Focused (Critical Repos)

```json
{
  "bid_strategy": {
    "type": "max_outcome_price",
    "bid_amount": 5.00,
    "optimization_goal": "quality"
  },
  "guarantee_terms": {
    "level": "standard",
    "failure_coverage": {
      "enabled": true,
      "max_payout": 100.00,
      "payout_conditions": [
        {
          "condition": "outcome_caused_damage",
          "description": "Missed bug caused production incident",
          "payout_type": "actual_damages"
        }
      ]
    }
  }
}
```

---

## Success Metrics & Reporting

### Key Metrics

| Metric | Definition | Good | Excellent |
|--------|------------|------|-----------|
| Bug Detection Rate | Bugs found / bugs present | > 70% | > 90% |
| False Positive Rate | False alerts / total alerts | < 15% | < 5% |
| Review Time | Time from PR to review | < 5 min | < 2 min |
| Developer Satisfaction | Rating from PR authors | > 4.0 | > 4.5 |
| Cost per Review | Average review cost | < $1.50 | < $0.75 |

### Conversion Events

```json
{
  "event_type": "outcome.success",
  "data": {
    "success": true,
    "success_criteria_results": {
      "no_false_positives": { "passed": true },
      "actionable_comments": { "actual": 0.95, "passed": true },
      "review_time_minutes": { "actual": 2.5, "passed": true }
    },
    "verification": {
      "method": "author_feedback",
      "timestamp": "2025-01-18T11:00:00Z"
    },
    "outcome_value": {
      "amount": 15.00,
      "value_type": "time_saved",
      "calculation_method": "developer_hourly_rate * time_saved"
    }
  }
}
```

---

## Integration Examples

### GitHub Actions Integration

```yaml
name: AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - name: Request AI Review
        uses: outcomes-protocol/github-action@v1
        with:
          outcome_type: code.review
          api_key: ${{ secrets.OUTCOMES_API_KEY }}
          config: |
            success_criteria:
              required:
                - metric: no_critical_findings
                  operator: eq
                  value: true
            delivery_constraints:
              max_latency_seconds: 300
              latency_preference: fastest
            bid_strategy:
              type: max_outcome_price
              bid_amount: 2.00
```

### Greptile-Style Integration

```json
{
  "outcome_type": "code.review",
  "specification": {
    "objective": "Review PR #123 for bugs, security issues, and style",
    "constraints": [
      "Must check for SQL injection vulnerabilities",
      "Must verify error handling is complete",
      "Must flag any TODO comments"
    ],
    "preferences": [
      "Should suggest performance improvements",
      "Should note opportunities for code reuse"
    ]
  },
  "context_sources": [
    {
      "type": "mcp_server",
      "config": {
        "server": "greptile",
        "tools": ["search_codebase", "get_file_context", "get_related_code"]
      }
    }
  ]
}
```

---

## Best Practices

### Do's

- Start with non-blocking reviews to build trust
- Configure auto-approve for small, safe changes
- Set appropriate guardrails for security-critical areas
- Use codebase indexing for better context
- Report outcome values (time saved) for optimization

### Don'ts

- Don't auto-merge without human oversight initially
- Don't skip security checks for any PR
- Don't set unrealistic latency expectations
- Don't ignore false positive feedback
- Don't enable code generation without tests required
