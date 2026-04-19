"""
base.py — InstanodeToolSpec.

LlamaIndex's convention for integrations is a ToolSpec class that exposes
methods; ``to_tool_list()`` converts every method into a FunctionTool with
a schema inferred from type hints + docstring. This is the canonical shape
for ``llama-index-tools-*`` packages.
"""

from __future__ import annotations

from typing import List, Optional

from llama_index.core.tools.tool_spec.base import BaseToolSpec

import instanode


class InstanodeToolSpec(BaseToolSpec):
    """
    LlamaIndex tool spec that exposes instanode.dev provisioning endpoints.

    Parameters
    ----------
    api_key:
        Optional bearer JWT (or ``INSTANODE_API_KEY``). Without one the spec
        provisions anonymously (free tier, 24h TTL resources).
    base_url:
        Override the API base URL (defaults to ``https://api.instanode.dev``).
    """

    # Names of methods on this class that should be exposed as agent tools.
    # LlamaIndex reads this to know which methods are tools vs helpers.
    spec_functions = [
        "provision_postgres",
        "provision_webhook",
        "list_resources",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self._client = instanode.Client(api_key=api_key, base_url=base_url)

    # ------------------------------------------------------------------
    # Exposed tools
    # ------------------------------------------------------------------

    def provision_postgres(self, name: str) -> str:
        """
        Provision a new Postgres database and return its connection URL.

        Use when the task needs to store structured data, run SQL, or hold
        vector embeddings (pgvector is pre-installed). The returned DSN is a
        standard postgres:// URL usable with psycopg, asyncpg, SQLAlchemy,
        Prisma, etc. Free-tier databases expire in 24 hours.

        :param name: Short kebab-case label (required, 1-120 chars), shown
            in the instanode dashboard.
        """
        try:
            res = self._client.provision_database(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return (
            f"Postgres ready. DSN: {res.connection_url} "
            f"(tier={res.tier}, storage_mb={res.limits.storage_mb}, "
            f"expires_in={res.limits.expires_in or 'never'})"
        )

    def provision_webhook(self, name: str) -> str:
        """
        Provision a webhook receiver URL.

        Use for incoming HTTP callbacks (GitHub webhooks, Stripe events,
        Slack slash-commands, etc.). The URL accepts POSTs and stores the
        recent request bodies for inspection.

        :param name: Short label for the webhook (required).
        """
        try:
            res = self._client.provision_webhook(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return (
            f"Webhook URL: {res.connection_url} "
            f"(tier={res.tier}, expires_in={res.limits.expires_in or 'never'})"
        )

    def list_resources(self) -> str:
        """
        List every instanode.dev resource owned by the current API key.

        Requires ``INSTANODE_API_KEY``. Use before provisioning a new
        resource to check if a suitable one already exists.
        """
        try:
            resources = self._client.list_resources()
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        if not resources:
            return "No resources."
        lines: List[str] = [
            f"- {r.resource_type} ({r.tier}) token={r.token} created={r.created_at}"
            for r in resources
        ]
        return "Resources:\n" + "\n".join(lines)
