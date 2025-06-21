from src.core.agent_graph import AgentState, build_agent_graph
from src.utils.logger import logger

if __name__ == "__main__":
    logger.info("=== PromoAgent: Autonomous Reddit Marketing Agent ===")
    print("=== PromoAgent: Autonomous Reddit Marketing Agent ===")
    query = input("Enter a topic or query to search on Reddit: ").strip()
    brand_instructions = input("Enter brand/product instructions for the reply: ").strip()

    # Initialize agent state with explicit brand instructions
    state = AgentState(query=query, brand_instructions=brand_instructions)

    # Build and run the agent graph
    graph = build_agent_graph()
    final_state = graph.invoke(state)
    
    logger.info("--- Pipeline Complete ---")
    print("\n--- Pipeline Complete ---")
    print(f"Reddit thread: {final_state.get('selected_thread', {}).get('title', 'N/A')}")
    print(f"Reply: {final_state.get('generated_reply', 'N/A')}")
    print(f"Reddit post result: {final_state.get('post_result', 'N/A')}")
    
    logger.info("(If configured, a notification email has been sent.)")
    print("(If configured, a notification email has been sent.)") 