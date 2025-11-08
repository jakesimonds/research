# How to View Block Records on pdsls.dev

**Task:** Investigate if someone blocked someone else by viewing public block records

---

## Quick Answer

Yes, you can view block records! Here's how:

**URL Pattern:**
```
https://pdsls.dev/at/{BLOCKER_DID}/app.bsky.graph.block
```

Replace `{BLOCKER_DID}` with the DID of the person you think did the blocking.

---

## Step-by-Step Guide

### Step 1: Get the DID of the Suspected Blocker

You need to find the DID (permanent identifier) of the person you think did the blocking.

**Method 1: Use the handle directly**
```
https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=username.bsky.social
```

Replace `username.bsky.social` with their actual handle.

Returns: `{"did":"did:plc:xxxxxxxxxxxxxx"}`

**Method 2: If you already know their handle, go straight to pdsls.dev**
```
https://pdsls.dev/at/@username.bsky.social
```

This will resolve their handle to their DID and show their repository.

**Method 3: From a post URL**

If you have a link to one of their posts like:
```
https://bsky.app/profile/username.bsky.social/post/3abc123xyz
```

The DID is embedded in the post. You can also just go to:
```
https://pdsls.dev/at/@username.bsky.social
```

### Step 2: Navigate to Their Block Collection

Once you have their DID (let's say it's `did:plc:abc123xyz789`), use this URL:

```
https://pdsls.dev/at/did:plc:abc123xyz789/app.bsky.graph.block
```

Or if you're already on their pdsls.dev page, click through the collections to find `app.bsky.graph.block`.

### Step 3: View Individual Block Records

On the block collection page, you'll see a list of block records. Each block record has:
- **Record key** (rkey): A unique identifier for that block (e.g., `3l4abc123xyz`)
- **Subject**: The DID of the person who is blocked
- **Created at**: When the block was created

**To view a specific block:**
```
https://pdsls.dev/at/did:plc:abc123xyz789/app.bsky.graph.block/3l4abc123xyz
```

### Step 4: Check if Someone Specific is Blocked

To find out if Person A blocked Person B:

1. Get Person A's DID (the suspected blocker)
2. Get Person B's DID (the suspected blocked person)
3. Go to Person A's block collection:
   ```
   https://pdsls.dev/at/{PERSON_A_DID}/app.bsky.graph.block
   ```
4. Look through the records for Person B's DID in the "subject" field

---

## Alternative Method: Direct API Query

If you want to query directly without the web interface:

```bash
# Get the blocker's DID first
curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=blocker.bsky.social"

# List their block records
curl "https://bsky.social/xrpc/com.atproto.repo.listRecords?repo=did:plc:BLOCKER_DID&collection=app.bsky.graph.block"
```

This returns JSON with all their block records.

**Example response structure:**
```json
{
  "records": [
    {
      "uri": "at://did:plc:abc123/app.bsky.graph.block/3l4xyz",
      "value": {
        "$type": "app.bsky.graph.block",
        "subject": "did:plc:blocked-person-did",
        "createdAt": "2024-11-08T12:34:56.789Z"
      }
    }
  ],
  "cursor": "..."
}
```

---

## Understanding Block Records

**Structure of a block record:**

```json
{
  "$type": "app.bsky.graph.block",
  "subject": "did:plc:xyz789abc",  // DID of the blocked person
  "createdAt": "2024-11-08T10:30:00.000Z"
}
```

**Key fields:**
- **subject**: The DID of the account being blocked
- **createdAt**: ISO 8601 timestamp of when the block was created
- **Record URI**: `at://BLOCKER_DID/app.bsky.graph.block/RKEY`

---

## Important Notes

### Blocks ARE Public

As you mentioned, blocks are indeed public in ATProto. This is by design:
- **Why?** Federation requires all servers to know about blocks to enforce them
- **Privacy concern?** Yes, but Bluesky decided this is necessary for distributed enforcement
- **Can't be hidden:** Any block you create is visible to anyone who knows how to look

### What You Can Find Out

✅ You CAN see:
- Who someone has blocked (by viewing their block collection)
- When they blocked them (createdAt timestamp)
- The DID of blocked accounts

❌ You CANNOT see (without additional work):
- Why they blocked them (no reason field)
- If someone has blocked YOU specifically (need to check their blocks)
- Historical blocks that have been removed (once unblocked, record is deleted)

### Limitations

**Pagination:** If someone has blocked many accounts, you may need to paginate through results. The API returns a `cursor` field for this.

**Deleted blocks:** If someone blocks then unblocks, the block record is deleted from their repository. You won't see historical blocks.

**Handle vs DID:** Block records store DIDs, not handles. So you need to resolve handles to DIDs to check specific blocks.

---

## Complete Example Scenario

**Scenario:** You saw User @alice.bsky.social reply to @bob.bsky.social, but now the replies are gone. You suspect Bob blocked Alice.

**Step 1: Get Bob's DID**
```bash
curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=bob.bsky.social"
# Returns: {"did":"did:plc:bobsdid123"}
```

**Step 2: Get Alice's DID**
```bash
curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=alice.bsky.social"
# Returns: {"did":"did:plc:alicesdid456"}
```

**Step 3: View Bob's blocks on pdsls.dev**
```
https://pdsls.dev/at/did:plc:bobsdid123/app.bsky.graph.block
```

**Step 4: Look for Alice's DID**

Browse the block records. If you see a record where:
```json
{
  "subject": "did:plc:alicesdid456",
  ...
}
```

Then yes, Bob has blocked Alice.

**Alternative: Direct API query**
```bash
curl "https://bsky.social/xrpc/com.atproto.repo.listRecords?repo=did:plc:bobsdid123&collection=app.bsky.graph.block" | grep "alicesdid456"
```

If this returns a match, Bob has blocked Alice.

---

## Using pdsls.dev Interface

**Navigation steps within pdsls.dev:**

1. Go to: `https://pdsls.dev`
2. Enter the blocker's handle or DID in the search
3. You'll see their repository overview with collections like:
   - `app.bsky.actor.profile`
   - `app.bsky.feed.post`
   - `app.bsky.graph.follow`
   - `app.bsky.graph.block` ← Click here
4. This shows all their block records
5. Click on individual records to see details

**What you'll see:**
- List of record keys (rkeys) like `3l4abc123xyz`
- Click a record to see full details including the blocked person's DID
- Timestamps showing when blocks were created

---

## Privacy Considerations

**Remember:**
- This is all public data by design
- Anyone can view anyone's blocks
- Be respectful with this information
- Don't use it for harassment or call-outs
- Consider that people block for many valid reasons

**Why blocks are public in ATProto:**

From Bluesky's blog:
> "In planning out how blocks would work in a federated system, we knew that there was a tension between making the actions public enough that all the services in the network could act upon them, but also the potential for harassment and call-outs if blocks were entirely public and enumerable. In the end we could not come up with a design for meaningfully 'private' blocks while still having the block behaviors enforced consistently."

---

## Troubleshooting

**"No records found"**
- The person may not have any active blocks
- Or they haven't blocked the specific person you're looking for

**"Invalid DID"**
- Double-check you have the correct DID format
- Make sure it starts with `did:plc:` or `did:web:`

**"pdsls.dev requires JavaScript"**
- Make sure JavaScript is enabled in your browser
- Try a different browser if issues persist

**Handle changed**
- If someone changed their handle, the old handle won't work
- DIDs are permanent, so use the DID instead

---

## Quick Reference URLs

**Resolve handle to DID:**
```
https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=HANDLE
```

**View someone's blocks on pdsls.dev:**
```
https://pdsls.dev/at/did:plc:THEIR_DID/app.bsky.graph.block
```

**View someone's blocks via API:**
```
https://bsky.social/xrpc/com.atproto.repo.listRecords?repo=did:plc:THEIR_DID&collection=app.bsky.graph.block
```

**View specific block record:**
```
https://pdsls.dev/at/did:plc:THEIR_DID/app.bsky.graph.block/RKEY
```

---

## Other Useful Collections

While you're exploring, here are other public collections you can view:

- `app.bsky.graph.follow` - Who they follow
- `app.bsky.feed.post` - Their posts
- `app.bsky.feed.like` - Their likes
- `app.bsky.feed.repost` - Their reposts
- `app.bsky.graph.listitem` - List memberships

**URL format is the same:**
```
https://pdsls.dev/at/did:plc:THEIR_DID/{collection}
```

---

**Created:** 2025-11-08
**Tool:** pdsls.dev
**Collection:** app.bsky.graph.block
