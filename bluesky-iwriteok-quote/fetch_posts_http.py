#!/usr/bin/env python3
"""
Fetch posts from @iwriteok on Bluesky using direct HTTP API calls.
"""

import json
import urllib.request
import urllib.parse
import time

BASE_URL = "https://public.api.bsky.app/xrpc"

def get_profile(handle):
    """Get profile information for a user."""
    url = f"{BASE_URL}/app.bsky.actor.getProfile?actor={urllib.parse.quote(handle)}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)'
    })
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def get_author_feed(actor_did, limit=100, cursor=None):
    """Get posts from an author's feed."""
    params = {'actor': actor_did, 'limit': str(limit)}
    if cursor:
        params['cursor'] = cursor

    url = f"{BASE_URL}/app.bsky.feed.getAuthorFeed?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)'
    })
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read())

def fetch_user_posts(handle, max_posts=1000):
    """Fetch posts from a Bluesky user."""
    try:
        # Get profile
        print(f"Fetching profile for @{handle}...")
        profile = get_profile(handle)

        print(f"Found: @{profile['handle']}")
        print(f"Display name: {profile.get('displayName', 'N/A')}")
        print(f"Posts count: {profile.get('postsCount', 'N/A')}")
        print()

        # Fetch posts
        posts = []
        cursor = None

        while len(posts) < max_posts:
            print(f"Fetching posts... ({len(posts)} so far)")

            response = get_author_feed(profile['did'], limit=100, cursor=cursor)

            if not response.get('feed'):
                break

            for item in response['feed']:
                if 'post' in item and 'record' in item['post']:
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

            # Be nice to the API
            time.sleep(0.5)

        return posts

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def search_posts_for_keywords(posts, keywords):
    """Search posts for specific keywords."""
    matches = []

    for post in posts:
        text_lower = post['text'].lower()

        # Check if post contains relevant keywords
        keyword_matches = [kw for kw in keywords if kw.lower() in text_lower]

        if keyword_matches:
            matches.append({
                **post,
                'matched_keywords': keyword_matches,
                'relevance_score': len(keyword_matches)
            })

    return sorted(matches, key=lambda x: x['relevance_score'], reverse=True)

if __name__ == '__main__':
    # Try different possible handles
    possible_handles = [
        'iwriteok.bsky.social',
        'iwriteok.com',
    ]

    posts = []
    for handle in possible_handles:
        print(f"\nTrying handle: {handle}")
        print("=" * 80)
        try:
            posts = fetch_user_posts(handle, max_posts=2000)
            if posts:
                print(f"\nSuccessfully fetched {len(posts)} posts from @{handle}")
                break
        except Exception as e:
            print(f"Failed with {handle}: {e}")
            continue

    if not posts:
        print("Could not fetch posts from any handle")
        exit(1)

    # Save all posts
    with open('all_posts.json', 'w') as f:
        json.dump(posts, f, indent=2)
    print(f"\nSaved {len(posts)} posts to all_posts.json")

    # Search for relevant keywords
    keywords = [
        'addiction', 'addicted', 'addict',
        'drug', 'drugs',
        'social media', 'twitter', 'facebook',
        'never done', 'never tried', 'understand',
        'dopamine', 'habit', 'compulsive',
        'substance', 'abuse'
    ]

    matches = search_posts_for_keywords(posts, keywords)

    print(f"\nFound {len(matches)} posts with relevant keywords")

    # Save matches
    with open('keyword_matches.json', 'w') as f:
        json.dump(matches, f, indent=2)

    # Print top matches
    print("\n" + "=" * 80)
    print("TOP CANDIDATE POSTS")
    print("=" * 80)

    for i, match in enumerate(matches[:30], 1):
        print(f"\n{i}. [{match['created_at']}]")
        print(f"   Keywords matched: {', '.join(match['matched_keywords'])}")
        print(f"   Engagement: {match['likes']} likes, {match['reposts']} reposts, {match['replies']} replies")
        print(f"\n   \"{match['text']}\"")
        print("-" * 80)

    # Also search for multi-keyword combinations
    print("\n" + "=" * 80)
    print("POSTS WITH MULTIPLE RELEVANT KEYWORDS (Highest Relevance)")
    print("=" * 80)

    high_relevance = [m for m in matches if m['relevance_score'] >= 3]
    for i, match in enumerate(high_relevance[:10], 1):
        print(f"\n{i}. [{match['created_at']}] - Score: {match['relevance_score']}")
        print(f"   Keywords: {', '.join(match['matched_keywords'])}")
        print(f"\n   \"{match['text']}\"")
        print("-" * 80)
