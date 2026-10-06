"""Tests for the cost-center-agent.

AI Core / LLM is NOT available in the test environment, so the LLM invocation
(`SampleAgent._invoke_with_fallback`) is patched. MCP tools come from the real
mcp-mock.json via get_mcp_tools() under IBD_TESTING=1 (set by conftest.py).
"""
import json

import pytest
from langchain_core.messages import AIMessage


# ---- MCP mock tool loading (unit) -------------------------------------------

@pytest.mark.asyncio
async def test_mock_tools_loaded_from_mcp_mock(add_agent_to_path):
    """get_mcp_tools() returns the two cost center tools from mcp-mock.json."""
    from mcp_providers.agw import get_mcp_tools

    tools = await get_mcp_tools()
    names = {t.name for t in tools}
    assert "list_a_costcenter_2_for_sap_self" in names
    assert "count_a_costcenter_2_for_sap_self" in names


@pytest.mark.asyncio
async def test_count_tool_returns_deterministic_total(add_agent_to_path):
    """The count tool returns the deterministic mock total used for the 'how many' answer."""
    from mcp_providers.agw import get_mcp_tools

    tools = {t.name: t for t in await get_mcp_tools()}
    result = await tools["count_a_costcenter_2_for_sap_self"].ainvoke({})
    # StructuredTool coroutine returns the JSON-encoded mock_response.
    assert json.loads(result) == 142


@pytest.mark.asyncio
async def test_list_tool_supports_creation_date_ranking(add_agent_to_path):
    """The list tool returns rows with CostCenterCreationDate so top-5 ranking is possible.

    CE_COSTCENTER_0001 has no numeric spend field, so 'top 5' ranks by creation date
    (most recently created first) — the chosen available-field substitute.
    """
    from mcp_providers.agw import get_mcp_tools

    tools = {t.name: t for t in await get_mcp_tools()}
    result = json.loads(await tools["list_a_costcenter_2_for_sap_self"].ainvoke({}))
    rows = result["results"]
    assert len(rows) >= 5
    assert all("CostCenterCreationDate" in r for r in rows)
    # No numeric spend field is present — ranking must use creation date, not spend.
    assert not any(k.lower().endswith("actualamount") or "spend" in k.lower() for k in rows[0])

    def _ts(r):
        return int(r["CostCenterCreationDate"][6:-2])

    top5 = sorted(rows, key=_ts, reverse=True)[:5]
    assert len(top5) == 5
    # Most recently created is first.
    assert _ts(top5[0]) > _ts(top5[-1])


# ---- End-to-end stream() flow (integration, LLM patched) --------------------

@pytest.mark.asyncio
async def test_stream_count_flow_delivers_answer(add_agent_to_path, monkeypatch):
    """Count question flows through stream() to a completed answer; LLM is mocked."""
    import agent as agent_mod
    from mcp_providers.agw import get_mcp_tools

    async def fake_invoke(self, **kwargs):
        return {"messages": [AIMessage(content="You have 142 cost centers in total.")]}

    monkeypatch.setattr(agent_mod.SampleAgent, "_invoke_with_fallback", fake_invoke)

    a = agent_mod.SampleAgent()
    tools = await get_mcp_tools()
    chunks = [c async for c in a.stream("How many cost centers do we have?", "ctx-1", tools=tools)]

    final = chunks[-1]
    assert final["is_task_complete"] is True
    assert "142" in final["content"]


@pytest.mark.asyncio
async def test_stream_top5_flow_delivers_answer(add_agent_to_path, monkeypatch):
    """Top-5 question flows through stream() to a completed answer; LLM is mocked."""
    import agent as agent_mod
    from mcp_providers.agw import get_mcp_tools

    async def fake_invoke(self, **kwargs):
        return {"messages": [AIMessage(content="Top 5 cost centers by creation date: Facilities, Sales EMEA, Research & Development, Human Resources, Finance.")]}

    monkeypatch.setattr(agent_mod.SampleAgent, "_invoke_with_fallback", fake_invoke)

    a = agent_mod.SampleAgent()
    tools = await get_mcp_tools()
    chunks = [c async for c in a.stream("Show me the top 5 cost centers", "ctx-3", tools=tools)]

    final = chunks[-1]
    assert final["is_task_complete"] is True
    assert "Facilities" in final["content"]


@pytest.mark.asyncio
async def test_stream_handles_llm_failure(add_agent_to_path, monkeypatch):
    """If the LLM call raises, stream() still completes with an error message, not a crash."""
    import agent as agent_mod

    async def boom(self, **kwargs):
        raise RuntimeError("AI Core unavailable")

    monkeypatch.setattr(agent_mod.SampleAgent, "_invoke_with_fallback", boom)

    a = agent_mod.SampleAgent()
    chunks = [c async for c in a.stream("How many cost centers?", "ctx-2", tools=[])]

    final = chunks[-1]
    assert final["is_task_complete"] is True
    assert "error" in final["content"].lower()
