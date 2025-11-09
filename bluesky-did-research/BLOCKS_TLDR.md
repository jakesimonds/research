# How to Check if Someone Blocked Someone Else - TL;DR

## Quick Answer

Blocks are public. Here's how to check:

### Method 1: Direct URL (Fastest)
```
https://pdsls.dev/at/@suspected-blocker.bsky.social/app.bsky.graph.block
```

Replace `suspected-blocker.bsky.social` with their handle.

### Method 2: API Query
```bash
# Get blocker's DID
curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=blocker.bsky.social"
# Returns: {"did":"did:plc:abc123"}

# List their blocks
curl "https://bsky.social/xrpc/com.atproto.repo.listRecords?repo=did:plc:abc123&collection=app.bsky.graph.block"
```

## What You'll See

Block records look like:
```json
{
  "subject": "did:plc:xyz789",  // DID of blocked person
  "createdAt": "2024-11-08T12:34:56.789Z"
}
```

## To Check Specific Block

1. Get blocker's DID: `https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=BLOCKER`
2. Get blocked person's DID: Same URL with blocked person's handle
3. View blocker's blocks: `https://pdsls.dev/at/BLOCKER_DID/app.bsky.graph.block`
4. Look for blocked person's DID in the "subject" fields

## Example

**Question:** Did @bob.bsky.social block @alice.bsky.social?

**Quick check:**
```bash
# Get both DIDs
curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=bob.bsky.social"
curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=alice.bsky.social"

# Check Bob's blocks
curl "https://bsky.social/xrpc/com.atproto.repo.listRecords?repo=did:plc:bobsdid&collection=app.bsky.graph.block" | grep "alicesdid"
```

If grep finds a match, Bob has blocked Alice.

## pdsls.dev Navigation

1. Go to `https://pdsls.dev`
2. Search for the blocker's handle
3. Navigate to their `app.bsky.graph.block` collection
4. Browse records to find the blocked person's DID

---

## Important Notes

✅ Blocks are public by design (required for federation)
✅ Anyone can view anyone's block list
✅ Records show WHO and WHEN, not WHY
❌ Unblocked users disappear from the list (not historical)
❌ Need DIDs, not handles, to match records

---

Full guide: `VIEWING_BLOCKS_ON_PDSLS.md`
