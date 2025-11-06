# Research Guide: Finding Robert Evans' Bluesky Quote

## Objective
Find a specific post by Robert Evans (@iwriteok on Bluesky) that says something to the effect of:
> "People who have never done drugs or had a drug problem don't understand that social media is an addiction"

## Who is @iwriteok?
- **Name**: Robert Evans
- **Profession**: Journalist and podcaster
- **Organization**: Cool Zone Media
- **Bluesky Handle**: iwriteok.bsky.social
- **Twitter/X**: @IwriteOK
- **Notable Work**: "Behind the Bastards", "It Could Happen Here" podcasts

## Research Context
- The post was made **at least several months ago** (from November 2025)
- Robert Evans posts frequently on Bluesky
- The quote is a paraphrase - need to find the exact wording
- Topic relates to social media addiction being compared to drug addiction
- Specifically about people without drug experience not understanding social media's addictive nature

## Research Methods

### Method 1: Direct Bluesky Search (Requires Bluesky Account)
1. Log into bsky.app
2. Use the search function with these query patterns:
   - `from:iwriteok addiction`
   - `from:iwriteok drugs social media`
   - `from:iwriteok understand addiction`
   - `from:iwriteok never done drugs`
   - `from:iwriteok dopamine`
3. Filter by date if possible (go back 3-12 months)
4. Scroll through results looking for the quote

### Method 2: Using Python Script (Requires Working Bluesky API Access)
See `working_fetch_script.py` in this directory. Run it with:
```bash
python3 working_fetch_script.py
```

This will:
1. Fetch Robert Evans' Bluesky posts (up to 2000)
2. Search for relevant keywords
3. Save results to JSON files
4. Display top candidates

### Method 3: Third-Party Tools
- **ClearSky** (clearsky.services): May have search capabilities
- **SkyView**: View Bluesky threads without account
- **Bluesky search engines**: Various third-party search tools

### Method 4: Community Help
- Ask in Cool Zone Media fan communities
- Check Reddit communities that follow Robert Evans
- Ask on Bluesky directly if anyone remembers the post

## Keywords to Search For
Primary keywords:
- addiction / addicted / addict
- drug / drugs / substance
- social media / twitter / facebook
- understand / don't understand / never done / never tried
- dopamine
- compulsive / habit

## What to Collect
For each candidate post, record:
1. Exact text of the post
2. Date/timestamp
3. Link to post (AT-URI or web URL)
4. Engagement metrics (likes, reposts, replies)
5. Any relevant thread context

## Expected Outcome
Create a list of candidate quotes ranked by:
1. Keyword matches
2. Semantic similarity to the remembered quote
3. Recency (within the timeframe)
4. Engagement (popular posts are more likely to be remembered)

## Technical Limitations Encountered
During automated research, the following blockers were encountered:
- Bluesky public API returns 403 Forbidden
- ClearSky API inaccessible
- Internet Archive blocked
- Environment has strict network restrictions

**Conclusion**: This research requires manual completion or access from an environment with unrestricted internet access.
