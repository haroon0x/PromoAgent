"""
Utility functions for PromoAgent.
"""
import re
from typing import Dict

def score_thread(thread: Dict, query: str) -> float:
    """
    Score a Reddit thread based on engagement and relevance to the query.
    Engagement: upvotes + 2 * num_comments
    Relevance: keyword overlap between query and thread title/selftext
    Returns a float score.
    """
    # Engagement
    score = thread.get('score', 0)
    num_comments = thread.get('num_comments', 0)
    engagement = score + 2 * num_comments

    # Relevance (simple keyword overlap)
    title = thread.get('title', '').lower()
    selftext = thread.get('selftext', '').lower()
    query_words = set(re.findall(r'\w+', query.lower()))
    thread_words = set(re.findall(r'\w+', title + ' ' + selftext))
    overlap = len(query_words & thread_words)
    relevance = overlap * 10  # weight relevance higher

    return engagement + relevance


def clean_text(text: str) -> str:
    """
    Clean and preprocess text scraped from Reddit.
    Removes URLs, markdown, excessive whitespace, and non-ASCII characters.
    """
    text = re.sub(r'http\\S+', '', text)  # Remove URLs
    text = re.sub(r'\\s+', ' ', text)     # Collapse whitespace
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII
    text = re.sub(r'[\\*_`>\\[\\](){}]', '', text)  # Remove markdown
    return text.strip()