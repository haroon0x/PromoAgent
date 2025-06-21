"""
Supabase client for PromoAgent duplicate tracking.
"""
import os
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from src.utils.config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def has_commented_on_thread(thread_id: str) -> bool:
    """
    Check if the bot has already commented on a specific thread using Supabase.
    Returns True if the bot has commented, False otherwise.
    """
    try:
        result = supabase.table('commented_threads').select('thread_id').eq('thread_id', thread_id).execute()
        if len(result.data) > 0:
            print(f"Already commented on thread {thread_id}")
            return True
        return False
    except Exception as e:
        print(f"Error checking Supabase: {e}")
        return False

def save_commented_thread(thread_id: str, thread_title: str = "", subreddit: str = ""):
    """
    Save a commented thread to Supabase.
    """
    try:
        supabase.table('commented_threads').insert({
            'thread_id': thread_id,
            'thread_title': thread_title,
            'subreddit': subreddit,
            'commented_at': datetime.now().isoformat()
        }).execute()
        print(f"Saved thread {thread_id} to Supabase")
    except Exception as e:
        print(f"Error saving to Supabase: {e}")

def get_recent_comments(limit: int = 100) -> List[Dict]:
    """
    Get recent commented threads from Supabase.
    """
    try:
        result = supabase.table('commented_threads').select('*').order('commented_at', desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"Error getting recent comments: {e}")
        return []

def delete_old_comments(days_old: int = 30):
    """
    Delete comments older than specified days.
    """
    try:
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_old).isoformat()
        supabase.table('commented_threads').delete().lt('commented_at', cutoff_date).execute()
        print(f"Deleted comments older than {days_old} days")
    except Exception as e:
        print(f"Error deleting old comments: {e}")

def get_comment_stats() -> Dict:
    """
    Get statistics about commented threads.
    """
    try:
        # Total comments
        total_result = supabase.table('commented_threads').select('*', count='exact').execute()
        total_comments = total_result.count if total_result.count else 0
        
        # Comments today
        today = datetime.now().date().isoformat()
        today_result = supabase.table('commented_threads').select('*', count='exact').gte('commented_at', today).execute()
        today_comments = today_result.count if today_result.count else 0
        
        # Top subreddits
        subreddit_result = supabase.table('commented_threads').select('subreddit').execute()
        subreddit_counts = {}
        for row in subreddit_result.data:
            subreddit = row.get('subreddit', 'unknown')
            subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
        
        return {
            'total_comments': total_comments,
            'today_comments': today_comments,
            'top_subreddits': dict(sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    except Exception as e:
        print(f"Error getting comment stats: {e}")
        return {} 