# Bluesky Handle Change Guide: Moving to a New Domain

**Created:** 2025-11-08
**Task:** Change Bluesky handle from one custom domain to another (both owned by you)

---

## Quick Answer

**Almost that simple, but not quite.** Here's what you're forgetting:

1. **You can't just copy the record** - Bluesky needs to generate a new verification code for the new domain
2. **DNS propagation** - Need to wait 5-10 minutes (up to 48 hours in rare cases)
3. **Old handle behavior** - Your old custom domain handle will become available to others
4. **Verification order matters** - Set up DNS first, THEN verify in app
5. **TTL settings** - Lower TTL temporarily for faster propagation

But don't worry - this is **MUCH safer** than PDS migration. Handle changes are reversible and low-risk.

---

## Step-by-Step Guide

### Phase 1: Preparation (5 minutes)

**1.1 Get Your DID**

Your DID never changes - it's your permanent identity. You need this for the DNS record.

```bash
# Method 1: Check your current DNS record
dig _atproto.yourcurrentdomain.com TXT

# Method 2: Use your handle
# Go to: https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=yourcurrenthandle.com
# This returns: {"did":"did:plc:xxxxxxxxxx"}

# Method 3: Look it up on pdsls.dev
# Visit: https://pdsls.dev/at/@yourcurrenthandle.com
```

Your DID looks like: `did:plc:abcd1234efgh5678ijkl`

**Save this somewhere safe - you'll need it.**

**1.2 Document Current State**

```bash
# Take screenshots of:
# - Your current profile showing your handle
# - Your follower count
# - A recent post

# Test current DNS record
dig _atproto.yourcurrentdomain.com TXT
# Should return something like:
# _atproto.yourcurrentdomain.com. 300 IN TXT "did=did:plc:your-did-here"
```

**1.3 Decide on Your New Handle**

Options:
- Root domain: `newdomain.com` → DNS record: `_atproto.newdomain.com`
- Subdomain: `me.newdomain.com` → DNS record: `_atproto.me.newdomain.com`
- Social subdomain: `social.newdomain.com` → DNS record: `_atproto.social.newdomain.com`

**Pro tip:** Using a subdomain (like `me.newdomain.com`) gives you flexibility to use the root domain for a website.

---

### Phase 2: DNS Configuration (10 minutes)

**2.1 Lower TTL on Old Record (Optional but Recommended)**

In your old domain's Route53 hosted zone:

1. Find the existing `_atproto` TXT record
2. Change TTL from 300 (or whatever it is) to **60 seconds**
3. Wait for the old TTL period (if it was 300, wait 5 minutes)

**Why?** This makes it easier to troubleshoot if you need to make changes.

**2.2 Create New DNS Record**

In your **new domain's Route53 hosted zone**:

1. Go to AWS Console → Route53 → Hosted Zones
2. Select your new domain's hosted zone
3. Click "Create record"

**Record configuration:**

```
Record name: _atproto
(or for subdomain: _atproto.yoursub)

Record type: TXT

Value: "did=did:plc:YOUR-ACTUAL-DID-HERE"
(Include the quotes in Route53!)

TTL: 60 seconds (temporarily low for testing)

Routing policy: Simple routing
```

**CRITICAL GOTCHAS:**

- ✅ **DO** include `did=` before your DID
- ✅ **DO** wrap the entire value in quotes: `"did=did:plc:xxxxx"`
- ✅ **DO** use exactly `_atproto` (with underscore, all lowercase)
- ❌ **DON'T** include the domain name in the record name (Route53 adds it automatically)
- ❌ **DON'T** forget the underscore in `_atproto`
- ❌ **DON'T** add extra spaces or line breaks

**Example of what it looks like in Route53:**

```
Name: _atproto.newdomain.com  (or _atproto.me.newdomain.com for subdomain)
Type: TXT
Value: "did=did:plc:abcd1234efgh5678ijkl"
TTL: 60
```

**2.3 Verify DNS Record**

**IMPORTANT: Wait 5-10 minutes after creating the record before verifying!**

```bash
# Test DNS propagation
dig _atproto.newdomain.com TXT

# Or for subdomain
dig _atproto.me.newdomain.com TXT

# Expected output:
# _atproto.newdomain.com. 60 IN TXT "did=did:plc:your-did-here"
```

**If `dig` doesn't show the record yet:**

```bash
# Try querying different DNS servers
dig @8.8.8.8 _atproto.newdomain.com TXT  # Google DNS
dig @1.1.1.1 _atproto.newdomain.com TXT  # Cloudflare DNS

# Check global propagation
# Use online tools:
# - https://dnschecker.org
# - https://www.whatsmydns.net
```

**Wait until at least 2-3 different DNS servers show your record before proceeding.**

---

### Phase 3: Change Handle in Bluesky (5 minutes)

**3.1 Start Handle Change**

In the Bluesky app:

1. Go to **Settings** → **Account** → **Handle**
2. Click **"Change handle"** or **"I have my own domain"**
3. Enter your new domain (e.g., `newdomain.com` or `me.newdomain.com`)

**3.2 Bluesky Shows You a Record**

Bluesky will generate something like:

```
Host: _atproto
Value: did=did:plc:abcd1234efgh5678ijkl
```

**This should match what you already set up in Route53!**

If it matches, great - you're ahead of the game.

**If it shows a different value:** This would be very strange since your DID doesn't change. Double-check you copied your DID correctly.

**3.3 Verify**

1. Click **"Verify DNS Record"** in the Bluesky app

**Possible outcomes:**

✅ **Success:** "Handle verified! Your handle is now newdomain.com"
- Congratulations! You're done.

❌ **Error: "Unable to verify DNS record"**
- Wait another 5 minutes for DNS propagation
- Try again
- Check DNS with `dig` command to confirm record exists
- Clear your browser/app cache
- Try from a different device

❌ **Error: "Invalid handle"**
- Your domain might not be accessible via HTTPS
- Check if newdomain.com has a valid SSL certificate
- Try the alternative method (well-known file) instead

**3.4 Confirm Change**

Once verified:
- Your profile should immediately show the new handle
- Your DID remains the same (verify at https://pdsls.dev/at/@newdomain.com)
- All your followers, posts, and data are intact

---

### Phase 4: Cleanup & Verification (Next 24 hours)

**4.1 Immediate Checks (5 minutes after change)**

- [ ] Profile shows new handle
- [ ] Can make a new post
- [ ] Can like/reply to posts
- [ ] Mentions still work
- [ ] Old posts are still visible

**4.2 Test Mentions**

Ask a friend to mention you with your new handle: `@newdomain.com`

**4.3 Test Handle Resolution**

```bash
# Check that your new handle resolves to your DID
curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=newdomain.com"
# Should return: {"did":"did:plc:your-did-here"}

# Check on pdsls.dev
# Visit: https://pdsls.dev/at/@newdomain.com
```

**4.4 Old Handle Behavior**

⚠️ **Important:** Your old custom domain handle is now available for anyone else to claim.

**Options:**

1. **Do nothing** - Old handle becomes available to others
   - Old mentions still work (they're based on DID)
   - Old profile URLs won't redirect to new handle

2. **Keep old DNS record** (if you still own the domain)
   - Leave the old `_atproto.olddomain.com` TXT record in place
   - This "parks" the old handle
   - No one else can claim it
   - You could even create a second account and assign it to the old handle

3. **Set up redirect** (advanced)
   - Create a landing page at olddomain.com
   - Explain you've moved to newdomain.com
   - Not automatic, but helps people find you

**If you're keeping the old domain:**
```bash
# Keep this record in the old domain's Route53 zone:
_atproto.olddomain.com TXT "did=did:plc:your-did-here"

# Anyone searching for @olddomain.com will get an "invalid handle" error
# because your DID now points to the new handle, creating a conflict
```

**Actually, on second thought:** If you want to truly park the old handle, you'd need a different DID (second account). Your single DID can only point to one handle at a time.

**4.5 Increase TTL (after 24 hours)**

Once everything is working perfectly:

1. Go back to Route53
2. Change TTL on `_atproto.newdomain.com` from 60 to 300 or 3600
3. Save changes

**Why?** Lower TTL = more DNS queries = slightly higher costs (though negligible). Standard TTL is fine once everything is stable.

**4.6 Optional: Delete Old DNS Record**

If you no longer need the old domain for Bluesky:

1. Go to old domain's Route53 hosted zone
2. Delete the `_atproto.olddomain.com` TXT record
3. Consider deleting the entire hosted zone if you're not using the domain

---

## What You're Actually Forgetting (Checklist)

Let me highlight the things people commonly forget:

- [ ] **DNS record format** - Must be exactly `"did=did:plc:xxxxx"` with quotes
- [ ] **Underscore in _atproto** - Easy to forget the underscore
- [ ] **Wait for propagation** - Don't verify immediately, wait 5-10 minutes
- [ ] **Subdomain vs root** - Record name changes if using subdomain
- [ ] **Old handle availability** - Becomes available to others (can't prevent with same DID)
- [ ] **SSL certificate** - New domain must have valid HTTPS/SSL
- [ ] **Lower TTL first** - Makes troubleshooting faster
- [ ] **Test with dig** - Verify DNS before trying in app
- [ ] **Clear cache** - If verification fails, try different device/browser

---

## Alternative Method: HTTPS Well-Known File

If DNS verification fails or you prefer this method:

**1. Create file at:** `https://newdomain.com/.well-known/atproto-did`

**2. File contents:**
```
did:plc:your-did-here
```
(Just the DID, nothing else, no quotes, no "did=")

**3. Set Content-Type:** `text/plain`

**4. Verify it's accessible:**
```bash
curl https://newdomain.com/.well-known/atproto-did
# Should return: did:plc:your-did-here
```

**5. In Bluesky app:** When changing handle, select "Verify with HTTP" instead of DNS

**Pros:** No DNS required, instant (no propagation)
**Cons:** Requires web server, file hosting, SSL certificate

---

## Troubleshooting Common Issues

### "Unable to verify DNS record"

**Cause:** DNS hasn't propagated yet
**Solution:** Wait 10-15 minutes, try again

**Cause:** Record formatted incorrectly
**Solution:**
```bash
# Check your record
dig _atproto.newdomain.com TXT

# Should return EXACTLY:
"did=did:plc:your-did-here"

# Common mistakes:
# ❌ "did:plc:xxxxx" (missing "did=")
# ❌ did=did:plc:xxxxx (missing quotes)
# ❌ "did = did:plc:xxxxx" (extra spaces)
```

**Cause:** Wrong record name
**Solution:** Must be `_atproto` (with underscore), not `atproto`

### "Invalid handle"

**Cause:** Domain doesn't have valid SSL certificate
**Solution:** Set up SSL/TLS for your domain (use AWS Certificate Manager)

**Cause:** Domain doesn't resolve
**Solution:** Ensure newdomain.com has A/CNAME records pointing somewhere

### "DID mismatch"

**Cause:** You used the wrong DID
**Solution:** Get your actual DID from current handle, use that exact value

### Verification works but handle doesn't change

**Cause:** App cache issue
**Solution:** Log out, log back in. Or try from different device.

---

## Complete Example Walkthrough

**Scenario:** Moving from `social.olddomain.com` to `me.newdomain.com`

**Step 1: Get DID**
```bash
$ dig _atproto.social.olddomain.com TXT
; Returns: "did=did:plc:abc123xyz789"
# My DID is: did:plc:abc123xyz789
```

**Step 2: Create DNS Record in Route53**

In newdomain.com hosted zone:
```
Name: _atproto.me
Type: TXT
Value: "did=did:plc:abc123xyz789"
TTL: 60
```

Full record name will be: `_atproto.me.newdomain.com`

**Step 3: Wait and Verify**
```bash
$ sleep 300  # Wait 5 minutes

$ dig _atproto.me.newdomain.com TXT
; Returns: "did=did:plc:abc123xyz789"
✅ Good to go!
```

**Step 4: Change in Bluesky App**
1. Settings → Account → Handle
2. "I have my own domain"
3. Enter: `me.newdomain.com`
4. Verify DNS Record
5. ✅ Success! Handle changed

**Step 5: Verify**
```bash
$ curl "https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle=me.newdomain.com"
{"did":"did:plc:abc123xyz789"}
✅ Working!
```

**Step 6: 24 hours later**
- Change TTL from 60 to 3600
- Consider removing old `_atproto.social.olddomain.com` record
- Done!

---

## Quick Reference: DNS Record Format

### Root Domain Handle

**Want handle:** `newdomain.com`

**Route53 record:**
```
Name: _atproto
Type: TXT
Value: "did=did:plc:YOUR-DID"
TTL: 60 (initially), then 3600
```

**Full FQDN:** `_atproto.newdomain.com`

### Subdomain Handle

**Want handle:** `me.newdomain.com`

**Route53 record:**
```
Name: _atproto.me
Type: TXT
Value: "did=did:plc:YOUR-DID"
TTL: 60 (initially), then 3600
```

**Full FQDN:** `_atproto.me.newdomain.com`

### Multiple Subdomains

**Want handle:** `bsky.social.newdomain.com`

**Route53 record:**
```
Name: _atproto.bsky.social
Type: TXT
Value: "did=did:plc:YOUR-DID"
TTL: 60 (initially), then 3600
```

**Full FQDN:** `_atproto.bsky.social.newdomain.com`

---

## Safety & Rollback

**Can I go back?**
Yes! Handle changes are fully reversible.

**Rollback procedure:**
1. Keep the old DNS record in place (don't delete it)
2. Go back to Settings → Handle in Bluesky
3. Change back to old handle
4. Verify
5. You're back to the old handle

**Your DID never changes** - it's your permanent identity. Handles are just pointers to your DID.

**Data loss?** None. Changing handles doesn't affect:
- Posts
- Followers
- Following
- Likes
- Blocks
- Lists
- Any other data

**Downtime?** Essentially zero. The handle change is atomic - it happens instantly once verified.

---

## Cost Implications (AWS)

**Route53 Hosted Zone:** $0.50/month per domain
**TXT Record:** Included (first 10,000 queries per month are free)
**DNS Queries:** $0.40 per million queries after free tier

**For personal use:** Negligible cost, probably $0.50/month total if you already have the hosted zone.

**If creating new hosted zone just for Bluesky:** Consider if $6/year is worth it vs. using the .well-known file method on existing hosting.

---

## Timeline Summary

| Phase | Time | Can Speed Up? |
|-------|------|---------------|
| Get DID | 1 min | ✅ Have it ready |
| Create DNS record | 2 min | ✅ Prepare in advance |
| DNS propagation | 5-10 min | ✅ Lower TTL first |
| Verify in app | 1 min | ❌ Must wait for DNS |
| **Total** | **10-15 min** | **Total: ~15 min** |

---

## Final Checklist

Before you start:
- [ ] I have my DID saved
- [ ] New domain is in Route53
- [ ] New domain has valid SSL (or I'm OK with well-known method)
- [ ] I've decided on root domain vs subdomain
- [ ] I've lowered TTL on old record (optional)

During setup:
- [ ] Created `_atproto` TXT record in new domain's hosted zone
- [ ] Value is exactly `"did=did:plc:MY-ACTUAL-DID"`
- [ ] Waited 5-10 minutes
- [ ] Verified with `dig` command
- [ ] Seen record on at least 2 different DNS servers

In Bluesky app:
- [ ] Changed handle to new domain
- [ ] Verified successfully
- [ ] Profile shows new handle
- [ ] Made a test post

After 24 hours:
- [ ] Increased TTL to 3600
- [ ] Decided what to do with old DNS record
- [ ] Tested that everything still works

---

## You Got This!

This is a **low-risk, reversible operation**. Unlike PDS migration, this is:
- ✅ Safe
- ✅ Supported
- ✅ Reversible
- ✅ No data loss
- ✅ Takes 15 minutes
- ✅ Well-documented
- ✅ Commonly done

The only thing you can mess up is the DNS record format, and even that is easily fixable.

**Worst case scenario:** DNS verification fails, you wait a bit, fix the record, try again. No harm done.

---

**Created:** 2025-11-08
**Status:** Ready to use
**Risk Level:** Low
