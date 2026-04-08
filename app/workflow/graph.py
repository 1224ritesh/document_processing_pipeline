from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from app.workflow.state import PipelineState
from app.workflow.nodes.segregator import segregator_node
from app.workflow.nodes.id_agent import id_agent_node
from app.workflow.nodes.discharge_agent import discharge_agent_node
from app.workflow.nodes.bill_agent import bill_agent_node
from app.workflow.nodes.aggregator import aggregator_node


def build_graph() -> CompiledStateGraph:
    
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("segregator", segregator_node)
    graph.add_node("id_agent", id_agent_node)
    graph.add_node("discharge_agent", discharge_agent_node)
    graph.add_node("bill_agent", bill_agent_node)
    graph.add_node("aggregator", aggregator_node)

    # Define edges
    # START → segregator
    graph.add_edge(START, "segregator")

    # segregator → 3 agents (fan-out, run in parallel)
    graph.add_edge("segregator", "id_agent")
    graph.add_edge("segregator", "discharge_agent")
    graph.add_edge("segregator", "bill_agent")

    # 3 agents → aggregator (fan-in, waits for all)
    graph.add_edge("id_agent", "aggregator")
    graph.add_edge("discharge_agent", "aggregator")
    graph.add_edge("bill_agent", "aggregator")

    # aggregator → END
    graph.add_edge("aggregator", END)

    return graph.compile()


# Singleton compiled graph
workflow: CompiledStateGraph = build_graph()
