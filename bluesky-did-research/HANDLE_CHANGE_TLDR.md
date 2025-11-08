# Handle Change TL;DR

## What You're Forgetting

You **cannot just copy the record** between hosted zones. Here's the complete process:

### 1. Get Your DID (1 minute)
```bash
dig _atproto.yourcurrentdomain.com TXT
# Returns: "did=did:plc:abc123xyz"
# Save this: did:plc:abc123xyz
```

### 2. Create DNS Record in NEW Domain (2 minutes)

In Route53 for **newdomain.com**:
```
Name: _atproto
Type: TXT
Value: "did=did:plc:abc123xyz"
TTL: 60
```

**CRITICAL FORMAT:**
- ✅ Include quotes: `"did=did:plc:..."`
- ✅ Include `did=` prefix
- ✅ Use underscore: `_atproto`

### 3. Wait for DNS (5-10 minutes)
```bash
# Test before proceeding
dig _atproto.newdomain.com TXT

# Should show your record
```

### 4. Verify in Bluesky App (1 minute)

Settings → Account → Handle → "I have my own domain" → Enter newdomain.com → Verify

### 5. Done!

Your handle changes instantly. No data loss, fully reversible.

---

## Common Mistakes

❌ Copying old record without updating it
❌ Forgetting the underscore: `_atproto`
❌ Wrong format: missing quotes or `did=` prefix
❌ Verifying immediately (DNS needs time to propagate)
❌ Wrong record name for subdomains

---

## For Subdomain (e.g., me.newdomain.com)

```
Name: _atproto.me
Type: TXT
Value: "did=did:plc:abc123xyz"
```

Full name will be: `_atproto.me.newdomain.com`

---

## Testing

```bash
# Must return your record before verifying in app
dig _atproto.newdomain.com TXT

# Also test with Google DNS
dig @8.8.8.8 _atproto.newdomain.com TXT
```

---

## What Happens to Old Handle?

- Old custom domain handle becomes available to others
- You cannot "reserve" it with same DID (one DID = one handle)
- Old mentions still work (they use your DID, not handle)
- To park it, you'd need a second account with different DID

---

## If Something Goes Wrong

1. Wait 10 more minutes for DNS
2. Check DNS record format (quotes, `did=` prefix, underscore)
3. Clear cache, try different browser
4. Worst case: delete record, start over (no harm done)

---

## Risk Level: LOW

This is safe, reversible, and takes 15 minutes total.

Read full guide: `HANDLE_CHANGE_GUIDE.md`
