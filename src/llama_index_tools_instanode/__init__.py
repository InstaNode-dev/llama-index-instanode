"""
llama-index-tools-instanode — LlamaIndex tool spec for instanode.dev.

Lets a LlamaIndex agent provision ephemeral Postgres databases or webhook
receivers mid-task via a single HTTP call to instanode.dev.

Quick start
-----------
    from llama_index.agent.openai import OpenAIAgent
    from llama_index_tools_instanode import InstanodeToolSpec

    tool_spec = InstanodeToolSpec()
    agent = OpenAIAgent.from_tools(tool_spec.to_tool_list())

    agent.chat("Spin up a Postgres DB for my side project and create a users table.")

Authentication
--------------
Free tier works without credentials. For paid-tier limits, set
INSTANODE_API_KEY in your environment or pass api_key= when constructing
the spec.

Links
-----
- Homepage:   https://instanode.dev
- Python SDK: https://pypi.org/project/instanode/
"""

from llama_index_tools_instanode.base import InstanodeToolSpec

__version__ = "0.2.0"
__all__ = ["InstanodeToolSpec"]
