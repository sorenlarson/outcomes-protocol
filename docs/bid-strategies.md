# Bid Strategies Deep Dive

**Version:** 1.0.0-draft
**Status:** Draft

## Overview

Bid strategies in the Outcomes Protocol borrow from programmatic advertising (Meta Advantage+, Google Performance Max) to solve price discovery for AI outcomes. Instead of negotiating prices per-customer, buyers express willingness-to-pay through standardized bid strategies, and the marketplace matches supply and demand.

## Why Bid-Based Pricing?

### The Information Asymmetry Problem

| Party | Knows | Doesn't Know |
|-------|-------|--------------|
| Buyer | Value of outcome to them | Provider's cost structure |
| Provider | Their cost to deliver | Buyer's true willingness to pay |
| Neither | Optimal price | Market clearing rate |

Traditional pricing requires revealing information:
- **Cost-plus**: Provider reveals costs → buyer extracts surplus
- **Value-based**: Buyer reveals value → provider extracts surplus

### The Bid-Based Solution

Bids express constraints without revealing underlying economics:

| What Buyer Says | What It Reveals | What Stays Private |
|-----------------|-----------------|-------------------|
| "Max $10/outcome" | Upper bound on WTP | Actual value (could be $100) |
| "Target $5 average" | Budget flexibility | Cost structure, margins |
| "5x ROAS target" | Value-to-cost ratio | Absolute value |

This enables price discovery without information leakage.

## Strategy Types

### 1. Max Outcome Price (Bid Cap)

**Concept**: Never pay more than X per successful outcome.

```json
{
  "bid_strategy": {
    "type": "max_outcome_price",
    "bid_amount": 10.00,
    "currency": "USD"
  }
}
```

**Behavior**:
- System bids up to $10 for each outcome
- If market price exceeds $10, outcome is not purchased
- Strict cap, no exceptions

**When to Use**:
- Hard unit economics constraints (e.g., "customer costs us $50 to acquire, max $10 for support")
- Compliance requirements on per-transaction costs
- Testing new outcome types with controlled spend

**Trade-offs**:
| Pro | Con |
|-----|-----|
| Predictable max cost | May miss outcomes when demand is high |
| Simple to understand | No flexibility for high-value situations |
| Easy to budget | Can't capture quality variance |

**Example Scenario**:
```
Bid cap: $10
Market prices: $8, $12, $7, $15, $9

Results:
- Outcome 1: Won at $8 ✓
- Outcome 2: Lost (above cap) ✗
- Outcome 3: Won at $7 ✓
- Outcome 4: Lost (above cap) ✗
- Outcome 5: Won at $9 ✓

Total: 3 outcomes, $24 spent, $8 average
```

---

### 2. Target Cost (Cost Cap)

**Concept**: Average to X per outcome over time, with flexibility per-outcome.

```json
{
  "bid_strategy": {
    "type": "target_cost",
    "bid_amount": 5.00,
    "currency": "USD",
    "tolerance_percent": 20,
    "averaging_window": "daily"
  }
}
```

**Behavior**:
- System targets $5 average cost
- Individual outcomes may cost $4-$7 (within tolerance)
- Adjusts bids to hit average over window

**When to Use**:
- Predictable budgeting with some flexibility
- Steady-state operations with consistent volume
- When outcome value is relatively uniform

**Trade-offs**:
| Pro | Con |
|-----|-----|
| Predictable average cost | Individual costs vary |
| More volume than bid cap | Requires volume to average out |
| Adapts to market | May overspend in volatile markets |

**Example Scenario**:
```
Target: $5 average
Tolerance: 20% ($4-$6 per outcome OK)
Window: Daily

Day 1 outcomes: $4, $6, $5, $5, $6 = $26 / 5 = $5.20 avg
  → Slightly over, system will bid lower tomorrow

Day 2 outcomes: $4, $4, $5, $4, $5 = $22 / 5 = $4.40 avg
  → Under target, can bid higher for quality

Weekly average: $4.80 ✓ (within tolerance)
```

---

### 3. Return on Outcome Spend (ROAS)

**Concept**: Achieve target ratio of outcome value to cost.

```json
{
  "bid_strategy": {
    "type": "return_on_spend",
    "target_roas": 5.0,
    "outcome_value_source": "conversion_value",
    "minimum_roas": 3.0
  }
}
```

**Behavior**:
- If outcome value is $50, willing to pay up to $10 (5x ROAS)
- Dynamically adjusts based on predicted outcome value
- Requires outcome values in Conversions API

**When to Use**:
- Outcome values vary significantly
- Clear attribution of value to outcomes
- Sophisticated measurement infrastructure

**Trade-offs**:
| Pro | Con |
|-----|-----|
| Optimizes for value, not volume | Requires value tracking |
| Captures high-value opportunities | Complex to set up |
| Efficient spend allocation | Attribution challenges |

**Example Scenario**:
```
Target ROAS: 5x

Outcome A: Predicted value $100 → Bid up to $20
Outcome B: Predicted value $25 → Bid up to $5
Outcome C: Predicted value $200 → Bid up to $40

Results:
- Won A at $15, actual value $120 → 8x ROAS ✓
- Won B at $6, actual value $20 → 3.3x ROAS (below target)
- Won C at $35, actual value $180 → 5.1x ROAS ✓

Portfolio ROAS: $320 value / $56 cost = 5.7x ✓
```

---

### 4. Maximize Throughput

**Concept**: Get the most outcomes within budget.

```json
{
  "bid_strategy": {
    "type": "maximize_throughput",
    "budget": {
      "amount": 1000.00,
      "period": "daily"
    },
    "quality_floor": {
      "min_provider_score": 4.0
    }
  }
}
```

**Behavior**:
- Spend full budget to maximize outcome count
- Bid dynamically based on market conditions
- May pay premium during high-demand periods

**When to Use**:
- Fixed budget, variable demand
- All outcomes have similar value
- Coverage more important than efficiency

**Trade-offs**:
| Pro | Con |
|-----|-----|
| Maximizes volume | May overpay per outcome |
| Uses full budget | Less cost control |
| Simple goal | Quality may suffer without floor |

---

### 5. Minimize Cost

**Concept**: Get cheapest outcomes meeting criteria.

```json
{
  "bid_strategy": {
    "type": "minimize_cost",
    "volume_target": {
      "outcomes_per_day": 100,
      "flexibility": "soft"
    },
    "max_price": 15.00
  }
}
```

**Behavior**:
- Bid minimum necessary to win outcomes
- May win fewer outcomes if market is expensive
- Prioritizes cost efficiency over volume

**When to Use**:
- Flexible on volume
- Cost reduction is primary goal
- Can wait for favorable market conditions

---

## Budget Configuration

### Budget Structure

```json
{
  "budget": {
    "total": 10000.00,
    "period": "monthly",
    "daily_cap": 500.00,
    "currency": "USD",
    "rollover": false,
    "alerts": [
      { "threshold_percent": 80, "action": "notify" },
      { "threshold_percent": 95, "action": "reduce_bids" },
      { "threshold_percent": 100, "action": "pause" }
    ]
  }
}
```

### Budget Periods

| Period | Use Case | Pacing |
|--------|----------|--------|
| `hourly` | High-volume, time-sensitive | Aggressive |
| `daily` | Standard operations | Even |
| `weekly` | Variable weekly patterns | Flexible |
| `monthly` | Long-term budgeting | Conservative |
| `total` | Campaign/project-based | Lifetime |

### Budget Pacing

```json
{
  "pacing": {
    "type": "even | accelerated | front_loaded | back_loaded",
    "aggressiveness": 0.8
  }
}
```

| Pacing Type | Behavior |
|-------------|----------|
| `even` | Spread evenly across period |
| `accelerated` | Spend as fast as possible |
| `front_loaded` | Heavier spend early in period |
| `back_loaded` | Heavier spend late in period |

---

## Auto-Bidding

### Overview

Auto-bidding lets the system optimize bids based on historical performance.

```json
{
  "auto_bid": {
    "enabled": true,
    "learning_period_outcomes": 50,
    "optimization_goal": "cost_per_success",
    "constraints": {
      "min_bid": 1.00,
      "max_bid": 25.00,
      "max_daily_adjustment_percent": 20
    },
    "signals": [
      "time_of_day",
      "day_of_week",
      "outcome_type",
      "context_complexity",
      "provider_score"
    ]
  }
}
```

### Learning Period

During learning, the system:
1. Tests bid levels across range
2. Measures win rates and outcome quality
3. Builds predictive model

```
Learning Progress:
├── Outcomes 1-20: Exploration (wide bid variance)
├── Outcomes 21-35: Calibration (narrowing range)
└── Outcomes 36-50: Optimization (fine-tuning)

Post-learning: Stable optimized bidding
```

### Optimization Signals

| Signal | Impact |
|--------|--------|
| `time_of_day` | Bid higher during business hours |
| `day_of_week` | Adjust for weekend patterns |
| `outcome_type` | Different base rates per type |
| `context_complexity` | Higher bids for complex contexts |
| `provider_score` | Premium for proven providers |

### Bid Adjustments

```json
{
  "bid_adjustments": {
    "urgent": { "multiplier": 1.5 },
    "complex_context": { "multiplier": 1.3 },
    "preferred_provider": { "multiplier": 1.2 },
    "off_hours": { "multiplier": 0.8 }
  }
}
```

---

## Latency-Price Tradeoffs

### Latency Tiers

Different latency requirements have different price implications:

```json
{
  "delivery_constraints": {
    "latency_preference": "fastest"
  },
  "bid_strategy": {
    "type": "max_outcome_price",
    "bid_amount": 15.00,
    "latency_premium": {
      "fastest": 1.5,
      "balanced": 1.0,
      "cost_optimized": 0.7
    }
  }
}
```

| Latency | Premium | Effective Bid |
|---------|---------|---------------|
| `fastest` | 1.5x | $22.50 |
| `balanced` | 1.0x | $15.00 |
| `cost_optimized` | 0.7x | $10.50 |

### Deadline Bidding

For hard deadlines, bids increase as deadline approaches:

```
Time to deadline vs. Bid multiplier:

100% remaining ─── 1.0x
 50% remaining ─── 1.2x
 25% remaining ─── 1.5x
 10% remaining ─── 2.0x
  5% remaining ─── 3.0x (or escalate)
```

---

## Guarantee-Price Tradeoffs

### Guarantee Levels Affect Price

Higher guarantees cost more:

```json
{
  "guarantee_terms": {
    "level": "full"
  },
  "bid_strategy": {
    "type": "max_outcome_price",
    "bid_amount": 10.00
  }
}
```

Effective pricing:

| Guarantee Level | Base Bid | Risk Premium | Total Max |
|-----------------|----------|--------------|-----------|
| `none` | $10.00 | $0 | $10.00 |
| `basic` | $10.00 | $0.50 | $10.50 |
| `standard` | $10.00 | $1.00 | $11.00 |
| `full` | $10.00 | $2.50 | $12.50 |

### Risk-Adjusted Bidding

For ROAS strategies, risk adjusts value calculation:

```
Outcome value: $100
Failure probability: 5%
Expected value: $100 × 0.95 = $95

With basic guarantee (refund on failure):
Risk-adjusted value: $95 + ($10 × 0.05) = $95.50
  (expected value + expected refund)

With full guarantee ($50 max payout):
Risk-adjusted value: $95 + ($50 × 0.05) = $97.50
```

---

## Multi-Outcome Campaigns

### Portfolio Bidding

For buyers with multiple outcome types:

```json
{
  "campaign": {
    "name": "Q1 Support Automation",
    "outcomes": [
      {
        "type": "cs.resolve",
        "allocation_percent": 60,
        "bid_strategy": { "type": "target_cost", "bid_amount": 5.00 }
      },
      {
        "type": "cs.triage",
        "allocation_percent": 30,
        "bid_strategy": { "type": "minimize_cost", "max_price": 2.00 }
      },
      {
        "type": "cs.escalate",
        "allocation_percent": 10,
        "bid_strategy": { "type": "max_outcome_price", "bid_amount": 1.00 }
      }
    ],
    "total_budget": {
      "amount": 10000.00,
      "period": "monthly"
    },
    "optimization": {
      "rebalance": true,
      "rebalance_frequency": "weekly"
    }
  }
}
```

### Cross-Outcome Optimization

System can shift budget between outcome types:

```
Week 1:
- cs.resolve: High demand, high prices → Underspend
- cs.triage: Low demand → Overspend shifted here

Week 2: Rebalance
- Increase cs.resolve allocation (prices dropped)
- Decrease cs.triage allocation

Goal: Maximize total outcomes within budget
```

---

## Reporting & Analytics

### Bid Performance Metrics

| Metric | Description |
|--------|-------------|
| Win rate | % of bids that won |
| Effective CPA | Actual cost per outcome |
| Budget utilization | % of budget spent |
| ROAS achieved | Actual return on spend |
| Bid-to-clear ratio | Your bid vs. clearing price |

### Sample Report

```json
{
  "period": "2025-01-01 to 2025-01-18",
  "strategy": "target_cost",
  "target": 5.00,

  "summary": {
    "outcomes_won": 1847,
    "total_spend": 9012.50,
    "effective_cpa": 4.88,
    "budget_utilization": 90.1,
    "win_rate": 78.3
  },

  "by_outcome_type": {
    "cs.resolve": {
      "outcomes": 1203,
      "spend": 6315.75,
      "cpa": 5.25
    },
    "cs.triage": {
      "outcomes": 644,
      "spend": 2696.75,
      "cpa": 4.19
    }
  },

  "recommendations": [
    {
      "type": "bid_adjustment",
      "message": "cs.resolve CPA 5% over target. Consider reducing bid by 3-5%.",
      "impact": "Save ~$300/month"
    }
  ]
}
```

---

## Best Practices

### Strategy Selection Guide

| Situation | Recommended Strategy |
|-----------|---------------------|
| "I have strict unit economics" | Max Outcome Price |
| "I want predictable average costs" | Target Cost |
| "I know what outcomes are worth" | Return on Spend |
| "I have fixed budget, need volume" | Maximize Throughput |
| "I'm cost-sensitive, flexible on volume" | Minimize Cost |

### Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Bid cap too low | Win rate drops to near zero | Analyze market prices, increase cap |
| No budget alerts | Surprise overspend | Set alerts at 80%, 95% |
| ROAS without value tracking | System can't optimize | Implement conversion value reporting |
| Too short learning period | Unstable bidding | Allow 50+ outcomes for learning |

### Optimization Checklist

- [ ] Set budget alerts at 80% and 95%
- [ ] Define quality floors to prevent race-to-bottom
- [ ] Enable auto-bidding after initial learning
- [ ] Report outcome values for ROAS optimization
- [ ] Review bid performance weekly
- [ ] Adjust for seasonal patterns
