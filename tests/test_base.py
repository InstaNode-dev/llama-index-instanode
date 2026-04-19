"""Unit tests for InstanodeToolSpec — client is stubbed, no HTTP."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import instanode
from llama_index_tools_instanode import InstanodeToolSpec


def _fake_result(url: str = "postgres://u:p@h/db") -> SimpleNamespace:
    return SimpleNamespace(
        connection_url=url,
        tier="anonymous",
        limits=SimpleNamespace(storage_mb=10, connections=2, expires_in="24h"),
    )


@patch("llama_index_tools_instanode.base.instanode.Client")
def test_spec_exposes_four_tools(client_cls):
    spec = InstanodeToolSpec()
    tool_list = spec.to_tool_list()
    names = {t.metadata.name for t in tool_list}
    assert names == {
        "provision_postgres",
        "provision_webhook",
        "provision_mongo",
        "list_resources",
    }


@patch("llama_index_tools_instanode.base.instanode.Client")
def test_postgres_returns_dsn(client_cls):
    client = MagicMock()
    client.provision_database.return_value = _fake_result("postgres://ok")
    client_cls.return_value = client
    spec = InstanodeToolSpec()
    assert "postgres://ok" in spec.provision_postgres()


@patch("llama_index_tools_instanode.base.instanode.Client")
def test_postgres_forwards_name(client_cls):
    client = MagicMock()
    client.provision_database.return_value = _fake_result()
    client_cls.return_value = client
    spec = InstanodeToolSpec()
    spec.provision_postgres(name="my-db")
    client.provision_database.assert_called_once_with(name="my-db")


@patch("llama_index_tools_instanode.base.instanode.Client")
def test_error_is_returned_not_raised(client_cls):
    client = MagicMock()
    client.provision_database.side_effect = instanode.InstanodeError(
        429, "rate_limited", "slow down"
    )
    client_cls.return_value = client
    spec = InstanodeToolSpec()
    out = spec.provision_postgres()
    assert out.startswith("ERROR:")
    assert "slow down" in out


@patch("llama_index_tools_instanode.base.instanode.Client")
def test_list_resources_empty(client_cls):
    client = MagicMock()
    client.list_resources.return_value = []
    client_cls.return_value = client
    spec = InstanodeToolSpec()
    assert spec.list_resources() == "No resources."


@patch("llama_index_tools_instanode.base.instanode.Client")
def test_list_resources_formatted(client_cls):
    client = MagicMock()
    client.list_resources.return_value = [
        SimpleNamespace(service="postgres", tier="hobby", created_at="2026-04-19T10:00Z")
    ]
    client_cls.return_value = client
    spec = InstanodeToolSpec()
    out = spec.list_resources()
    assert "postgres" in out and "hobby" in out
