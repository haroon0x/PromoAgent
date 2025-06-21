"""
LangGraph pipeline for PromoAgent.
"""
from langgraph.graph import StateGraph , START, END
from typing import List, Dict, Optional
from src.api.reddit_api import search_threads, post_comment, search_questions, post_comment_reply
from src.models.model import generate_replies
from src.utils.config import get_brand_instructions
from src.api.notifier import send_gmail_notification
from pydantic import BaseModel, Field
from src.utils.logger import logger
import os

class AgentState(BaseModel):
    query: str
    brand_instructions: str
    threads: List[Dict] = Field(default_factory=list)
    selected_thread: Optional[Dict] = None
    generated_reply: Optional[str] = None
    post_result: Optional[str] = None
    comment_questions: List[Dict] = Field(default_factory=list)
    comment_replies: List[Dict] = Field(default_factory=list)


def node_search_threads(state: AgentState) -> AgentState:
    state.threads = search_threads(state.query)
    if state.threads:
        state.selected_thread = state.threads[0]
    return state

def node_generate_reply(state: AgentState) -> AgentState:
    if state.selected_thread:
        try:
            logger.info(f"Generating reply for thread: {state.selected_thread.get('title')}")
            state.generated_reply = generate_replies(state.selected_thread, state.brand_instructions)
            logger.info(f"Generated reply: {state.generated_reply[:100]}...")
        except Exception as e:
            state.generated_reply = None
            logger.error(f"Error generating reply: {e}")
            print(f"Error generating reply: {e}")
    return state

def node_post_reply(state: AgentState) -> AgentState:
    if state.selected_thread and state.generated_reply:
        thread_id = state.selected_thread.get('id')
        try:
            state.post_result = post_comment(thread_id, state.generated_reply)
        except Exception as e:
            state.post_result = f"Error posting comment: {e}"
            logger.error(f"Error posting comment: {e}")
            print(f"Error posting comment: {e}")
    return state

def node_search_comment_questions(state: AgentState) -> AgentState:
    """Search for questions in comments that could be answered with the promoted product."""
    if state.selected_thread:
        thread_id = state.selected_thread.get('id')
        try:
            state.comment_questions = search_questions(thread_id)
            logger.info(f"Found {len(state.comment_questions)} potential questions in comments.")
            print(f"Found {len(state.comment_questions)} potential questions in comments")
        except Exception as e:
            logger.error(f"Error searching comment questions: {e}")
            print(f"Error searching comment questions: {e}")
            state.comment_questions = []
    return state

def print_comment_questions(state: AgentState) -> AgentState:
    """Print found comment questions for testing purposes."""
    logger.info("--- Comment Questions Found ---")
    print("\n=== Comment Questions Found ===")
    if state.comment_questions:
        for i, question in enumerate(state.comment_questions, 1):
            log_message = (
                f"\n{i}. Comment by {question['author']} (Score: {question['score']})"
                f"\n   Text: {question['body'][:200]}..."
                f"\n   ID: {question['id']}"
            )
            logger.info(log_message)
            print(log_message)
    else:
        logger.info("No comment questions found.")
        print("No comment questions found.")
    logger.info("-----------------------------")
    print("=" * 40)
    return state

def node_generate_comment_replies(state: AgentState) -> AgentState:
    """Generate replies to comment questions."""
    if state.comment_questions:
        replies = []
        for question in state.comment_questions[:3]:  # Limit to top 3 questions
            try:
                # Create context for the comment reply
                comment_context = f"Comment: {question['body']}\nThread: {question['thread_title']}"
                
                # Generate reply using the same model but with comment context
                reply_text = generate_replies(
                    {'title': question['thread_title'], 'selftext': question['body']}, 
                    state.brand_instructions
                )
                
                replies.append({
                    'comment_id': question['id'],
                    'original_comment': question['body'],
                    'reply_text': reply_text,
                    'author': question['author']
                })
            except Exception as e:
                print(f"Error generating reply for comment {question['id']}: {e}")
        
        state.comment_replies = replies
    return state

def node_post_comment_replies(state: AgentState) -> AgentState:
    """Post replies to comment questions."""
    if state.comment_replies:
        for reply in state.comment_replies:
            try:
                result = post_comment_reply(reply['comment_id'], reply['reply_text'])
                reply['post_result'] = result
                print(f"Posted reply to comment by {reply['author']}: {result}")
            except Exception as e:
                reply['post_result'] = f"Error: {e}"
                logger.error(f"Error posting reply to comment: {e}")
                print(f"Error posting reply to comment: {e}")
    return state

def node_notify_via_email(state: AgentState) -> AgentState:
    if state.selected_thread and state.generated_reply and state.post_result:
        subject = f"PromoAgent: Replied to Reddit thread '{state.selected_thread.get('title', '')}'"
        body = f"A reply was posted to Reddit.\n\nThread: {state.selected_thread.get('title', '')}\nURL: {state.selected_thread.get('url', '')}\n\nReply:\n{state.generated_reply}\n\nReddit Comment ID/Status: {state.post_result}"
        try:
            send_gmail_notification(subject, body)
            logger.info(f"Sent email notification to {os.getenv('NOTIFY_EMAIL')}")
            print(f"Sent email notification to {os.getenv('NOTIFY_EMAIL')}")
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            print(f"Error sending email notification: {e}")
    return state

def has_threads(state : AgentState):
    return state.threads != [] 

def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("search_threads", node_search_threads)
    graph.add_node("generate_reply", node_generate_reply)
    graph.add_node("post_reply", node_post_reply)
    graph.add_node("notify_via_email", node_notify_via_email)
    
    # Linear flow
    graph.set_entry_point("search_threads")
    #graph.add_edge("search_threads", "generate_reply")  #non conditional flow
    graph.add_conditional_edges("search_threads", has_threads, {
        True: "generate_reply",
        False: END
    })
    graph.add_edge("generate_reply", "post_reply")
    graph.add_edge("post_reply", "notify_via_email")

    return graph.compile()

