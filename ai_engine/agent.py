from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from ai_engine.rag import rag_pipeline
import asyncio

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    incident_id: str
    logs: str
    root_cause: str
    suggested_fix: str
    status: str

def log_analyzer(state: AgentState):
    """Analyze logs to identify the error pattern."""
    print(f"--- [Node: Log Analyzer] Analyzing logs for incident {state['incident_id']} ---")
    # In a real scenario, this would query Elasticsearch/OpenSearch
    error_log = "ERROR 500: Payment service failed due to Redis connection timeout"
    return {"logs": error_log, "status": "pattern_identified"}

def rag_consultant(state: AgentState):
    """Retrieve historical solutions using RAG."""
    print(f"--- [Node: RAG Consultant] Consulting historical knowledge for: {state['logs']} ---")
    historical_solution = rag_pipeline.query(state['logs'])
    return {"root_cause": historical_solution, "status": "historical_context_found"}

def fix_recommender(state: AgentState):
    """Recommend a fix based on the diagnosis."""
    print("--- [Node: Fix Recommender] Generating remediation steps ---")
    fix = f"REMEDIATION: {state['root_cause']}. Suggested by AI Agent."
    return {"suggested_fix": fix, "status": "completed"}

def rca_workflow():
    workflow = StateGraph(AgentState)
    
    # Define Nodes
    workflow.add_node("analyzer", log_analyzer)
    workflow.add_node("rag_consultant", rag_consultant)
    workflow.add_node("recommender", fix_recommender)
    
    # Define Edges
    workflow.set_entry_point("analyzer")
    workflow.add_edge("analyzer", "rag_consultant")
    workflow.add_edge("rag_consultant", "recommender")
    workflow.add_edge("recommender", END)
    
    return workflow.compile()

# Compilation of the graph
agent_executor = rca_workflow()

async def run_rca(incident_id: str):
    """Helper to run the RCA agent asynchronously."""
    initial_state = {
        "messages": [HumanMessage(content=f"Analyze incident {incident_id}")],
        "incident_id": incident_id,
        "logs": "",
        "root_cause": "",
        "suggested_fix": "",
        "status": "started"
    }
    result = await asyncio.to_thread(agent_executor.invoke, initial_state)
    return result
