#!/usr/bin/env python3
"""
Fetch posts from @iwriteok on Bluesky using requests library.
Try different approaches including web scraping.
"""

import json
import requests
import time
import re

def try_api_approach():
    """Try using the API with different endpoints."""

    # Try different base URLs
    base_urls = [
        "https://bsky.social/xrpc",
        "https://api.bsky.app/xrpc",
        "https://bsky.app/xrpc",
    ]

    handles = ['iwriteok.bsky.social', 'iwriteok.com']

    for base_url in base_urls:
        for handle in handles:
            try:
                print(f"\nTrying: {base_url} with handle {handle}")
                url = f"{base_url}/app.bsky.actor.getProfile"
                params = {'actor': handle}
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }

                response = requests.get(url, params=params, headers=headers, timeout=10)
                print(f"  Status: {response.status_code}")

                if response.status_code == 200:
                    profile = response.json()
                    print(f"  SUCCESS! Found: @{profile['handle']}")
                    return base_url, profile
                else:
                    print(f"  Response: {response.text[:200]}")

            except Exception as e:
                print(f"  Error: {e}")

    return None, None

def try_web_scrape(handle):
    """Try scraping the web profile."""
    try:
        # Try to access the profile page
        url = f"https://bsky.app/profile/{handle}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        print(f"\nTrying to scrape: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            # Look for JSON data in the page
            # Bluesky often embeds data in script tags
            html = response.text

            # Try to find embedded JSON data
            json_pattern = r'<script[^>]*>.*?window\.__INITIAL_STATE__\s*=\s*({.*?})</script>'
            matches = re.findall(json_pattern, html, re.DOTALL)

            if matches:
                print(f"Found {len(matches)} JSON data blocks")
                return html

            # Also just return the HTML for inspection
            return html

    except Exception as e:
        print(f"Error scraping: {e}")

    return None

def search_bluesky_social(query):
    """Try using bsky.social search."""
    try:
        url = "https://bsky.app/search"
        params = {'q': f'from:{query}'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        print(f"\nTrying search: {url}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            return response.text

    except Exception as e:
        print(f"Error searching: {e}")

    return None

if __name__ == '__main__':
    print("=" * 80)
    print("ATTEMPTING TO ACCESS BLUESKY DATA")
    print("=" * 80)

    # Try API approach
    print("\n1. Trying API approach...")
    print("-" * 80)
    base_url, profile = try_api_approach()

    if profile:
        print(f"\n✓ Successfully accessed API!")
        print(f"  Display name: {profile.get('displayName', 'N/A')}")
        print(f"  Posts count: {profile.get('postsCount', 'N/A')}")

        # Now try to fetch posts
        print("\n2. Fetching posts...")
        # Implementation continues...

    else:
        print("\n✗ API approach failed")

        # Try web scraping
        print("\n2. Trying web scraping approach...")
        print("-" * 80)

        handles = ['iwriteok.bsky.social', 'iwriteok']
        for handle in handles:
            html = try_web_scrape(handle)
            if html:
                # Save HTML for inspection
                filename = f'profile_{handle.replace(".", "_")}.html'
                with open(filename, 'w') as f:
                    f.write(html)
                print(f"  Saved HTML to {filename}")
                print(f"  HTML length: {len(html)} characters")

                # Try to extract post data from HTML
                # Look for specific patterns
                if 'post' in html.lower():
                    print("  Found 'post' mentions in HTML - analyzing...")
                break

        # Try search
        print("\n3. Trying search approach...")
        print("-" * 80)
        search_html = search_bluesky_social('iwriteok')
        if search_html:
            with open('search_results.html', 'w') as f:
                f.write(search_html)
            print("  Saved search HTML")

    print("\n" + "=" * 80)
    print("Investigation complete - check output files")
