"""Cart graph — reason over the cart and surface its deals, in parallel.

Agents 5 and 6 are independent: Cart Optimization inspects the cart's own
contents (duplicates, cheaper sellers, split shipping), while Deal & Coupon
just repeats the markdown a listing already reports. They share no data, so
they run as parallel branches off the start.

Cart Optimization is sequential within its own branch — the written advice is
phrased from the proved flags, so `check` runs before `narrate`.
"""

from langgraph.graph import END, START, StateGraph

from app.agents import cart_optimization, deal_coupon
from app.graph.state import AgentState


def _optimize(state: AgentState) -> dict:
    # search_results is the pool of alternatives the cheaper-elsewhere rule
    # compares against; empty until a search has run, which is the no-op case.
    flags = cart_optimization.check(state.cart, state.search_results)
    return {"cart_flags": flags, "cart_advice": cart_optimization.narrate(flags)}


def _deals(state: AgentState) -> dict:
    return {"deals": deal_coupon.find_deals([item.listing for item in state.cart])}


def build():
    graph = StateGraph(AgentState)
    graph.add_node("optimize", _optimize)
    graph.add_node("deals", _deals)
    graph.add_edge(START, "optimize")
    graph.add_edge(START, "deals")
    graph.add_edge("optimize", END)
    graph.add_edge("deals", END)
    return graph.compile()


graph = build()
