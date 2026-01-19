"""
Customer Service Outcome Implementation

This module provides a complete implementation of the cs.resolve outcome type,
demonstrating how to build an AI-powered customer service agent using the
Outcomes Protocol and Claude Agent SDK.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# In production, these would be actual SDK imports
# from anthropic import Anthropic
# from mcp import Client as MCPClient

logger = logging.getLogger("cs_outcome")


@dataclass
class CustomerContext:
    """Customer information retrieved from CRM."""
    customer_id: str
    name: str
    email: str
    tier: str  # bronze, silver, gold, platinum
    lifetime_value: float
    previous_interactions: int
    sentiment_history: List[str]


@dataclass
class OrderContext:
    """Order information retrieved from order system."""
    order_id: str
    status: str
    items: List[Dict[str, Any]]
    total: float
    created_at: str
    shipped_at: Optional[str]
    tracking_number: Optional[str]
    delivery_estimate: Optional[str]


class CustomerServiceOutcome:
    """
    Implements the cs.resolve outcome type.

    This class handles the full lifecycle of resolving a customer service inquiry:
    1. Gathering customer and order context
    2. Understanding the customer's issue
    3. Taking appropriate actions (lookups, refunds, etc.)
    4. Confirming resolution with the customer
    5. Handling escalation when needed
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_latency = config.get('max_latency_seconds', 300)
        self.max_refund = config.get('tools', {}).get('limits', {}).get(
            'orders.process_refund', {}
        ).get('max_amount', 50)
        self.allowed_discount_codes = config.get('tools', {}).get('limits', {}).get(
            'orders.apply_discount', {}
        ).get('allowed_codes', [])

        # MCP clients would be initialized here
        self.crm_client = None
        self.orders_client = None
        self.knowledge_client = None

        # Tracking
        self.actions_taken = []
        self.tools_called = []

    async def execute(
        self,
        request_id: str,
        objective: str,
        customer_id: str,
        initial_message: str,
        conversation_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the customer service resolution.

        Args:
            request_id: Unique request identifier
            objective: What we're trying to achieve
            customer_id: Customer identifier
            initial_message: Customer's initial message
            conversation_history: Previous messages in the conversation

        Returns:
            Dict containing resolution result, actions taken, and metadata
        """
        start_time = datetime.utcnow()

        try:
            # Step 1: Gather context
            customer = await self._get_customer_context(customer_id)
            orders = await self._get_recent_orders(customer_id)

            # Step 2: Analyze the inquiry
            analysis = await self._analyze_inquiry(
                initial_message,
                customer,
                orders,
                conversation_history or []
            )

            # Step 3: Check for escalation triggers
            escalation_trigger = self._check_escalation_triggers(analysis, customer)
            if escalation_trigger:
                return await self._handle_escalation(
                    request_id, escalation_trigger, customer, analysis
                )

            # Step 4: Resolve the issue
            resolution = await self._resolve_issue(
                analysis['issue_type'],
                analysis['details'],
                customer,
                orders
            )

            # Step 5: Generate response and confirm resolution
            response_message = await self._generate_response(
                resolution,
                customer,
                analysis
            )

            # Calculate metrics
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds()

            return {
                "status": "completed",
                "result": {
                    "resolution": resolution['summary'],
                    "response_message": response_message,
                    "issue_type": analysis['issue_type'],
                },
                "artifacts": [
                    {
                        "type": "message",
                        "content": response_message,
                    }
                ],
                "actions_taken": self.actions_taken,
                "tools_called": self.tools_called,
                "metrics": {
                    "latency_seconds": latency,
                    "tokens_used": resolution.get('tokens_used', 0),
                    "customer_tier": customer.tier,
                },
            }

        except Exception as e:
            logger.error(f"Error in customer service outcome: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "actions_taken": self.actions_taken,
            }

    async def _get_customer_context(self, customer_id: str) -> CustomerContext:
        """Retrieve customer information from CRM."""
        self._log_tool_call("crm.get_customer", {"customer_id": customer_id})

        # In production, this would call the CRM MCP server
        # customer_data = await self.crm_client.call("get_customer", customer_id=customer_id)

        # Simulated response
        return CustomerContext(
            customer_id=customer_id,
            name="Jane Smith",
            email="jane.smith@example.com",
            tier="gold",
            lifetime_value=2500.00,
            previous_interactions=12,
            sentiment_history=["positive", "neutral", "positive"]
        )

    async def _get_recent_orders(self, customer_id: str) -> List[OrderContext]:
        """Retrieve recent orders for customer."""
        self._log_tool_call("orders.get_order_history", {"customer_id": customer_id})

        # Simulated response
        return [
            OrderContext(
                order_id="ORD-12345",
                status="shipped",
                items=[{"name": "Widget Pro", "quantity": 2, "price": 49.99}],
                total=99.98,
                created_at="2025-01-10T10:00:00Z",
                shipped_at="2025-01-12T14:00:00Z",
                tracking_number="TRK123456789",
                delivery_estimate="2025-01-18"
            )
        ]

    async def _analyze_inquiry(
        self,
        message: str,
        customer: CustomerContext,
        orders: List[OrderContext],
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze the customer's inquiry to understand intent."""
        # In production, this would use Claude to analyze the message

        # Simulated analysis
        message_lower = message.lower()

        if "where" in message_lower and "order" in message_lower:
            return {
                "issue_type": "order_tracking",
                "details": {
                    "order_id": orders[0].order_id if orders else None,
                },
                "sentiment": "neutral",
                "urgency": "normal",
                "confidence": 0.95,
            }
        elif "refund" in message_lower:
            return {
                "issue_type": "refund_request",
                "details": {
                    "reason": "customer_request",
                },
                "sentiment": "slightly_negative",
                "urgency": "normal",
                "confidence": 0.88,
            }
        elif "speak to" in message_lower or "human" in message_lower:
            return {
                "issue_type": "escalation_request",
                "details": {},
                "sentiment": "frustrated",
                "urgency": "high",
                "confidence": 1.0,
            }
        else:
            return {
                "issue_type": "general_inquiry",
                "details": {},
                "sentiment": "neutral",
                "urgency": "normal",
                "confidence": 0.75,
            }

    def _check_escalation_triggers(
        self,
        analysis: Dict[str, Any],
        customer: CustomerContext
    ) -> Optional[str]:
        """Check if any escalation triggers are met."""
        # Explicit request
        if analysis['issue_type'] == 'escalation_request':
            return "explicit_request"

        # Low confidence
        if analysis['confidence'] < 0.7:
            return "confidence_threshold"

        # Frustrated sentiment + high-value customer
        if analysis['sentiment'] == 'frustrated' and customer.tier in ['gold', 'platinum']:
            return "vip_frustrated"

        return None

    async def _handle_escalation(
        self,
        request_id: str,
        trigger: str,
        customer: CustomerContext,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle escalation to human agent."""
        self._log_action("escalate_to_human", {"trigger": trigger})

        # Generate handoff summary
        summary = {
            "customer": {
                "name": customer.name,
                "tier": customer.tier,
                "lifetime_value": customer.lifetime_value,
            },
            "issue": analysis['issue_type'],
            "sentiment": analysis['sentiment'],
            "escalation_reason": trigger,
            "recommended_action": self._get_escalation_recommendation(trigger, analysis),
        }

        return {
            "status": "escalated",
            "escalation": {
                "trigger": trigger,
                "summary": summary,
            },
            "actions_taken": self.actions_taken,
        }

    def _get_escalation_recommendation(
        self,
        trigger: str,
        analysis: Dict[str, Any]
    ) -> str:
        """Get recommended action for human agent."""
        recommendations = {
            "explicit_request": "Customer explicitly requested human assistance. Acknowledge and assist.",
            "confidence_threshold": "AI was uncertain about resolution. Review context and resolve.",
            "vip_frustrated": "High-value customer is frustrated. Consider goodwill gesture.",
        }
        return recommendations.get(trigger, "Review and resolve customer issue.")

    async def _resolve_issue(
        self,
        issue_type: str,
        details: Dict[str, Any],
        customer: CustomerContext,
        orders: List[OrderContext]
    ) -> Dict[str, Any]:
        """Resolve the customer's issue based on type."""
        if issue_type == "order_tracking":
            return await self._resolve_order_tracking(details, orders)
        elif issue_type == "refund_request":
            return await self._resolve_refund_request(details, orders, customer)
        else:
            return await self._resolve_general_inquiry(details, customer)

    async def _resolve_order_tracking(
        self,
        details: Dict[str, Any],
        orders: List[OrderContext]
    ) -> Dict[str, Any]:
        """Resolve order tracking inquiry."""
        order = orders[0] if orders else None
        if not order:
            return {
                "summary": "No recent orders found",
                "action": "inform_no_orders",
            }

        self._log_tool_call("orders.get_shipment_status", {"order_id": order.order_id})
        self._log_action("provided_tracking_info", {"order_id": order.order_id})

        return {
            "summary": f"Provided tracking information for order {order.order_id}",
            "action": "provided_tracking",
            "data": {
                "order_id": order.order_id,
                "status": order.status,
                "tracking_number": order.tracking_number,
                "delivery_estimate": order.delivery_estimate,
            }
        }

    async def _resolve_refund_request(
        self,
        details: Dict[str, Any],
        orders: List[OrderContext],
        customer: CustomerContext
    ) -> Dict[str, Any]:
        """Resolve refund request."""
        order = orders[0] if orders else None
        if not order:
            return {
                "summary": "No eligible orders for refund",
                "action": "no_refund_eligible",
            }

        # Check if refund amount is within limits
        if order.total > self.max_refund:
            self._log_action("refund_exceeds_limit", {
                "amount": order.total,
                "limit": self.max_refund
            })
            # Offer partial refund or escalate
            return {
                "summary": f"Offered {self.max_refund} refund (max allowed), escalating for remainder",
                "action": "partial_refund_offered",
                "data": {
                    "offered_amount": self.max_refund,
                    "full_amount": order.total,
                }
            }

        # Process the refund
        self._log_tool_call("orders.process_refund", {
            "order_id": order.order_id,
            "amount": order.total,
            "reason": details.get('reason', 'customer_request')
        })
        self._log_action("refund_processed", {"amount": order.total})

        return {
            "summary": f"Processed full refund of ${order.total:.2f}",
            "action": "refund_processed",
            "data": {
                "order_id": order.order_id,
                "refund_amount": order.total,
            }
        }

    async def _resolve_general_inquiry(
        self,
        details: Dict[str, Any],
        customer: CustomerContext
    ) -> Dict[str, Any]:
        """Resolve general inquiry using knowledge base."""
        self._log_tool_call("knowledge.search_articles", {"query": "general help"})

        return {
            "summary": "Provided helpful information from knowledge base",
            "action": "provided_information",
        }

    async def _generate_response(
        self,
        resolution: Dict[str, Any],
        customer: CustomerContext,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate a friendly response message."""
        # In production, Claude would generate this based on context

        action = resolution['action']

        if action == "provided_tracking":
            data = resolution['data']
            return (
                f"Hi {customer.name}! Great news - your order {data['order_id']} is on its way! "
                f"It's currently {data['status']} and should arrive by {data['delivery_estimate']}. "
                f"You can track it with tracking number: {data['tracking_number']}. "
                f"Is there anything else I can help you with?"
            )
        elif action == "refund_processed":
            data = resolution['data']
            return (
                f"I've processed a refund of ${data['refund_amount']:.2f} for order {data['order_id']}. "
                f"You should see this back on your original payment method within 5-7 business days. "
                f"Is there anything else I can help you with today?"
            )
        elif action == "partial_refund_offered":
            data = resolution['data']
            return (
                f"I can immediately process a ${data['offered_amount']:.2f} refund for you. "
                f"For the remaining amount, I'll connect you with a specialist who can help further. "
                f"Would you like me to proceed with the partial refund now?"
            )
        else:
            return (
                f"Thank you for reaching out, {customer.name}! "
                f"I've found some helpful information for you. "
                f"Is there anything specific you'd like to know more about?"
            )

    def _log_tool_call(self, tool: str, params: Dict[str, Any]):
        """Log a tool call."""
        self.tools_called.append({
            "tool": tool,
            "params": params,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    def _log_action(self, action: str, details: Dict[str, Any]):
        """Log an action taken."""
        self.actions_taken.append({
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })


# Example usage
async def main():
    config = {
        "max_latency_seconds": 300,
        "tools": {
            "limits": {
                "orders.process_refund": {"max_amount": 50},
                "orders.apply_discount": {"allowed_codes": ["SORRY10", "LOYALTY15"]},
            }
        }
    }

    outcome = CustomerServiceOutcome(config)

    result = await outcome.execute(
        request_id="req_test123",
        objective="Resolve customer inquiry",
        customer_id="cust_abc123",
        initial_message="Where is my order? I ordered it last week and haven't received it yet."
    )

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
