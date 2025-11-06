#!/usr/bin/env python3
"""
Fetch posts from @iwriteok on Bluesky and search for the quote about
social media addiction and drugs.
"""

import json
from atproto import Client
from datetime import datetime

def fetch_user_posts(handle, limit=100):
    """Fetch posts from a Bluesky user."""
    client = Client()

    # No need to login for public posts
    # We can use the public API

    try:
        # Get the user's profile to find their DID
        profile = client.app.bsky.actor.get_profile({'actor': handle})
        print(f"Found profile: @{profile.handle}")
        print(f"Display name: {profile.display_name}")
        print(f"Posts count: {profile.posts_count}")
        print()

        # Fetch the user's posts
        posts = []
        cursor = None

        print(f"Fetching posts from @{handle}...")

        while len(posts) < limit:
            params = {
                'actor': profile.did,
                'limit': 100
            }
            if cursor:
                params['cursor'] = cursor

            response = client.app.bsky.feed.get_author_feed(params)

            if not response.feed:
                break

            for item in response.feed:
                if hasattr(item, 'post') and hasattr(item.post, 'record'):
                    post = item.post
                    posts.append({
                        'uri': post.uri,
                        'cid': post.cid,
                        'text': post.record.text if hasattr(post.record, 'text') else '',
                        'created_at': post.record.created_at,
                        'author': post.author.handle,
                        'likes': post.like_count if hasattr(post, 'like_count') else 0,
                        'reposts': post.repost_count if hasattr(post, 'repost_count') else 0,
                        'replies': post.reply_count if hasattr(post, 'reply_count') else 0,
                    })

            cursor = response.cursor
            if not cursor:
                break

            print(f"Fetched {len(posts)} posts so far...")

        return posts

    except Exception as e:
        print(f"Error fetching posts: {e}")
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
        try:
            posts = fetch_user_posts(handle, limit=1000)
            if posts:
                print(f"Successfully fetched {len(posts)} posts from @{handle}")
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
        'addiction', 'addicted', 'drug', 'drugs',
        'social media', 'never done', 'understand',
        'dopamine', 'habit', 'compulsive'
    ]

    matches = search_posts_for_keywords(posts, keywords)

    print(f"\nFound {len(matches)} posts with relevant keywords")

    # Save matches
    with open('keyword_matches.json', 'w') as f:
        json.dump(matches, f, indent=2)

    # Print top matches
    print("\nTop candidate posts:")
    print("=" * 80)
    for i, match in enumerate(matches[:20], 1):
        print(f"\n{i}. [{match['created_at']}]")
        print(f"   Keywords: {', '.join(match['matched_keywords'])}")
        print(f"   Engagement: {match['likes']} likes, {match['reposts']} reposts, {match['replies']} replies")
        print(f"   Text: {match['text']}")
        print("-" * 80)
