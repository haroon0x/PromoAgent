"""
FastAPI backend for PromoAgent frontend integration.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime

from src.core.agent_graph import build_agent_graph, AgentState
from src.utils.config import get_brand_instructions
from src.utils.logger import logger

app = FastAPI(title="PromoAgent API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class AgentRequest(BaseModel):
    topic: str
    brand_instructions: str
    mode: str = "autonomous"  # autonomous or preview

class ActivityResponse(BaseModel):
    id: str
    timestamp: str
    type: str
    message: str
    status: str

class ResultResponse(BaseModel):
    id: str
    thread_title: str
    submission_url: str
    post_url: str
    generated_reply: str
    posted: bool
    timestamp: str

# Global state for real-time updates
agent_sessions = {}

def update_last_activity_status(session_id: str, status: str):
    """Update the status of the most recent activity."""
    if session_id in agent_sessions and agent_sessions[session_id]['activities']:
        agent_sessions[session_id]['activities'][-1]['status'] = status

@app.get("/")
async def root():
    return {"message": "PromoAgent API is running"}

@app.post("/api/agent/start")
async def start_agent(request: AgentRequest):
    """Start the PromoAgent with given parameters."""
    try:
        # Create agent state
        state = AgentState(
            query=request.topic,
            brand_instructions=request.brand_instructions
        )
        
        # Generate session ID
        session_id = f"session_{datetime.now().timestamp()}"
        
        # Initialize session
        agent_sessions[session_id] = {
            "state": state,
            "activities": [],
            "results": [],
            "is_running": True
        }
        
        # Start agent in background
        asyncio.create_task(run_agent_pipeline(session_id, state))
        
        return {
            "session_id": session_id,
            "status": "started",
            "message": f"Agent started for topic: {request.topic}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/{session_id}/status")
async def get_agent_status(session_id: str):
    """Get current agent status and activities."""
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = agent_sessions[session_id]
    
    return {
        "session_id": session_id,
        "is_running": session["is_running"],
        "activities": session["activities"],
        "results": session["results"]
    }

@app.post("/api/agent/{session_id}/stop")
async def stop_agent(session_id: str):
    """Stop the agent."""
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    agent_sessions[session_id]["is_running"] = False
    
    return {
        "session_id": session_id,
        "status": "stopped",
        "message": "Agent stopped"
    }

async def run_agent_pipeline(session_id: str, state: AgentState):
    """Run the agent pipeline and update session in real-time."""
    session = agent_sessions[session_id]
    graph = None
    try:
        graph = build_agent_graph()
        
        add_activity(session_id, "start", f"Starting agent for topic: {state.query}", "in-progress")

        async for step in graph.astream(state):
            node_name = list(step.keys())[-1]
            node_output = list(step.values())[-1]

            update_last_activity_status(session_id, "completed")
            
            if node_name == "search_threads":
                threads = node_output.get('threads', [])
                if not threads:
                    add_activity(session_id, "search", "No relevant threads found. Stopping agent.", "completed")
                    session["is_running"] = False
                    return
                
                add_activity(session_id, "search", f"Found {len(threads)} relevant threads.", "completed")
                selected_thread_title = node_output.get('selected_thread', {}).get('title', 'N/A')
                add_activity(session_id, "search", f"Selected best thread: '{selected_thread_title}'", "completed")
                add_activity(session_id, "generate", "Generating AI reply...", "in-progress")

            elif node_name == "generate_reply":
                generated_reply = node_output.get('generated_reply')
                if not generated_reply:
                    add_activity(session_id, "generate", "Failed to generate AI reply. Stopping agent.", "error")
                    session["is_running"] = False
                    return
                
                reply_snippet = (generated_reply[:75] + '...') if len(generated_reply) > 75 else generated_reply
                add_activity(session_id, "generate", "Successfully generated AI reply.", "completed")
                add_activity(session_id, "generate", f'Reply preview: "{reply_snippet}"', "completed")
                add_activity(session_id, "post", "Posting reply to Reddit...", "in-progress")

            elif node_name == "post_reply":
                post_result = node_output.get('post_result', '')
                if post_result and post_result.startswith('https://'):
                    add_activity(session_id, "post", "Successfully posted reply.", "completed")
                    add_activity(session_id, "post", f"View comment: {post_result}", "completed")
                else:
                    error_message = post_result or "An unknown error occurred."
                    add_activity(session_id, "post", f"Failed to post reply: {error_message}", "error")

                # Check if email notification is the next step
                if graph and "notify_via_email" in graph.nodes:
                     add_activity(session_id, "notify", "Sending notification email...", "in-progress")

            elif node_name == "notify_via_email":
                add_activity(session_id, "notify", "Email notification sent.", "completed")

            session["state"] = node_output
        
        update_last_activity_status(session_id, "completed")
        final_state = session.get("state", {})
        add_activity(session_id, "complete", "Agent run finished successfully.", "completed")
        
        if final_state.get('selected_thread'):
            add_result(session_id, final_state)
            
    except Exception as e:
        logger.error(f"Error in agent pipeline for session {session_id}: {e}", exc_info=True)
        update_last_activity_status(session_id, "error")
        add_activity(session_id, "error", f"An unexpected error occurred: {str(e)}", "error")
    
    finally:
        session["is_running"] = False

def add_activity(session_id: str, activity_type: str, message: str, status: str):
    """Add activity to session."""
    if session_id in agent_sessions:
        activity = {
            "id": f"activity_{len(agent_sessions[session_id]['activities'])}",
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "message": message,
            "status": status
        }
        agent_sessions[session_id]["activities"].append(activity)

def add_result(session_id: str, final_state):
    """Add result to session."""
    if session_id in agent_sessions:
        post_url = final_state.get('post_result', '')
        posted_successfully = post_url.startswith('https://')

        result = {
            "id": f"result_{len(agent_sessions[session_id]['results'])}",
            "thread_title": final_state.get('selected_thread', {}).get('title', 'N/A'),
            "submission_url": final_state.get('selected_thread', {}).get('url', ''),
            "generated_reply": final_state.get('generated_reply', 'N/A'),
            "posted": posted_successfully,
            "post_url": post_url if posted_successfully else '',
            "timestamp": datetime.now().isoformat()
        }
        agent_sessions[session_id]["results"].append(result)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PromoAgent Backend...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        "src.backend.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    ) 