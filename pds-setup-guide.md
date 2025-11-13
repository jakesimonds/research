# ATProto PDS Setup Guide - AWS EC2 + Account Migration

**Use Case:** Set up a Personal Data Server (PDS) on AWS EC2 and migrate an existing Bluesky account to it.

**Timeline:** 2-3 hours total
**Cost:** ~$15-20 for 2 weeks (t3.micro)

---

## ⚠️ Critical Warnings

**READ THIS FIRST:**

1. **This is experimental** - Federation is still in beta (as of November 2024)
2. **Use a test account first** - DO NOT migrate your primary account initially
3. **Permanent lockout risk** - If migration fails, you could lose access to your account
4. **No Bluesky support** - They cannot help recover your account if something goes wrong
5. **Keep old account accessible for 30+ days** after migration

**Recommended:** Practice this entire process with a throwaway test account before attempting with any account you care about.

---

## Part 1: AWS EC2 Setup

### Step 1: Launch EC2 Instance

1. **Go to AWS Console → EC2 → Launch Instance**

2. **Configure instance:**
   ```
   Name: atproto-pds

   AMI: Ubuntu Server 22.04 LTS (64-bit x86)

   Instance type: t3.micro (for testing/low activity)
                  t3.small (for production use)

   Key pair: Create new or select existing
             (You'll need this to SSH in)

   Network settings:
   ✓ Allow SSH (22) from your IP
   ✓ Allow HTTP (80) from anywhere (0.0.0.0/0)
   ✓ Allow HTTPS (443) from anywhere (0.0.0.0/0)

   Storage: 20 GB gp3 (minimum)
            30 GB gp3 (recommended)

   Advanced details:
   - Leave defaults
   ```

3. **Launch instance**

### Step 2: Allocate Elastic IP (Important!)

**Why:** EC2 public IPs change on restart. Elastic IPs are static.

1. **EC2 Console → Network & Security → Elastic IPs**
2. **Allocate Elastic IP address**
3. **Actions → Associate Elastic IP address**
   - Select your PDS instance
   - Associate

**Note the Elastic IP** - you'll need it for DNS

### Step 3: Install Dependencies

**SSH into your instance:**

```bash
# Replace with your key and Elastic IP
ssh -i your-key.pem ubuntu@YOUR_ELASTIC_IP
```

**Install Docker:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose git curl

# Add ubuntu user to docker group (avoid needing sudo)
sudo usermod -aG docker ubuntu

# Log out and back in for group change to take effect
exit
ssh -i your-key.pem ubuntu@YOUR_ELASTIC_IP

# Verify Docker works
docker --version
docker-compose --version
```

---

## Part 2: Route 53 Domain Setup

### Step 1: Choose Your Subdomain

**Recommended format:** `pds.yourdomain.com`

**Example:** If you own `example.com`, use `pds.example.com`

### Step 2: Create DNS Records in Route 53

1. **Go to Route 53 → Hosted Zones → Select your domain**

2. **Create A Record:**
   ```
   Click "Create record"

   Record name: pds
   Record type: A - Routes traffic to an IPv4 address
   Value: YOUR_ELASTIC_IP (from Step 2.2)
   TTL: 300
   Routing policy: Simple routing

   Create record
   ```

3. **Verify DNS propagation:**

   ```bash
   # From your local machine
   dig pds.yourdomain.com

   # Or use nslookup
   nslookup pds.yourdomain.com

   # Should show your Elastic IP
   ```

   **Note:** DNS can take 5-60 minutes to propagate. Wait until it resolves correctly.

---

## Part 3: PDS Installation

### Step 1: Clone Official PDS Repository

```bash
# SSH into your EC2 instance
cd ~
git clone https://github.com/bluesky-social/pds.git
cd pds
```

### Step 2: Run Installer

```bash
sudo bash installer.sh
```

**The installer will prompt you for:**

```
Enter your public hostname (e.g. example.com): pds.yourdomain.com

Enter your admin email (for Let's Encrypt): your.email@example.com

Do you want to enable email service? [y/N]: N
(Unless you plan to run email, choose N)

Do you want to enable blob storage? [y/N]: y
(Choose y to store images/videos)
```

**The installer will:**
- Generate secure passwords
- Create `.env` configuration file
- Set up automatic TLS certificates (Let's Encrypt)
- Configure Docker Compose

### Step 3: Review Configuration

```bash
cat pds.env
```

**Key settings to verify:**

```bash
PDS_HOSTNAME=pds.yourdomain.com
PDS_ADMIN_EMAIL=your.email@example.com

# These are auto-generated - DO NOT LOSE THEM
PDS_JWT_SECRET=<random-secret>
PDS_ADMIN_PASSWORD=<random-password>
PDS_PLC_ROTATION_KEY_K256_PRIVATE_KEY_HEX=<key>

# Storage settings
PDS_BLOBSTORE_DISK_LOCATION=/pds/blocks
PDS_DATA_DIRECTORY=/pds
```

**IMPORTANT:** Backup this file securely! You'll need these secrets if you ever restore the server.

```bash
# Copy to your local machine
scp -i your-key.pem ubuntu@YOUR_ELASTIC_IP:~/pds/pds.env ~/pds-backup.env
```

### Step 4: Start PDS

```bash
cd ~/pds
sudo docker-compose up -d
```

**Wait 2-3 minutes for startup, then check:**

```bash
# Check containers are running
docker ps

# Should see something like:
# CONTAINER ID   IMAGE                  STATUS
# xxxxx          ghcr.io/bluesky-social/pds:latest   Up 2 minutes

# Check logs
docker-compose logs -f

# Press Ctrl+C to exit logs
```

### Step 5: Verify PDS is Working

```bash
# Check health endpoint
curl https://pds.yourdomain.com/xrpc/_health

# Should return:
# {"version":"0.x.x"}

# Check TLS certificate
curl -I https://pds.yourdomain.com

# Should show:
# HTTP/2 200
# (Certificate should be from Let's Encrypt)
```

**If health check fails:**
- Verify DNS is resolving correctly
- Check Docker logs: `docker-compose logs`
- Ensure ports 80/443 are open in security groups
- Wait a few more minutes for Let's Encrypt cert issuance

---

## Part 4: Create Test Account (DO THIS FIRST!)

**Before migrating your real account, test the PDS:**

### Option A: Via Bluesky App

1. Open Bluesky app
2. Go to **Settings → Account → Hosting Provider**
3. Tap **Change Service**
4. Enter: `https://pds.yourdomain.com`
5. **Sign up** with a new test account

### Option B: Via API

```bash
curl -X POST https://pds.yourdomain.com/xrpc/com.atproto.server.createAccount \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "handle": "testuser.pds.yourdomain.com",
    "password": "secure-password-here"
  }'
```

**Verify:**
- Log into the test account
- Post something
- Verify it appears in Bluesky
- Upload an image
- Follow someone and verify federation works

**Let it run for 24-48 hours** to ensure stability before migrating real accounts.

---

## Part 5: Account Migration (Use PDS MOOver - Recommended)

### Why PDS MOOver?

- Handles all 4 migration stages automatically
- Has backup/restore functionality
- Client-side (data stays in your browser)
- Free for individual accounts
- Has recovery tools if something goes wrong

**Official Tool:** https://pdsmoover.com

### Step 1: Pre-Migration Checklist

**Complete ALL of these:**

- [ ] Test account successfully created and working on your PDS
- [ ] PDS has been stable for 24+ hours
- [ ] DNS is correctly configured and stable
- [ ] TLS certificate is valid (https works)
- [ ] You have backed up `pds.env` file locally
- [ ] You have screenshots of your current account (profile, follower count, post count)
- [ ] You understand this is risky and potentially destructive
- [ ] This is NOT your primary account (or you accept the risk)
- [ ] You have 2-4 hours of uninterrupted time
- [ ] Your device won't go to sleep (for blob uploads)

### Step 2: Backup Current Account

1. **Go to https://pdsmoover.com**

2. **Click "Backup" tab**

3. **Enter credentials:**
   ```
   PDS URL: https://bsky.social
   Handle: yourhandle.bsky.social
   Password: your-current-password
   ```

4. **Click "Create Backup"**

5. **Wait for completion** (can take 10-60 minutes depending on account size)

6. **Download backup file** to your local machine as additional safety

7. **Verify backup shows success**

### Step 3: Execute Migration

1. **Still on https://pdsmoover.com, go to "Migrate" tab**

2. **Enter source PDS:**
   ```
   Source PDS: https://bsky.social
   Handle: yourhandle.bsky.social
   Password: your-current-password
   ```

3. **Enter destination PDS:**
   ```
   Destination PDS: https://pds.yourdomain.com
   Handle: yourhandle.pds.yourdomain.com
   Password: choose-a-new-password
   ```

4. **Click "Start Migration"**

5. **DO NOT CLOSE THE BROWSER TAB**

### Step 4: Wait for Migration Stages

The migration will proceed through 4 stages:

**Stage 1: Account Creation** (1-2 minutes)
- Creates account on new PDS
- Transfers identity

**Stage 2: Repository Transfer** (5-20 minutes)
- Migrates all posts, likes, follows, blocks
- Transfers preferences

**Stage 3: Blob Upload** (30 minutes to several hours)
- Uploads all images and videos
- **This is the longest part**
- Progress bar shows current file being uploaded
- **IMPORTANT:** Blobs upload sequentially, not in parallel

**Stage 4: DID Update & Activation** (2-5 minutes)
- Updates DID document to point to new PDS
- Activates account
- Old PDS can no longer update your DID

### Step 5: Monitor Progress

**What you'll see:**
```
✓ Stage 1: Account created
✓ Stage 2: Repository transferred (12,543 records)
⏳ Stage 3: Uploading blobs... (147/523)
   Currently uploading: image-abc123.jpg (2.3 MB)
```

**If it stalls:**
- Check browser console for errors (F12)
- Check your PDS logs: `docker-compose logs -f`
- Check disk space: `df -h`
- DO NOT refresh or close browser

**Typical timings:**
- Small account (<100 images): 30-60 minutes
- Medium account (100-500 images): 1-3 hours
- Large account (1000+ images): 4-12 hours

### Step 6: Verify Migration Success

Once complete, verify:

```bash
# Check your DID document points to new PDS
curl https://plc.directory/YOUR_DID | jq

# Should show:
# "service": [
#   {
#     "id": "#atproto_pds",
#     "type": "AtprotoPersonalDataServer",
#     "serviceEndpoint": "https://pds.yourdomain.com"
#   }
# ]
```

**In Bluesky app:**
- [ ] Log out and log back in
- [ ] Verify all posts are visible
- [ ] Check follower/following counts match
- [ ] Verify images and videos load
- [ ] Post new content and verify it federates
- [ ] Check that your handle works

### Step 7: Handle Missing Blobs (If Needed)

If some images/videos are missing:

1. **Go back to https://pdsmoover.com**
2. **Click "Missing" tab**
3. **Enter your credentials**
4. **Tool will find and upload missing blobs**

**Note:** You have ~30 days to recover missing blobs from old PDS.

---

## Part 6: Post-Migration Monitoring

### First 24 Hours

**Check every few hours:**

```bash
# SSH into your server
ssh -i your-key.pem ubuntu@YOUR_ELASTIC_IP

# Check PDS health
curl https://pds.yourdomain.com/xrpc/_health

# Check Docker containers
docker ps

# Check logs for errors
cd ~/pds
docker-compose logs --tail=100

# Check disk usage
df -h
# Should have plenty free
```

**In Bluesky:**
- Post updates
- Verify federation (ask a friend to check if they see your posts)
- Test all features (posting, following, liking, etc.)

### First Week

**Daily checks:**
- PDS health endpoint
- Post at least once to verify federation
- Monitor disk space
- Check Docker logs for any errors

**DO NOT delete old account yet** - keep it accessible for 30+ days

### 30 Days Later

If everything has been stable:
- Consider deactivating old account
- Keep it for another 30 days before permanent deletion
- After 60 days total, safe to delete

---

## Part 7: Maintenance

### Daily Health Checks

```bash
# Create a simple monitoring script
cat > ~/check-pds.sh << 'EOF'
#!/bin/bash
echo "=== PDS Health Check ==="
echo "Time: $(date)"
echo ""

echo "1. Health endpoint:"
curl -s https://pds.yourdomain.com/xrpc/_health
echo ""

echo "2. Docker status:"
docker ps --format "table {{.Names}}\t{{.Status}}"
echo ""

echo "3. Disk usage:"
df -h | grep -E '(Filesystem|/dev/root)'
echo ""

echo "4. Memory:"
free -h
echo ""

echo "=== Check complete ==="
EOF

chmod +x ~/check-pds.sh

# Run it
./check-pds.sh
```

### Weekly Checks

```bash
# Check for Docker image updates
cd ~/pds
docker-compose pull

# If updates available
docker-compose up -d

# Check logs after restart
docker-compose logs --tail=50
```

### When to Worry

**Check logs immediately if:**
- Health endpoint returns error
- Can't post or view your profile
- Disk usage over 80%
- Docker container restarts repeatedly

```bash
# View recent errors
docker-compose logs --tail=200 | grep -i error

# Follow logs in real-time
docker-compose logs -f
```

---

## Part 8: Backup Strategy (Optional but Recommended)

### EBS Snapshot (Simple Approach)

1. **AWS Console → EC2 → Volumes**
2. **Select your PDS instance volume**
3. **Actions → Create Snapshot**
4. **Name it:** `pds-backup-YYYY-MM-DD`

**To restore:**
1. Create new volume from snapshot
2. Attach to new EC2 instance
3. Start PDS

### Manual Backup (Alternative)

```bash
# Stop PDS temporarily
cd ~/pds
docker-compose stop

# Backup data directory
sudo tar -czf pds-backup-$(date +%Y%m%d).tar.gz /pds

# Restart PDS
docker-compose start

# Download backup to local machine
scp -i your-key.pem ubuntu@YOUR_ELASTIC_IP:~/pds-backup-*.tar.gz ~/
```

---

## Troubleshooting

### PDS won't start

```bash
# Check logs
docker-compose logs

# Common issues:
# - Port 443 already in use: something else using that port
# - DNS not resolving: wait longer or check Route53
# - Cert issuance failed: check DNS is correct and port 80 is open
```

### Can't access via HTTPS

```bash
# Check if Let's Encrypt cert was issued
docker-compose logs | grep -i certificate

# If cert failed, check:
# 1. DNS resolves to correct IP
# 2. Port 80 is open (needed for ACME challenge)
# 3. Hostname in pds.env is correct
```

### Migration fails mid-process

**DO NOT PANIC**

1. Check PDS logs for errors
2. Check disk space isn't full
3. Go back to PDS MOOver and use "Missing" tab to recover
4. If DID was already updated, your account is on new PDS (blobs can be recovered later)
5. Ask in ATProto Discord: https://discord.gg/atproto

### Old posts visible but can't create new ones

**This means DID wasn't updated properly:**

```bash
# Check your DID document
curl https://plc.directory/YOUR_DID

# If it still points to old PDS, migration didn't complete
# You may need to manually update DID (advanced - see official docs)
```

---

## Cost Estimate

### 2 Weeks (Hackathon)
```
EC2 t3.micro:     $7-8
EBS 20GB:         $1
Data transfer:    $1-2
Route53:          $0.50
Elastic IP:       Free (while associated)
----------------------------
Total:            ~$10-12
```

### Monthly (Production)
```
EC2 t3.small:     $15-17
EBS 30GB:         $3
Data transfer:    $5-10
Route53:          $0.50
Backups:          $2-5
----------------------------
Total:            ~$25-35/month
```

### When You're Done (Delete Everything)

```bash
# SSH into instance and stop PDS
cd ~/pds
docker-compose down

# AWS Console:
# 1. EC2 → Instances → Terminate
# 2. Volumes → Delete (if not auto-deleted)
# 3. Elastic IPs → Release
# 4. Route53 → Delete A record

# Final charges: Just what you used (~$10-12 for 2 weeks)
```

---

## Resources

**Official Documentation:**
- PDS GitHub: https://github.com/bluesky-social/pds
- Migration Guide: https://github.com/bluesky-social/pds/blob/main/ACCOUNT_MIGRATION.md
- ATProto Self-Hosting: https://atproto.com/guides/self-hosting

**Tools:**
- PDS MOOver: https://pdsmoover.com
- Account Viewer: https://pdsls.dev
- PLC Directory: https://plc.directory

**Community:**
- ATProto Discord: https://discord.gg/atproto
- GitHub Discussions: https://github.com/bluesky-social/atproto/discussions

**Related Research in This Repo:**
- Full research findings: `/bluesky-did-research/RESEARCH_FINDINGS.md`
- Quick reference: `/bluesky-did-research/QUICK_REFERENCE.md`

---

## Final Recommendations

1. **Test with throwaway account first** - Cannot stress this enough
2. **Do this on a weekend** - Give yourself time if things go wrong
3. **Join ATProto Discord BEFORE you start** - Help is available if needed
4. **Screenshot everything** - Your current account state
5. **Don't rush** - Especially during blob uploads
6. **Keep old account for 60 days** - Safety net

**Good luck!** 🚀

---

**Created:** 2025-11-13
**Last Updated:** 2025-11-13
**Tested On:** AWS EC2 Ubuntu 22.04, PDS 0.4.x
