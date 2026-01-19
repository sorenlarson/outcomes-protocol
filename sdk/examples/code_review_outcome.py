"""
Code Review Outcome Implementation

This module provides a complete implementation of the code.review outcome type,
demonstrating how to build an AI-powered code review agent using the
Outcomes Protocol and Claude Agent SDK.

Inspired by tools like Greptile, this implementation:
- Analyzes PR diffs for bugs, security issues, and style violations
- Provides actionable inline comments
- Integrates with codebase context for better understanding
- Handles escalation for complex or sensitive changes
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("code_review_outcome")


class IssueSeverity(Enum):
    """Severity levels for review findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(Enum):
    """Categories of review findings."""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"


@dataclass
class ReviewFinding:
    """A single finding from the code review."""
    id: str
    category: IssueCategory
    severity: IssueSeverity
    file_path: str
    line_start: int
    line_end: int
    title: str
    description: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    confidence: float = 0.9


@dataclass
class PRContext:
    """Context about the pull request being reviewed."""
    pr_number: int
    title: str
    description: str
    author: str
    base_branch: str
    head_branch: str
    files_changed: int
    additions: int
    deletions: int
    commits: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FileChange:
    """A changed file in the PR."""
    path: str
    status: str  # added, modified, deleted, renamed
    additions: int
    deletions: int
    patch: str
    previous_content: Optional[str] = None
    new_content: Optional[str] = None


class CodeReviewOutcome:
    """
    Implements the code.review outcome type.

    This class handles the full lifecycle of reviewing a pull request:
    1. Fetching PR diff and context
    2. Analyzing code for issues across multiple dimensions
    3. Generating actionable review comments
    4. Deciding on review outcome (approve, request changes, comment)
    5. Handling escalation for sensitive changes
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_latency = config.get('max_latency_seconds', 300)

        # Review configuration
        self.auto_approve_enabled = config.get('auto_approve', {}).get('enabled', False)
        self.auto_approve_conditions = config.get('auto_approve', {}).get('conditions', [])
        self.require_human_for = config.get('require_human_for', [])

        # Tracking
        self.findings: List[ReviewFinding] = []
        self.tools_called = []

    async def execute(
        self,
        request_id: str,
        owner: str,
        repo: str,
        pr_number: int,
        review_focus: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the code review.

        Args:
            request_id: Unique request identifier
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            review_focus: Specific areas to focus on (e.g., ["security", "performance"])

        Returns:
            Dict containing review findings, decision, and metadata
        """
        start_time = datetime.utcnow()
        review_focus = review_focus or ["bugs", "security", "style", "maintainability"]

        try:
            # Step 1: Fetch PR context
            pr_context = await self._get_pr_context(owner, repo, pr_number)

            # Step 2: Fetch file changes
            file_changes = await self._get_file_changes(owner, repo, pr_number)

            # Step 3: Check for escalation triggers
            escalation_trigger = self._check_escalation_triggers(pr_context, file_changes)
            if escalation_trigger:
                return await self._handle_escalation(
                    request_id, escalation_trigger, pr_context
                )

            # Step 4: Analyze each file
            for file_change in file_changes:
                await self._analyze_file(file_change, pr_context, review_focus)

            # Step 5: Determine review decision
            decision = self._determine_decision(pr_context)

            # Step 6: Generate review summary
            summary = self._generate_summary()

            # Calculate metrics
            end_time = datetime.utcnow()
            latency = (end_time - start_time).total_seconds()

            return {
                "status": "completed",
                "result": {
                    "decision": decision['action'],
                    "summary": summary,
                    "findings_count": len(self.findings),
                    "findings_by_severity": self._count_by_severity(),
                },
                "artifacts": [
                    {
                        "type": "review_comments",
                        "content": self._format_findings_as_comments(),
                    },
                    {
                        "type": "review_summary",
                        "content": summary,
                    }
                ],
                "findings": [self._finding_to_dict(f) for f in self.findings],
                "decision": decision,
                "tools_called": self.tools_called,
                "metrics": {
                    "latency_seconds": latency,
                    "files_reviewed": len(file_changes),
                    "lines_analyzed": pr_context.additions + pr_context.deletions,
                },
            }

        except Exception as e:
            logger.error(f"Error in code review outcome: {e}")
            return {
                "status": "failed",
                "error": str(e),
            }

    async def _get_pr_context(self, owner: str, repo: str, pr_number: int) -> PRContext:
        """Fetch PR metadata from GitHub."""
        self._log_tool_call("github.get_pull_request", {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number
        })

        # Simulated response
        return PRContext(
            pr_number=pr_number,
            title="Add user authentication endpoint",
            description="Implements JWT-based authentication for the API",
            author="developer123",
            base_branch="main",
            head_branch="feature/auth-endpoint",
            files_changed=5,
            additions=245,
            deletions=12,
            commits=[
                {"sha": "abc123", "message": "Add auth middleware"},
                {"sha": "def456", "message": "Implement JWT validation"},
            ]
        )

    async def _get_file_changes(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> List[FileChange]:
        """Fetch changed files from the PR."""
        self._log_tool_call("github.get_diff", {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number
        })

        # Simulated response
        return [
            FileChange(
                path="src/auth/handler.ts",
                status="added",
                additions=120,
                deletions=0,
                patch="""
+import { Request, Response } from 'express';
+import jwt from 'jsonwebtoken';
+
+export async function authenticate(req: Request, res: Response) {
+  const token = req.headers.authorization?.split(' ')[1];
+
+  if (!token) {
+    return res.status(401).json({ error: 'No token provided' });
+  }
+
+  try {
+    const decoded = jwt.verify(token, process.env.JWT_SECRET);
+    req.user = decoded;
+    return next();
+  } catch (error) {
+    return res.status(401).json({ error: 'Invalid token' });
+  }
+}
+
+export async function login(req: Request, res: Response) {
+  const { email, password } = req.body;
+
+  // TODO: Implement actual user lookup
+  const user = await findUser(email, password);
+
+  if (!user) {
+    return res.status(401).json({ error: 'Invalid credentials' });
+  }
+
+  const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET);
+  return res.json({ token });
+}
""",
            ),
            FileChange(
                path="src/auth/middleware.ts",
                status="added",
                additions=45,
                deletions=0,
                patch="""
+import { Request, Response, NextFunction } from 'express';
+
+export function requireAuth(req: Request, res: Response, next: NextFunction) {
+  if (!req.user) {
+    return res.status(401).json({ error: 'Authentication required' });
+  }
+  next();
+}
""",
            ),
            FileChange(
                path="src/routes/index.ts",
                status="modified",
                additions=10,
                deletions=2,
                patch="""
@@ -5,6 +5,14 @@ import { Router } from 'express';
+import { authenticate, login } from '../auth/handler';
+import { requireAuth } from '../auth/middleware';

 const router = Router();

+// Auth routes
+router.post('/login', login);
+router.use(authenticate);
+
 // Protected routes
+router.get('/profile', requireAuth, getProfile);
""",
            ),
        ]

    def _check_escalation_triggers(
        self,
        pr_context: PRContext,
        file_changes: List[FileChange]
    ) -> Optional[str]:
        """Check if the PR should be escalated to human review."""
        # Large PR
        if pr_context.additions + pr_context.deletions > 1000:
            return "large_pr"

        # Sensitive paths
        sensitive_paths = ["security", "auth", "crypto", "payment"]
        for file in file_changes:
            for sensitive in sensitive_paths:
                if sensitive in file.path.lower():
                    if "changes_to_security_critical" in self.require_human_for:
                        return "security_sensitive"

        # Changes to critical config
        critical_files = [".env", "config/production", "secrets"]
        for file in file_changes:
            for critical in critical_files:
                if critical in file.path.lower():
                    return "critical_config"

        return None

    async def _handle_escalation(
        self,
        request_id: str,
        trigger: str,
        pr_context: PRContext
    ) -> Dict[str, Any]:
        """Handle escalation to human reviewers."""
        recommendations = {
            "large_pr": "Large PR - consider splitting into smaller changes",
            "security_sensitive": "Changes to security-critical code require human review",
            "critical_config": "Changes to production configuration require human approval",
        }

        return {
            "status": "escalated",
            "escalation": {
                "trigger": trigger,
                "reason": recommendations.get(trigger, "Human review required"),
                "pr_context": {
                    "title": pr_context.title,
                    "files_changed": pr_context.files_changed,
                    "additions": pr_context.additions,
                },
            },
            "partial_analysis": {
                "findings": [self._finding_to_dict(f) for f in self.findings],
            },
        }

    async def _analyze_file(
        self,
        file_change: FileChange,
        pr_context: PRContext,
        review_focus: List[str]
    ):
        """Analyze a single file for issues."""
        self._log_tool_call("analyze_code", {"path": file_change.path})

        # In production, this would use Claude to analyze the code
        # Here we simulate finding some issues

        # Security analysis
        if "security" in review_focus:
            await self._check_security_issues(file_change)

        # Bug detection
        if "bugs" in review_focus:
            await self._check_bugs(file_change)

        # Style issues
        if "style" in review_focus:
            await self._check_style(file_change)

        # Maintainability
        if "maintainability" in review_focus:
            await self._check_maintainability(file_change)

    async def _check_security_issues(self, file_change: FileChange):
        """Check for security vulnerabilities."""
        patch = file_change.patch

        # Check for hardcoded secrets
        if "process.env" not in patch and ("secret" in patch.lower() or "password" in patch.lower()):
            self.findings.append(ReviewFinding(
                id=f"sec_{len(self.findings)}",
                category=IssueCategory.SECURITY,
                severity=IssueSeverity.CRITICAL,
                file_path=file_change.path,
                line_start=1,
                line_end=1,
                title="Potential hardcoded secret",
                description="Detected potential hardcoded secret or password. Use environment variables instead.",
                suggestion="Move secrets to environment variables and use process.env",
            ))

        # Check for missing token expiration
        if "jwt.sign" in patch and "expiresIn" not in patch:
            self.findings.append(ReviewFinding(
                id=f"sec_{len(self.findings)}",
                category=IssueCategory.SECURITY,
                severity=IssueSeverity.HIGH,
                file_path=file_change.path,
                line_start=30,
                line_end=30,
                title="JWT token missing expiration",
                description="JWT tokens should have an expiration time to limit the window of token compromise.",
                suggestion="Add expiresIn option: jwt.sign(payload, secret, { expiresIn: '1h' })",
                confidence=0.95,
            ))

    async def _check_bugs(self, file_change: FileChange):
        """Check for potential bugs."""
        patch = file_change.patch

        # Check for missing await
        if "async" in patch and "findUser" in patch:
            if "await findUser" not in patch:
                self.findings.append(ReviewFinding(
                    id=f"bug_{len(self.findings)}",
                    category=IssueCategory.BUG,
                    severity=IssueSeverity.HIGH,
                    file_path=file_change.path,
                    line_start=22,
                    line_end=22,
                    title="Missing await on async function",
                    description="The findUser function appears to be async but is not awaited.",
                    suggestion="Add await: const user = await findUser(email, password);",
                    confidence=0.85,
                ))

    async def _check_style(self, file_change: FileChange):
        """Check for style issues."""
        patch = file_change.patch

        # Check for TODO comments
        if "TODO" in patch:
            self.findings.append(ReviewFinding(
                id=f"style_{len(self.findings)}",
                category=IssueCategory.DOCUMENTATION,
                severity=IssueSeverity.LOW,
                file_path=file_change.path,
                line_start=21,
                line_end=21,
                title="TODO comment in production code",
                description="TODO comment suggests incomplete implementation.",
                suggestion="Implement the actual user lookup or create a follow-up issue",
                confidence=1.0,
            ))

    async def _check_maintainability(self, file_change: FileChange):
        """Check for maintainability issues."""
        # Check for missing error handling
        if "catch" in file_change.patch:
            self.findings.append(ReviewFinding(
                id=f"maint_{len(self.findings)}",
                category=IssueCategory.MAINTAINABILITY,
                severity=IssueSeverity.MEDIUM,
                file_path=file_change.path,
                line_start=15,
                line_end=15,
                title="Generic error handling",
                description="Error is caught but not logged. Consider adding logging for debugging.",
                suggestion="Add logging: console.error('Token verification failed:', error);",
                confidence=0.75,
            ))

    def _determine_decision(self, pr_context: PRContext) -> Dict[str, Any]:
        """Determine the review decision based on findings."""
        critical_count = len([f for f in self.findings if f.severity == IssueSeverity.CRITICAL])
        high_count = len([f for f in self.findings if f.severity == IssueSeverity.HIGH])

        # Check auto-approve conditions
        if self.auto_approve_enabled:
            if critical_count == 0 and high_count == 0:
                if self._check_auto_approve_conditions(pr_context):
                    return {
                        "action": "approve",
                        "reason": "No critical or high severity issues found",
                    }

        # Request changes if critical issues
        if critical_count > 0:
            return {
                "action": "request_changes",
                "reason": f"Found {critical_count} critical issue(s) that must be addressed",
            }

        # Request changes if multiple high issues
        if high_count >= 2:
            return {
                "action": "request_changes",
                "reason": f"Found {high_count} high severity issues",
            }

        # Comment with suggestions
        if len(self.findings) > 0:
            return {
                "action": "comment",
                "reason": "Found issues to discuss, but not blocking",
            }

        return {
            "action": "approve",
            "reason": "No significant issues found",
        }

    def _check_auto_approve_conditions(self, pr_context: PRContext) -> bool:
        """Check if auto-approve conditions are met."""
        for condition in self.auto_approve_conditions:
            if condition == "lines_changed < 50":
                if pr_context.additions + pr_context.deletions >= 50:
                    return False
            elif condition == "no_security_findings":
                if any(f.category == IssueCategory.SECURITY for f in self.findings):
                    return False
            elif condition == "all_tests_pass":
                # Would check CI status
                pass
        return True

    def _generate_summary(self) -> str:
        """Generate a human-readable review summary."""
        by_severity = self._count_by_severity()

        summary_parts = ["## Code Review Summary\n"]

        if not self.findings:
            summary_parts.append("No issues found. Code looks good!\n")
        else:
            summary_parts.append(f"Found **{len(self.findings)}** issue(s):\n")
            for severity, count in by_severity.items():
                if count > 0:
                    emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}.get(severity, "")
                    summary_parts.append(f"- {emoji} {severity.title()}: {count}\n")

            summary_parts.append("\n### Key Findings\n")
            for finding in self.findings[:5]:  # Top 5 findings
                summary_parts.append(f"- **{finding.title}** ({finding.file_path}:{finding.line_start})\n")

        return "".join(summary_parts)

    def _count_by_severity(self) -> Dict[str, int]:
        """Count findings by severity."""
        counts = {s.value: 0 for s in IssueSeverity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return counts

    def _format_findings_as_comments(self) -> List[Dict[str, Any]]:
        """Format findings as GitHub review comments."""
        comments = []
        for finding in self.findings:
            comment = {
                "path": finding.file_path,
                "line": finding.line_start,
                "body": f"**{finding.severity.value.upper()}**: {finding.title}\n\n{finding.description}",
            }
            if finding.suggestion:
                comment["body"] += f"\n\n**Suggestion**: {finding.suggestion}"
            comments.append(comment)
        return comments

    def _finding_to_dict(self, finding: ReviewFinding) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "id": finding.id,
            "category": finding.category.value,
            "severity": finding.severity.value,
            "file_path": finding.file_path,
            "line_start": finding.line_start,
            "line_end": finding.line_end,
            "title": finding.title,
            "description": finding.description,
            "suggestion": finding.suggestion,
            "confidence": finding.confidence,
        }

    def _log_tool_call(self, tool: str, params: Dict[str, Any]):
        """Log a tool call."""
        self.tools_called.append({
            "tool": tool,
            "params": params,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })


# Example usage
async def main():
    config = {
        "max_latency_seconds": 300,
        "auto_approve": {
            "enabled": True,
            "conditions": [
                "lines_changed < 50",
                "no_security_findings",
                "all_tests_pass",
            ]
        },
        "require_human_for": [
            "changes_to_security_critical",
            "changes_to_auth",
            "large_prs > 500_lines",
        ]
    }

    outcome = CodeReviewOutcome(config)

    result = await outcome.execute(
        request_id="req_test456",
        owner="acme-corp",
        repo="web-platform",
        pr_number=456,
        review_focus=["security", "bugs", "style", "maintainability"]
    )

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
