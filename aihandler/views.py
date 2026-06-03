import os
import sys
import json
import asyncio

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from .models import Product, ResponseModel
from .serializers import ProductSerializer
from .main import rag_index


# ---------------------------------------------------------------------------
# MCP client – loaded once per worker, kept alive for the workerʼs lifetime
# ---------------------------------------------------------------------------
class _MCPManager:
    def __init__(self):
        self._tools = None
        self._stdio_ctx = None
        self._session_ctx = None

    async def _start(self):
        from langchain_mcp_adapters.tools import load_mcp_tools
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(os.path.dirname(__file__), "mcp_server.py")],
        )

        self._stdio_ctx = stdio_client(server_params)
        read, write = await self._stdio_ctx.__aenter__()

        self._session_ctx = ClientSession(read, write)
        session = await self._session_ctx.__aenter__()
        await session.initialize()

        self._tools = await load_mcp_tools(session)

    @property
    def tools(self):
        return self._tools or []

    async def close(self):
        if self._session_ctx:
            await self._session_ctx.__aexit__(None, None, None)
        if self._stdio_ctx:
            await self._stdio_ctx.__aexit__(None, None, None)


_mcp_manager: _MCPManager | None = None


def _get_mcp_tools():
    """Return MCP tools, initialising the connection on first call."""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = _MCPManager()
        asyncio.run(_mcp_manager._start())
    return _mcp_manager.tools


def _build_llm() -> ChatOpenAI:
    """Create a DeepSeek chat model configured via environment variables."""
    return ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        api_key=os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY", "")),
        temperature=0.7,
    )


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------
class GetAllProduct(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ChatCommerceService(APIView):
    def post(self, request):
        try:
            input_user = request.data["input_user"]

            # -- RAG retrieval -------------------------------------------------
            retrieved_product = rag_index.retrieve_documents(input_user, k=5)
            product_context = "\n\n".join(
                [
                    f"Product Name: {json.loads(doc)['product_name']}\n"
                    f"Description: {json.loads(doc)['description']}\n"
                    f"Price: {json.loads(doc)['retail_price']}\n"
                    f"URL: {json.loads(doc)['product_url']}\n"
                    f"Brand: {json.loads(doc)['brand']}"
                    for doc in retrieved_product
                ]
            )

            # -- LLM (DeepSeek) + MCP tools -----------------------------------
            llm = _build_llm()
            mcp_tools = _get_mcp_tools()
            llm_with_tools = llm.bind_tools(mcp_tools)

            # -- Parser --------------------------------------------------------
            parser = JsonOutputParser(pydantic_object=ResponseModel)

            # -- Build message list -------------------------------------------
            system_msg = SystemMessage(
                content=(
                    "You are an AI shopping assistant. You have access to:\n"
                    "1. A pre-retrieved list of relevant products shown below.\n"
                    "2. MCP tools (product_search, filter_by_price, get_product_details) "
                    "for additional lookups.\n\n"
                    "Use the tools when the retrieved context is insufficient. "
                    "Always return your final answer as a clean JSON object "
                    "(no markdown fences, no comments) matching this schema:\n"
                    f"{parser.get_format_instructions()}\n\n"
                    f"<RETRIEVED_PRODUCTS>\n{product_context}\n</RETRIEVED_PRODUCTS>"
                )
            )
            human_msg = HumanMessage(content=input_user)
            messages = [system_msg, human_msg]

            # -- First LLM call (may request tool calls) ----------------------
            response = llm_with_tools.invoke(messages)

            # -- Handle tool calls if the model made any ----------------------
            if response.tool_calls:
                tools_by_name = {t.name: t for t in mcp_tools}
                messages.append(response)  # AIMessage with tool_calls
                for tc in response.tool_calls:
                    tool = tools_by_name.get(tc["name"])
                    if tool:
                        tool_result = str(tool.invoke(tc["args"]))
                    else:
                        tool_result = f"Unknown tool: {tc['name']}"
                    messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tc["id"])
                    )

                # Final call to get the structured answer
                final_response = llm.invoke(messages)
            else:
                final_response = response

            # -- Parse JSON ---------------------------------------------------
            raw_response = parser.invoke(final_response)

            return Response(
                {"status": 200, "message": "Success", "data": raw_response},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": 500, "message": "Internal server error", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
