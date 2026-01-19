# Outcomes Protocol SDK Integration

This directory contains resources for integrating the Outcomes Protocol with the Claude Agent SDK.

## Overview

The SDK integration enables AI agents built on Claude Agent SDK to operate as **execution engines** in the Outcomes Protocol marketplace. An execution engine is a combination of:
- **Model**: The AI model (e.g., Claude Opus 4, Claude Sonnet)
- **Harness**: The tooling layer (Claude Code, custom MCP servers)

Execution engines can:
1. Receive and process outcome requests
2. Bid on outcomes based on capability and pricing
3. Report delivery via the Conversions API
4. Handle escalation to human operators
5. Optimize based on feedback

## Files

- `outcomes.yml` - Example configuration file for `.claude/outcomes.yml`
- `outcomes_provider.py` - Execution engine harness for executing outcomes
- `examples/` - Example implementations for specific verticals

## Configuration

### Project-Level Configuration

Place `outcomes.yml` in your project's `.claude/` directory:

```
your-project/
├── .claude/
│   ├── settings.json
│   └── outcomes.yml    <-- Outcomes configuration
├── src/
└── ...
```

### Configuration Structure

```yaml
# .claude/outcomes.yml

# Execution engine identity
execution_engine:
  id: "claude-code-acme-cs"
  name: "Acme Customer Service Engine"
  version: "1.0.0"
  model: "claude-opus-4"
  harness: "claude-code"
  vendor: "anthropic"

# Supported outcome types
outcomes:
  - type: "cs.resolve"
    enabled: true
    config:
      max_latency_seconds: 300
      default_effort: "standard"

# Tool permissions
tools:
  allowed:
    - "crm.*"
    - "orders.get_*"
    - "orders.process_refund"
  denied:
    - "*.delete_*"
    - "admin.*"

# Escalation configuration
escalation:
  enabled: true
  destinations:
    - type: "zendesk"
      config:
        subdomain: "${ZENDESK_SUBDOMAIN}"

# Conversions API reporting
conversions:
  api_endpoint: "https://api.outcomes-protocol.com/v1/events"
  api_key: "${OUTCOMES_API_KEY}"
  auto_report: true
```

## Execution Engine Harness

The `outcomes_provider.py` module provides a harness for operating as an execution engine:

```python
from outcomes_provider import OutcomesEngine

# Initialize engine
engine = OutcomesEngine.from_config(".claude/outcomes.yml")

# Process an outcome request
async def handle_request(request):
    # Execute the outcome
    response = await engine.execute(request)

    # Report to conversions API (automatic if auto_report: true)
    await engine.report_conversion(response)

    return response
```

## Hooks Integration

The execution engine integrates with Claude Agent SDK hooks:

```python
# In your hooks configuration
from outcomes_provider import outcome_hooks

hooks = {
    "pre_tool_call": outcome_hooks.pre_tool_call,
    "post_tool_call": outcome_hooks.post_tool_call,
    "on_completion": outcome_hooks.on_completion,
    "on_error": outcome_hooks.on_error,
}
```

## Example Implementations

### Customer Service (`examples/customer_service_outcome.py`)

Complete implementation of `cs.resolve` outcome type with:
- CRM context integration
- Order lookup and refund tools
- Customer satisfaction tracking
- Zendesk escalation

### Code Review (`examples/code_review_outcome.py`)

Implementation of `code.review` outcome type with:
- GitHub integration
- Codebase indexing
- Review comment generation
- Auto-approval logic

## Getting Started

1. Copy `outcomes.yml` to your project's `.claude/` directory
2. Configure your execution engine settings and API keys
3. Import and initialize the execution engine harness
4. Connect hooks to your agent execution

```python
import asyncio
from outcomes_provider import OutcomesEngine

async def main():
    # Load configuration
    engine = OutcomesEngine.from_config(".claude/outcomes.yml")

    # Example request
    request = {
        "request_id": "req_123",
        "outcome_type": "cs.resolve",
        "specification": {
            "objective": "Resolve customer order inquiry"
        },
        # ... rest of request
    }

    # Execute
    response = await engine.execute(request)
    print(f"Outcome: {response['status']}")
    print(f"Cost: ${response['delivery_metrics']['cost_breakdown']['total']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Variables

Required environment variables:

| Variable | Description |
|----------|-------------|
| `OUTCOMES_API_KEY` | API key for Conversions API |
| `ANTHROPIC_API_KEY` | API key for Claude |
| `ZENDESK_SUBDOMAIN` | Zendesk subdomain (if using) |
| `ZENDESK_API_TOKEN` | Zendesk API token (if using) |
| `GITHUB_TOKEN` | GitHub token (for code outcomes) |

## Testing

```bash
# Run execution engine tests
python -m pytest tests/

# Test specific outcome type
python -m pytest tests/test_cs_resolve.py

# Run with mock conversions API
MOCK_CONVERSIONS=1 python -m pytest tests/
```

## Debugging

Enable debug logging:

```python
import logging
logging.getLogger("outcomes_engine").setLevel(logging.DEBUG)
```

View execution traces:

```python
response = await engine.execute(request, trace=True)
print(response["_trace"])
```
