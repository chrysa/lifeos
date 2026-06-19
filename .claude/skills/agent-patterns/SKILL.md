# Skill: Agent patterns — LangGraph + Pydantic AI

## When to invoke
Auto-invoke when: building AI agents, designing LangGraph state machines, defining Pydantic AI tools, writing agent tests, integrating Claude API with stateful workflows (lifeos, ai-aggregator, discord-bot-back).

## 1. State machine design (LangGraph)

### Typed state — always use a dataclass or TypedDict
```python
# agent/state.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

@dataclass
class AgentState:
    messages: Annotated[list[BaseMessage], add_messages] = field(default_factory=list)
    tool_calls_remaining: int = 3
    final_answer: str | None = None
    error: str | None = None
```

### Graph construction — explicit node + edge typing
```python
# agent/graph.py
from langgraph.graph import StateGraph, END
from agent.state import AgentState

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("reason", reason_node)
    graph.add_node("act", act_node)
    graph.add_node("respond", respond_node)

    graph.set_entry_point("reason")
    graph.add_conditional_edges(
        "reason",
        should_act,  # returns "act" | END
        {"act": "act", END: "respond"},
    )
    graph.add_edge("act", "reason")
    graph.add_edge("respond", END)
    return graph

# Compile with checkpointer for persistence
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def get_compiled_graph(pool) -> CompiledGraph:
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()
    return build_graph().compile(checkpointer=checkpointer)
```

### Checkpointer rules
| Environment | Checkpointer |
|---|---|
| Production | `AsyncPostgresSaver` (PostgreSQL 16 on cluster) |
| Tests | `MemorySaver` (no DB required) |
| Local dev | `MemorySaver` or `AsyncSqliteSaver` |

**Rule**: every agent MUST have a checkpointer configured. Stateless agents lose context on restart.

## 2. Tool definition (Pydantic AI)

### Tool with input validation
```python
# agent/tools/search.py
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import ToolDefinition

class SearchInput(BaseModel):
    query: str
    max_results: int = 5

class SearchResult(BaseModel):
    url: str
    snippet: str

agent = Agent("claude-3-5-sonnet-latest")

@agent.tool
async def web_search(ctx: RunContext[None], input: SearchInput) -> list[SearchResult]:
    """Search the web and return relevant results."""
    # implementation
    ...
```

### Structured output — always use Pydantic models
```python
from pydantic import BaseModel
from pydantic_ai import Agent

class AnalysisResult(BaseModel):
    summary: str
    confidence: float
    sources: list[str]

agent: Agent[None, AnalysisResult] = Agent(
    "claude-3-5-sonnet-latest",
    result_type=AnalysisResult,
    system_prompt="You are an analysis assistant.",
)
```

## 3. Agent testing

### Mock LLM calls — never call real APIs in tests
```python
# tests/agent/test_graph.py
import pytest
from unittest.mock import AsyncMock
from pydantic_ai.models.test import TestModel
from langgraph.checkpoint.memory import MemorySaver

from agent.graph import build_graph
from agent.state import AgentState

@pytest.fixture
def test_graph():
    graph = build_graph()
    return graph.compile(checkpointer=MemorySaver())


async def test_agent_returns_final_answer(test_graph) -> None:
    config = {"configurable": {"thread_id": "test-1"}}
    result = await test_graph.ainvoke(
        AgentState(messages=[HumanMessage(content="What is 2+2?")]),
        config=config,
    )
    assert result["final_answer"] is not None


# For Pydantic AI — use TestModel to avoid API calls
async def test_tool_called_with_correct_input() -> None:
    with agent.override(model=TestModel()):
        result = await agent.run("search for python async patterns")
    assert result.data is not None
```

### Fixture pattern for graph with MemorySaver
```python
@pytest.fixture
def compiled_graph():
    from langgraph.checkpoint.memory import MemorySaver
    return build_graph().compile(checkpointer=MemorySaver())
```

## 4. Error handling in agents

### Always handle tool failures gracefully
```python
async def act_node(state: AgentState) -> AgentState:
    try:
        result = await call_tool(state)
        return AgentState(**state.__dict__, messages=[...])
    except ToolError as exc:
        remaining = state.tool_calls_remaining - 1
        if remaining <= 0:
            return AgentState(**state.__dict__, error=str(exc), final_answer="Unable to complete.")
        return AgentState(**state.__dict__, tool_calls_remaining=remaining)
```

### Circuit breaker for external tool calls
Reuse `api.routing.circuit_breaker.CircuitBreaker` from ai-aggregator for any agent that calls external APIs:
```python
from api.routing.circuit_breaker import CircuitBreaker

_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=60.0)

async def safe_tool_call(provider: str, fn, *args, **kwargs):
    if not _breaker.can_call(provider):
        raise ToolError(f"Provider {provider} circuit open")
    try:
        result = await fn(*args, **kwargs)
        _breaker.record_success(provider)
        return result
    except Exception as exc:
        _breaker.record_failure(provider)
        raise ToolError(str(exc)) from exc
```

## 5. Ollama fallback pattern

Every Claude API call should have an Ollama fallback for local/offline resilience:

```python
import os
from pydantic_ai import Agent

def get_model() -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude-3-5-sonnet-latest"
    # Fallback to local Ollama
    return "ollama:llama3"

agent = Agent(get_model(), ...)
```

## 6. Forbidden patterns

| Anti-pattern | Fix |
|---|---|
| Stateless agent (no checkpointer) | Always compile with `MemorySaver` at minimum |
| Raw string LLM output parsed with regex | Use `result_type=PydanticModel` |
| Calling real Claude API in tests | Use `TestModel` or `mocker.AsyncMock` |
| Infinite retry loop in `act_node` | Cap with `tool_calls_remaining` counter in state |
| Agent tool that does DB access directly | Inject repository via `RunContext` deps |
| `asyncio.run(agent.run(...))` in a route | Just `await agent.run(...)` — already in async context |
