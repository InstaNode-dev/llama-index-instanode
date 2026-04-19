"""
base.py — InstanodeToolSpec.

LlamaIndex's convention for integrations is a ToolSpec class that exposes
methods; `to_tool_list()` converts every method into a FunctionTool with a
schema inferred from type hints + docstring. This is the canonical shape
for `llama-index-tools-*` packages.
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
        Optional bearer token (or INSTANODE_API_KEY env var). Without one
        the spec provisions anonymously (free tier, 24h TTL).
    base_url:
        Override the API base URL (defaults to https://api.instanode.dev).
    """

    # Names of methods on this class that should be exposed as agent tools.
    # LlamaIndex reads this to know which methods are tools vs helpers.
    spec_functions = [
        "provision_postgres",
        "provision_webhook",
        "provision_mongo",
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

    def provision_postgres(self, name: Optional[str] = None) -> str:
        """
        Provision a new Postgres database and return its connection URL.

        Use when the task needs to store structured data, run SQL, or hold
        vector embeddings (pgvector is pre-installed). The returned DSN is a
        standard postgres:// URL usable with psycopg2, SQLAlchemy, Prisma,
        etc. Free-tier databases expire in 24 hours.

        :param name: Optional human-readable label, shown in the instanode
            dashboard; has no effect on the connection URL.
        """
        try:
            res = self._client.provision_database(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return (
            f"Postgres ready. DSN: {res.connection_url} "
            f"(tier={res.tier}, storage_mb={res.limits.storage_mb}, "
            f"expires_in={res.limits.expires_in})"
        )

    def provision_webhook(self, name: Optional[str] = None) -> str:
        """
        Provision a webhook receiver URL.

        Use for incoming HTTP callbacks (GitHub webhooks, Stripe events,
        Slack slash-commands, etc.). The URL accepts POSTs and stores the
        last 100 requests for inspection.

        :param name: Optional label for the webhook.
        """
        try:
            res = self._client.provision_webhook(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return f"Webhook URL: {res.connection_url} (tier={res.tier})"

    def provision_mongo(self, name: Optional[str] = None) -> str:
        """
        Provision a MongoDB database and return a mongodb:// URI.

        Use for document/JSON-heavy workloads.

        :param name: Optional label for the database.
        """
        try:
            res = self._client.provision_mongodb(name=name)
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        return f"MongoDB URI: {res.connection_url} (tier={res.tier})"

    def list_resources(self) -> str:
        """
        List every instanode.dev resource owned by this token.

        Requires an INSTANODE_API_KEY. Use before provisioning a new
        resource to check if a suitable one already exists.
        """
        try:
            resources = self._client.list_resources()
        except instanode.InstanodeError as exc:
            return f"ERROR: {exc}"
        if not resources:
            return "No resources."
        lines: List[str] = [
            f"- {r.service} ({r.tier}) created {r.created_at}"
            for r in resources
        ]
        return "Resources:\n" + "\n".join(lines)
