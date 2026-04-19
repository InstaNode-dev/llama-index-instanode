# llama-index-tools-instanode

LlamaIndex tool spec for [instanode.dev](https://instanode.dev). Lets a
LlamaIndex agent provision ephemeral Postgres databases + webhook receivers
mid-task. No Docker, no account for the free tier.

```
pip install llama-index-tools-instanode
```

## Usage

```python
from llama_index.agent.openai import OpenAIAgent
from llama_index_tools_instanode import InstanodeToolSpec

tool_spec = InstanodeToolSpec()
agent = OpenAIAgent.from_tools(tool_spec.to_tool_list(), verbose=True)

agent.chat(
    "Stand up a Postgres DB with pgvector, then store this embedding in it: "
    "<embedding>."
)
```

The agent gets four tools:

- `provision_postgres(name?)` → `postgres://` DSN (pgvector pre-installed).
- `provision_webhook(name?)` → HTTPS receiver URL.
- `provision_mongo(name?)` → `mongodb://` URI.
- `list_resources()` → enumerate resources owned by the current API key.

### Scoping to specific tools

```python
tool_list = [
    t for t in tool_spec.to_tool_list()
    if t.metadata.name in {"provision_postgres"}
]
```

### Paid-tier credentials

Set `INSTANODE_API_KEY` in your environment, or pass it explicitly:

```python
tool_spec = InstanodeToolSpec(api_key="sk_...")
```

## Tier model

| Tier | Postgres | Webhooks | Persistence |
|---|---|---|---|
| Anonymous (no key) | 10 MB / 2 connections | 100 stored | 24 hours |
| Paid (free signup at instanode.dev) | 500 MB / 5 connections | 1000 stored | Permanent |

## Related

- Python SDK: <https://pypi.org/project/instanode/>
- MCP server (for Claude Code/Cursor): <https://www.npmjs.com/package/@instanode/mcp>
- LangChain variant: <https://pypi.org/project/langchain-instanode/>
- HTTP API reference: <https://instanode.dev/llms.txt>

## License

MIT.
