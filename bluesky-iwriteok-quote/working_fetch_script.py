#!/usr/bin/env python3
"""
Working script to fetch Robert Evans' (@iwriteok) Bluesky posts
and search for the social media addiction quote.

This script should work in an environment with proper internet access.

Requirements:
    pip install requests

Usage:
    python3 working_fetch_script.py
"""

import json
import requests
import time
from datetime import datetime
from typing import List, Dict, Optional

# Configuration
BASE_URL = "https://public.api.bsky.app/xrpc"
HANDLE = "iwriteok.bsky.social"
MAX_POSTS = 2000

# Keywords to search for
KEYWORDS = [
    'addiction', 'addicted', 'addict',
    'drug', 'drugs', 'substance',
    'social media', 'twitter', 'facebook', 'instagram',
    'never done', 'never tried', 'haven\'t done',
    'understand', 'don\'t understand', 'doesn\'t understand',
    'dopamine', 'habit', 'compulsive',
    'abuse'
]

def get_profile(handle: str) -> Optional[Dict]:
    """Get profile information for a user."""
    try:
        url = f"{BASE_URL}/app.bsky.actor.getProfile"
        params = {'actor': handle}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://bsky.app',
            'Referer': 'https://bsky.app/',
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Error fetching profile: {e}")
        return None

def get_author_feed(actor_did: str, limit: int = 100, cursor: Optional[str] = None) -> Optional[Dict]:
    """Get posts from an author's feed."""
    try:
        url = f"{BASE_URL}/app.bsky.feed.getAuthorFeed"
        params = {'actor': actor_did, 'limit': str(limit)}
        if cursor:
            params['cursor'] = cursor

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://bsky.app',
            'Referer': 'https://bsky.app/',
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        print(f"Error fetching feed: {e}")
        return None

def fetch_all_posts(handle: str, max_posts: int = 2000) -> List[Dict]:
    """Fetch all posts from a user."""
    print(f"Fetching profile for @{handle}...")
    profile = get_profile(handle)

    if not profile:
        print("Failed to fetch profile")
        return []

    print(f"\nProfile found:")
    print(f"  Handle: @{profile['handle']}")
    print(f"  Display name: {profile.get('displayName', 'N/A')}")
    print(f"  Total posts: {profile.get('postsCount', 'N/A')}")
    print(f"  DID: {profile['did']}")
    print()

    posts = []
    cursor = None
    page = 0

    print("Fetching posts...")
    while len(posts) < max_posts:
        page += 1
        print(f"  Page {page}: {len(posts)} posts fetched so far...", end='\r')

        response = get_author_feed(profile['did'], limit=100, cursor=cursor)

        if not response or not response.get('feed'):
            break

        for item in response['feed']:
            if 'post' not in item or 'record' not in item['post']:
                continue

            post = item['post']
            record = post['record']

            posts.append({
                'uri': post['uri'],
                'cid': post['cid'],
                'text': record.get('text', ''),
                'created_at': record.get('createdAt', ''),
                'author': post['author']['handle'],
                'likes': post.get('likeCount', 0),
                'reposts': post.get('repostCount', 0),
                'replies': post.get('replyCount', 0),
            })

        cursor = response.get('cursor')
        if not cursor:
            break

        # Be respectful to the API
        time.sleep(0.5)

    print(f"\n\nFetched {len(posts)} total posts")
    return posts

def calculate_relevance_score(post: Dict, keywords: List[str]) -> tuple[int, List[str]]:
    """Calculate how relevant a post is based on keyword matches."""
    text_lower = post['text'].lower()
    matched_keywords = []

    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched_keywords.append(keyword)

    # Bonus scoring
    score = len(matched_keywords)

    # Bonus for multiple key concepts
    has_addiction = any(k in matched_keywords for k in ['addiction', 'addicted', 'addict'])
    has_drugs = any(k in matched_keywords for k in ['drug', 'drugs', 'substance'])
    has_social_media = any(k in matched_keywords for k in ['social media', 'twitter', 'facebook', 'instagram'])
    has_understand = any(k in matched_keywords for k in ['understand', 'don\'t understand', 'doesn\'t understand'])

    if has_addiction and has_drugs:
        score += 5
    if has_addiction and has_social_media:
        score += 5
    if has_drugs and has_understand:
        score += 3
    if has_social_media and has_understand:
        score += 3

    return score, matched_keywords

def search_posts(posts: List[Dict], keywords: List[str]) -> List[Dict]:
    """Search posts for relevant keywords and rank by relevance."""
    matches = []

    for post in posts:
        score, matched = calculate_relevance_score(post, keywords)

        if score > 0:
            matches.append({
                **post,
                'matched_keywords': matched,
                'relevance_score': score
            })

    # Sort by relevance score, then by engagement
    return sorted(matches, key=lambda x: (x['relevance_score'], x['likes']), reverse=True)

def format_post_output(post: Dict, index: int) -> str:
    """Format a post for display."""
    # Parse date
    try:
        dt = datetime.fromisoformat(post['created_at'].replace('Z', '+00:00'))
        date_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        date_str = post['created_at']

    output = []
    output.append(f"\n{'='*80}")
    output.append(f"#{index} - Relevance Score: {post['relevance_score']}")
    output.append(f"{'='*80}")
    output.append(f"Date: {date_str}")
    output.append(f"Link: https://bsky.app/profile/{post['author']}/post/{post['uri'].split('/')[-1]}")
    output.append(f"Engagement: {post['likes']} likes, {post['reposts']} reposts, {post['replies']} replies")
    output.append(f"Keywords matched: {', '.join(post['matched_keywords'])}")
    output.append(f"\nText:")
    output.append(f"{'-'*80}")
    output.append(f"{post['text']}")
    output.append(f"{'-'*80}")

    return '\n'.join(output)

def main():
    print("="*80)
    print("ROBERT EVANS BLUESKY QUOTE FINDER")
    print("="*80)
    print()

    # Fetch posts
    posts = fetch_all_posts(HANDLE, MAX_POSTS)

    if not posts:
        print("Failed to fetch posts. Check your internet connection and API access.")
        return

    # Save all posts
    print("\nSaving all posts to 'all_posts.json'...")
    with open('all_posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    # Search for relevant posts
    print(f"\nSearching for posts matching keywords...")
    matches = search_posts(posts, KEYWORDS)

    print(f"Found {len(matches)} posts with relevant keywords")

    # Save matches
    print("\nSaving matches to 'keyword_matches.json'...")
    with open('keyword_matches.json', 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)

    # Display top candidates
    print("\n" + "="*80)
    print("TOP CANDIDATE POSTS")
    print("="*80)

    # Show top 20 most relevant
    for i, post in enumerate(matches[:20], 1):
        print(format_post_output(post, i))

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total posts fetched: {len(posts)}")
    print(f"Posts with keywords: {len(matches)}")
    print(f"High relevance posts (score >= 8): {len([m for m in matches if m['relevance_score'] >= 8])}")
    print(f"\nResults saved to:")
    print(f"  - all_posts.json (all {len(posts)} posts)")
    print(f"  - keyword_matches.json ({len(matches)} matching posts)")

if __name__ == '__main__':
    main()
