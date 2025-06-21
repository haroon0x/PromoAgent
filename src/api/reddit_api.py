"""
Reddit API interface for PromoAgent.
"""
import praw
from typing import List, Dict
from src.utils.config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
    REDDIT_USER_AGENT,
)
from src.utils.logger import logger



def get_reddit_instance():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=REDDIT_USER_AGENT,
    )

def has_commented_on_thread(thread_id: str) -> bool:
    """
    Check if the bot has already commented on a specific thread using Reddit API.
    Returns True if the bot has commented, False otherwise.
    """
    reddit = get_reddit_instance()
    try:
        # Get the current user's comment history
        user = reddit.user.me()
        
        # Check if user has commented on this submission
        for comment in user.comments.new(limit=100):  # Check last 100 comments
            if comment.submission.id == thread_id:
                print(f"Already commented on thread {thread_id}")
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking comment history: {e}")
        return False
    
def search_threads(query: str, limit: int = 5) -> List[Dict]:
    """
    Search Reddit for threads matching the query.
    Returns a list of thread info dicts, excluding threads already commented on.
    """
    reddit = get_reddit_instance()
    results = []
    
    # Search for more threads than needed to account for filtering
    search_limit = limit * 2  # Search 2x more to account for already commented threads
    
    for submission in reddit.subreddit('all').search(query, sort='relevance', limit=search_limit):
        # Check if we've already commented on this thread
        if has_commented_on_thread(submission.id):
            continue
        if submission.archived:
            continue
            
        results.append({
            'id': submission.id,
            'title': submission.title,
            'selftext': submission.selftext,
            'url': submission.url,
            'score': submission.score,
            'num_comments': submission.num_comments,
            'subreddit': str(submission.subreddit),
        })
        
        # Stop if we have enough results
        if len(results) >= limit:
            break
    
    return results

def post_comment(thread_id: str, comment: str) -> str:
    """
    Post a comment to a Reddit thread.
    Returns the comment URL or error message.
    """
    reddit = get_reddit_instance()
    try:
        submission = reddit.submission(id=thread_id)
        reply = submission.reply(comment)
        url = f"https://reddit.com{reply.permalink}"
        logger.info(f"Posted comment: {url}")
        return url
    except Exception as e:
        logger.error(f"Error posting comment to thread {thread_id}: {e}")
        print(f"Error posting comment to thread {thread_id}: {e}")
        return f"Error posting comment: {e}"

def post_comment_reply(comment_id: str, reply_text: str) -> str:
    """
    Post a reply to a specific Reddit comment.
    Returns the reply URL or error message.
    """
    reddit = get_reddit_instance()
    try:
        comment = reddit.comment(id=comment_id)
        reply = comment.reply(reply_text)
        url = f"https://reddit.com{reply.permalink}"
        logger.info(f"Posted comment reply: {url}")
        return url
    except Exception as e:
        logger.error(f"Error posting comment reply to {comment_id}: {e}")
        print(f"Error posting comment reply to {comment_id}: {e}")
        return f"Error posting comment reply: {e}"

def search_questions(thread_id: str, query_keywords: List[str] = None) -> List[Dict]:
    """
    Find comments in a thread where users are asking questions that could be answered with the promoted product.
    Returns a list of comment info dicts.
    """
    reddit = get_reddit_instance()
    results = []
    
    try:
        submission = reddit.submission(id=thread_id)
        submission.comments.replace_more(limit=0)  # Load all comments
        
        # Default keywords that indicate someone is looking for help/solutions
        if query_keywords is None:
            query_keywords = [
                'help', 'need', 'looking for', 'recommend', 'suggest', 'best', 
                'how to', 'what should', 'anyone know', 'advice', 'solution',
                'tool', 'software', 'platform', 'service', 'alternative'
            ] 
        
        for comment in submission.comments.list():
            comment_text = comment.body.lower()
            
            is_question = any(keyword in comment_text for keyword in query_keywords)
            
            # Additional checks for question indicators
            has_question_mark = '?' in comment.body
            starts_with_question_words = any(comment_text.startswith(word) for word in ['what', 'how', 'where', 'when', 'why', 'which'])
            
            if (is_question or has_question_mark or starts_with_question_words) and comment.score > 0:
                results.append({
                    'id': comment.id,
                    'body': comment.body,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'permalink': f"https://reddit.com{comment.permalink}",
                    'thread_id': thread_id,
                    'thread_title': submission.title
                })
        
        # Sort by score (highest first) and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:10]  # Return top 10 most upvoted questions
        
    except Exception as e:
        logger.error(f"Error searching questions in thread {thread_id}: {e}")
        print(f"Error searching questions in thread {thread_id}: {e}")
        return [] 