"""
Outcomes Protocol Execution Engine Harness

This module provides a harness for operating as an execution engine in the
Outcomes Protocol marketplace. An execution engine is a combination of:
- Model: The AI model (e.g., Claude Opus 4)
- Harness: The tooling layer (e.g., Claude Code)

It handles:
- Loading and validating configuration
- Bidding on and executing outcomes
- Reporting to the Conversions API
- Managing escalation to human operators
"""

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

# Configure logging
logger = logging.getLogger("outcomes_engine")


class OutcomeStatus(Enum):
    """Possible outcome statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class EscalationTrigger(Enum):
    """Types of escalation triggers."""
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    EXPLICIT_REQUEST = "explicit_request"
    OUT_OF_SCOPE = "out_of_scope"
    MAX_ATTEMPTS = "max_attempts"
    TIMEOUT = "timeout"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class OutcomeRequest:
    """Represents an incoming outcome request."""
    request_id: str
    outcome_type: str
    specification: Dict[str, Any]
    context_sources: List[Dict[str, Any]] = field(default_factory=list)
    tools: List[Dict[str, Any]] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    delivery_constraints: Dict[str, Any] = field(default_factory=dict)
    escalation_policy: Dict[str, Any] = field(default_factory=dict)
    bid_strategy: Dict[str, Any] = field(default_factory=dict)
    guarantee_terms: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutcomeResponse:
    """Represents the response to an outcome request."""
    response_id: str
    request_id: str
    status: OutcomeStatus
    outcome: Optional[Dict[str, Any]] = None
    success_criteria_results: Optional[Dict[str, Any]] = None
    delivery_metrics: Optional[Dict[str, Any]] = None
    escalation: Optional[Dict[str, Any]] = None
    guarantee: Optional[Dict[str, Any]] = None
    execution_engine: Optional[Dict[str, Any]] = None
    timestamps: Dict[str, str] = field(default_factory=dict)


@dataclass
class EngineConfig:
    """Execution engine configuration loaded from outcomes.yml."""
    engine_id: str
    engine_name: str
    version: str
    model: str
    model_version: str
    harness: str
    harness_version: str
    vendor: str
    capabilities: List[str]
    outcomes: List[Dict[str, Any]]
    context_sources: Dict[str, Any]
    tools: Dict[str, Any]
    escalation: Dict[str, Any]
    conversions: Dict[str, Any]
    logging_config: Dict[str, Any]

    @classmethod
    def from_yaml(cls, path: str) -> "EngineConfig":
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            config = yaml.safe_load(f)

        # Expand environment variables
        config = cls._expand_env_vars(config)

        # Support both old 'provider' and new 'execution_engine' keys
        engine_config = config.get('execution_engine', config.get('provider', {}))

        return cls(
            engine_id=engine_config.get('id', 'unknown'),
            engine_name=engine_config.get('name', 'Unknown Engine'),
            version=engine_config.get('version', '0.0.0'),
            model=engine_config.get('model', 'claude-opus-4'),
            model_version=engine_config.get('model_version', ''),
            harness=engine_config.get('harness', 'claude-code'),
            harness_version=engine_config.get('harness_version', ''),
            vendor=engine_config.get('vendor', 'anthropic'),
            capabilities=engine_config.get('capabilities', []),
            outcomes=config.get('outcomes', []),
            context_sources=config.get('context_sources', {}),
            tools=config.get('tools', {}),
            escalation=config.get('escalation', {}),
            conversions=config.get('conversions', {}),
            logging_config=config.get('logging', {}),
        )

    @staticmethod
    def _expand_env_vars(config: Any) -> Any:
        """Recursively expand environment variables in config."""
        if isinstance(config, dict):
            return {k: EngineConfig._expand_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [EngineConfig._expand_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            var_name = config[2:-1]
            return os.environ.get(var_name, config)
        return config


class ConversionsClient:
    """Client for reporting to the Conversions API."""

    def __init__(self, config: Dict[str, Any]):
        self.endpoint = config.get('api_endpoint', '')
        self.api_key = config.get('api_key', '')
        self.auto_report = config.get('auto_report', True)
        self.retry_config = config.get('retry', {})

    async def report_event(self, event: Dict[str, Any]) -> bool:
        """Report an event to the Conversions API."""
        if not self.endpoint or not self.api_key:
            logger.warning("Conversions API not configured, skipping report")
            return False

        # In production, this would make an HTTP request
        # For now, we log the event
        logger.info(f"Reporting conversion event: {event['event_type']} for {event['request_id']}")

        # Simulate API call
        # In real implementation:
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(
        #         self.endpoint,
        #         json=event,
        #         headers={"Authorization": f"Bearer {self.api_key}"}
        #     ) as response:
        #         return response.status == 200

        return True

    def create_success_event(self, request: OutcomeRequest, response: OutcomeResponse) -> Dict[str, Any]:
        """Create a success event for the Conversions API."""
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "event_type": "outcome.success",
            "event_time": datetime.utcnow().isoformat() + "Z",
            "request_id": request.request_id,
            "response_id": response.response_id,
            "data": {
                "success": True,
                "success_criteria_results": response.success_criteria_results,
                "overall_success": True,
            }
        }

    def create_failure_event(self, request: OutcomeRequest, response: OutcomeResponse, reason: str) -> Dict[str, Any]:
        """Create a failure event for the Conversions API."""
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "event_type": "outcome.failure",
            "event_time": datetime.utcnow().isoformat() + "Z",
            "request_id": request.request_id,
            "response_id": response.response_id,
            "data": {
                "success": False,
                "failure_category": "execution_failed",
                "failure_details": reason,
            }
        }


class EscalationHandler:
    """Handles escalation to human operators."""

    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get('enabled', True)
        self.triggers = config.get('triggers', [])
        self.destinations = config.get('destinations', [])
        self.handoff_content = config.get('handoff_content', {})

    def should_escalate(
        self,
        confidence: float,
        attempt_count: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Optional[EscalationTrigger]:
        """Check if escalation should be triggered."""
        for trigger in self.triggers:
            trigger_type = trigger.get('type')

            if trigger_type == 'confidence_threshold':
                if confidence < trigger.get('threshold', 0.7):
                    return EscalationTrigger.CONFIDENCE_THRESHOLD

            elif trigger_type == 'explicit_request':
                patterns = trigger.get('patterns', [])
                message_lower = user_message.lower()
                if any(pattern.lower() in message_lower for pattern in patterns):
                    return EscalationTrigger.EXPLICIT_REQUEST

            elif trigger_type == 'max_attempts':
                if attempt_count >= trigger.get('attempts', 3):
                    return EscalationTrigger.MAX_ATTEMPTS

            elif trigger_type == 'out_of_scope':
                conditions = trigger.get('conditions', [])
                for condition in conditions:
                    if self._evaluate_condition(condition, context):
                        return EscalationTrigger.OUT_OF_SCOPE

        return None

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate an escalation condition."""
        # Simple condition evaluation
        # In production, this would be more sophisticated
        if "refund_amount > " in condition:
            threshold = float(condition.split("> ")[1])
            return context.get('refund_amount', 0) > threshold
        elif condition in context:
            return context[condition] is True
        return False

    async def escalate(
        self,
        request: OutcomeRequest,
        trigger: EscalationTrigger,
        context: Dict[str, Any],
        transcript: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform escalation to human operator."""
        handoff_id = f"hoff_{uuid.uuid4().hex[:12]}"

        # Build handoff payload
        payload = {
            "handoff_id": handoff_id,
            "request_id": request.request_id,
            "escalation_reason": {
                "trigger": trigger.value,
                "details": f"Escalated due to {trigger.value}"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Add summary if configured
        if self.handoff_content.get('include_summary', True):
            payload["summary"] = self._generate_summary(request, context, transcript)

        # Add transcript if configured
        if self.handoff_content.get('include_transcript', True):
            payload["transcript"] = transcript

        # Add customer context if configured
        if self.handoff_content.get('include_customer_context', True):
            payload["customer_context"] = context.get('customer', {})

        # Send to destination
        destination = self._get_destination()
        if destination:
            await self._send_to_destination(destination, payload)

        return {
            "handoff_id": handoff_id,
            "reason": payload["escalation_reason"],
            "destination": destination,
            "summary_provided": 'summary' in payload,
            "transcript_provided": 'transcript' in payload,
        }

    def _generate_summary(
        self,
        request: OutcomeRequest,
        context: Dict[str, Any],
        transcript: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a structured summary for handoff."""
        return {
            "issue": request.specification.get('objective', 'Unknown'),
            "attempted_resolution": context.get('attempted_actions', []),
            "customer_sentiment": context.get('sentiment', 'neutral'),
            "recommended_action": context.get('recommended_action', 'Review and resolve'),
        }

    def _get_destination(self) -> Optional[Dict[str, Any]]:
        """Get the highest priority available destination."""
        sorted_destinations = sorted(
            self.destinations,
            key=lambda d: d.get('priority', 999)
        )
        return sorted_destinations[0] if sorted_destinations else None

    async def _send_to_destination(self, destination: Dict[str, Any], payload: Dict[str, Any]):
        """Send handoff to the configured destination."""
        dest_type = destination.get('type')

        if dest_type == 'zendesk':
            # In production: create Zendesk ticket
            logger.info(f"Creating Zendesk ticket for handoff {payload['handoff_id']}")
        elif dest_type == 'webhook':
            # In production: POST to webhook URL
            logger.info(f"Posting to webhook for handoff {payload['handoff_id']}")
        else:
            logger.warning(f"Unknown destination type: {dest_type}")


class OutcomesEngine:
    """Main execution engine harness for bidding on and executing outcomes."""

    def __init__(self, config: EngineConfig):
        self.config = config
        self.conversions = ConversionsClient(config.conversions)
        self.escalation = EscalationHandler(config.escalation)

        # Configure logging
        log_level = getattr(logging, config.logging_config.get('level', 'INFO'))
        logger.setLevel(log_level)

    @classmethod
    def from_config(cls, path: str) -> "OutcomesEngine":
        """Create execution engine from configuration file."""
        config = EngineConfig.from_yaml(path)
        return cls(config)


    def get_outcome_config(self, outcome_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific outcome type."""
        for outcome in self.config.outcomes:
            if outcome.get('type') == outcome_type and outcome.get('enabled', True):
                return outcome
        return None

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed by the configuration."""
        allowed = self.config.tools.get('allowed', [])
        denied = self.config.tools.get('denied', [])

        # Check denied first
        for pattern in denied:
            if self._matches_pattern(tool_name, pattern):
                return False

        # Then check allowed
        for pattern in allowed:
            if self._matches_pattern(tool_name, pattern):
                return True

        return False

    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """Check if a name matches a wildcard pattern."""
        if '*' not in pattern:
            return name == pattern

        parts = pattern.split('*')
        if len(parts) == 2:
            prefix, suffix = parts
            return name.startswith(prefix) and name.endswith(suffix)

        return False

    def get_tool_limits(self, tool_name: str) -> Dict[str, Any]:
        """Get limits for a specific tool."""
        limits = self.config.tools.get('limits', {})
        return limits.get(tool_name, {})

    async def execute(
        self,
        request: OutcomeRequest,
        trace: bool = False
    ) -> OutcomeResponse:
        """Execute an outcome request."""
        start_time = time.time()
        response_id = f"resp_{uuid.uuid4().hex[:12]}"

        # Get outcome configuration
        outcome_config = self.get_outcome_config(request.outcome_type)
        if not outcome_config:
            return self._create_error_response(
                response_id, request,
                f"Outcome type {request.outcome_type} not supported or disabled"
            )

        # Check delivery constraints
        max_latency = request.delivery_constraints.get(
            'max_latency_seconds',
            outcome_config.get('config', {}).get('max_latency_seconds', 300)
        )

        # Initialize execution context
        context = {
            "request": request,
            "outcome_config": outcome_config,
            "attempt_count": 0,
            "actions_taken": [],
            "tools_called": [],
        }

        try:
            # Execute the outcome
            # In production, this would call the Claude API with appropriate tools
            result = await self._execute_outcome(request, outcome_config, context)

            # Check if escalation was triggered
            if result.get('escalated'):
                return self._create_escalated_response(
                    response_id, request, result, start_time
                )

            # Evaluate success criteria
            criteria_results = self._evaluate_criteria(request, result)

            # Create response
            response = OutcomeResponse(
                response_id=response_id,
                request_id=request.request_id,
                status=OutcomeStatus.COMPLETED if criteria_results['overall_success'] else OutcomeStatus.FAILED,
                outcome={
                    "type": request.outcome_type,
                    "result": result.get('result', {}),
                    "artifacts": result.get('artifacts', []),
                },
                success_criteria_results=criteria_results,
                delivery_metrics={
                    "latency_seconds": time.time() - start_time,
                    "tokens_used": result.get('tokens_used', 0),
                    "cost_breakdown": {
                        "compute": result.get('compute_cost', 0),
                        "risk_premium": 0,  # Calculated by marketplace
                        "total": result.get('compute_cost', 0),
                    },
                    "effort_level": outcome_config.get('config', {}).get('default_effort', 'standard'),
                    "tool_calls": context.get('tools_called', []),
                },
                execution_engine={
                    "engine_id": self.config.engine_id,
                    "model": self.config.model,
                    "model_version": self.config.model_version,
                    "harness": self.config.harness,
                    "harness_version": self.config.harness_version,
                    "vendor": self.config.vendor,
                    "capabilities": self.config.capabilities,
                },
                timestamps={
                    "requested_at": request.metadata.get('requested_at', datetime.utcnow().isoformat() + "Z"),
                    "started_at": datetime.utcnow().isoformat() + "Z",
                    "completed_at": datetime.utcnow().isoformat() + "Z",
                }
            )

            # Report to Conversions API if auto-report enabled
            if self.conversions.auto_report:
                event = self.conversions.create_success_event(request, response)
                await self.conversions.report_event(event)

            return response

        except Exception as e:
            logger.error(f"Error executing outcome: {e}")
            return self._create_error_response(response_id, request, str(e))

    async def _execute_outcome(
        self,
        request: OutcomeRequest,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the actual outcome using Claude."""
        # This is a simplified implementation
        # In production, this would:
        # 1. Initialize Claude client with appropriate model
        # 2. Set up MCP servers for context sources
        # 3. Configure tools with permissions
        # 4. Run the conversation/task
        # 5. Handle escalation triggers

        # Simulate execution
        logger.info(f"Executing {request.outcome_type} for request {request.request_id}")

        # Check for escalation triggers
        user_message = request.specification.get('objective', '')
        trigger = self.escalation.should_escalate(
            confidence=0.85,  # Would come from model
            attempt_count=context['attempt_count'],
            user_message=user_message,
            context=context
        )

        if trigger:
            escalation_result = await self.escalation.escalate(
                request, trigger, context, transcript=[]
            )
            return {
                "escalated": True,
                "escalation": escalation_result,
                "tokens_used": 500,
                "compute_cost": 0.01,
            }

        # Simulate successful completion
        return {
            "result": {
                "resolution": "Issue resolved successfully",
                "actions_taken": ["Looked up order", "Provided tracking info"],
            },
            "artifacts": [
                {
                    "type": "message",
                    "content": "Your order is on the way! Tracking: TRK123456",
                }
            ],
            "tokens_used": 2500,
            "compute_cost": 0.05,
        }

    def _evaluate_criteria(
        self,
        request: OutcomeRequest,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate success criteria against the result."""
        criteria = request.success_criteria
        results = {"required": [], "optional": [], "overall_success": True}

        # Evaluate required criteria
        for criterion in criteria.get('required', []):
            passed = self._evaluate_single_criterion(criterion, result)
            results["required"].append({
                "metric": criterion['metric'],
                "passed": passed,
            })
            if not passed:
                results["overall_success"] = False

        # Evaluate optional criteria
        for criterion in criteria.get('optional', []):
            passed = self._evaluate_single_criterion(criterion, result)
            results["optional"].append({
                "metric": criterion['metric'],
                "passed": passed,
            })

        return results

    def _evaluate_single_criterion(
        self,
        criterion: Dict[str, Any],
        result: Dict[str, Any]
    ) -> bool:
        """Evaluate a single criterion."""
        # Simplified evaluation
        # In production, this would be more sophisticated
        metric = criterion.get('metric')
        operator = criterion.get('operator', 'eq')
        expected = criterion.get('value')

        # For demo, assume all criteria pass
        return True

    def _create_error_response(
        self,
        response_id: str,
        request: OutcomeRequest,
        error: str
    ) -> OutcomeResponse:
        """Create an error response."""
        return OutcomeResponse(
            response_id=response_id,
            request_id=request.request_id,
            status=OutcomeStatus.FAILED,
            outcome=None,
            success_criteria_results={"required": [], "optional": [], "overall_success": False},
            delivery_metrics={"error": error},
            timestamps={
                "requested_at": datetime.utcnow().isoformat() + "Z",
                "completed_at": datetime.utcnow().isoformat() + "Z",
            }
        )

    def _create_escalated_response(
        self,
        response_id: str,
        request: OutcomeRequest,
        result: Dict[str, Any],
        start_time: float
    ) -> OutcomeResponse:
        """Create an escalated response."""
        return OutcomeResponse(
            response_id=response_id,
            request_id=request.request_id,
            status=OutcomeStatus.ESCALATED,
            outcome=None,
            escalation=result.get('escalation'),
            delivery_metrics={
                "latency_seconds": time.time() - start_time,
                "tokens_used": result.get('tokens_used', 0),
                "cost_breakdown": {
                    "compute": result.get('compute_cost', 0),
                    "total": result.get('compute_cost', 0),
                },
            },
            timestamps={
                "requested_at": datetime.utcnow().isoformat() + "Z",
                "escalated_at": datetime.utcnow().isoformat() + "Z",
            }
        )


# Backwards compatibility alias
OutcomesProvider = OutcomesEngine


# Hooks for Claude Agent SDK integration
class OutcomeHooks:
    """Hooks for integrating with Claude Agent SDK."""

    def __init__(self, engine: OutcomesEngine):
        self.engine = engine
        self.current_context = {}

    async def pre_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Called before each tool call."""
        # Check if tool is allowed
        if not self.engine.is_tool_allowed(tool_name):
            logger.warning(f"Tool {tool_name} not allowed")
            return {"error": f"Tool {tool_name} not permitted"}

        # Check tool limits
        limits = self.engine.get_tool_limits(tool_name)
        if limits:
            # Validate against limits
            if 'max_amount' in limits and 'amount' in args:
                if args['amount'] > limits['max_amount']:
                    return {"error": f"Amount exceeds limit of {limits['max_amount']}"}

        return None  # Allow the call

    async def post_tool_call(
        self,
        tool_name: str,
        args: Dict[str, Any],
        result: Any
    ):
        """Called after each tool call."""
        # Track tool usage
        self.current_context.setdefault('tools_called', []).append({
            "tool": tool_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": not isinstance(result, Exception),
        })

    async def on_completion(self, result: Dict[str, Any]):
        """Called when outcome execution completes."""
        logger.info("Outcome execution completed")

    async def on_error(self, error: Exception):
        """Called when an error occurs."""
        logger.error(f"Outcome execution error: {error}")


# Create default hooks instance
outcome_hooks = None


def init_hooks(engine: OutcomesEngine):
    """Initialize hooks with an execution engine."""
    global outcome_hooks
    outcome_hooks = OutcomeHooks(engine)
    return outcome_hooks


# Example usage
if __name__ == "__main__":
    async def main():
        # Load execution engine
        engine = OutcomesEngine.from_config("outcomes.yml")

        # Create sample request
        request = OutcomeRequest(
            request_id="req_test123",
            outcome_type="cs.resolve",
            specification={
                "objective": "Help customer track their order",
            },
            success_criteria={
                "required": [
                    {"metric": "resolution_confirmed", "operator": "eq", "value": True},
                ],
            },
            delivery_constraints={
                "max_latency_seconds": 300,
            },
        )

        # Execute
        response = await engine.execute(request)
        print(f"Status: {response.status.value}")
        print(f"Response ID: {response.response_id}")

    asyncio.run(main())
