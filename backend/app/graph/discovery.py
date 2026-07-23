"""Discovery graph — the search half of the assistant.

Wires Agents 1-3 into the linear pipeline a shopping query runs through:
understand the request, search live stores, rank the candidates. Each node is a
thin adapter over an agent; the agents hold the logic and stay unit-testable on
their own.

Agent 4 (Review Intelligence) is deliberately not a node here. Reviews are
summarized lazily, per product, behind /api/reviews — an LLM call each, against
a five-per-minute free tier. Summarizing every ranked result up front would
duplicate that route and exhaust the minute's budget on products the shopper
never opens.
"""

from langgraph.graph import END, START, StateGraph

from app.agents import comparison, product_search, requirement_analyzer
from app.graph.state import AgentState


def _analyze(state: AgentState) -> dict:
    return {"requirements": requirement_analyzer.analyze(state.user_query)}


def _search(state: AgentState) -> dict:
    return {"search_results": product_search.search(state.requirements)}


def _compare(state: AgentState) -> dict:
    return {"ranked_products": comparison.rank(state.search_results, state.requirements)}


def build():
    graph = StateGraph(AgentState)
    graph.add_node("analyze", _analyze)
    graph.add_node("search", _search)
    graph.add_node("compare", _compare)
    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "search")
    graph.add_edge("search", "compare")
    graph.add_edge("compare", END)
    return graph.compile()


graph = build()
