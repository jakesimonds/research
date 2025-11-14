# 🚀 EC2 Setup Guide - Step by Step

Complete walkthrough for deploying the honeypot on AWS EC2.

## Part 1: Launch EC2 Instance (AWS Console)

1. **Go to EC2 Dashboard**
   - Navigate to: https://console.aws.amazon.com/ec2/

2. **Click "Launch Instance"**

3. **Configure Instance:**
   ```
   Name: honeypot-demo

   AMI: Amazon Linux 2023 AMI
   (Or: Ubuntu Server 22.04 LTS)

   Instance Type: t2.micro
   (Free tier eligible - $0 cost if within limits)

   Key pair: Create new or use existing
   (Download .pem file if creating new)

   Network Settings:
   ✅ Allow SSH from: My IP
   ✅ Allow HTTP from: Anywhere (0.0.0.0/0)

   Storage: 8 GB gp3 (default is fine)
   ```

4. **Click "Launch Instance"**

5. **Wait ~2 minutes** for instance to start

6. **Note your Public IP**
   - Click on your instance
   - Copy "Public IPv4 address"

## Part 2: Connect to EC2

### From Mac/Linux:
```bash
# Set correct permissions on key
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ec2-user@YOUR_PUBLIC_IP
# Or for Ubuntu: ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### From Windows (PowerShell):
```powershell
ssh -i your-key.pem ec2-user@YOUR_PUBLIC_IP
```

## Part 3: Install Git and Clone Project

```bash
# Update system
sudo yum update -y    # Amazon Linux
# OR
sudo apt update && sudo apt upgrade -y    # Ubuntu

# Install git
sudo yum install git -y    # Amazon Linux
# OR
sudo apt install git -y    # Ubuntu

# Clone your honeypot repo
git clone https://github.com/yourusername/honeypot-demo.git
cd honeypot-demo

# OR if you don't have it in a repo yet, create manually:
mkdir honeypot-demo
cd honeypot-demo
# Then upload files via scp (see below)
```

## Part 4: Upload Files (if not using git)

From your **local machine**:

```bash
# Upload entire directory
scp -i your-key.pem -r honeypot-demo/* ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/

# Or upload individual files
scp -i your-key.pem app.py ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/
scp -i your-key.pem Dockerfile ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/
scp -i your-key.pem docker-compose.yml ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/
scp -i your-key.pem requirements.txt ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/
scp -i your-key.pem analyze_logs.py ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/
scp -i your-key.pem deploy.sh ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/
```

## Part 5: Deploy Honeypot

Back on the **EC2 instance**:

```bash
# Navigate to directory
cd honeypot-demo

# Make deploy script executable
chmod +x deploy.sh

# Run deployment (installs Docker + starts honeypot)
./deploy.sh

# If it says "please log out and back in"
exit
ssh -i your-key.pem ec2-user@YOUR_PUBLIC_IP
cd honeypot-demo
./deploy.sh
```

## Part 6: Verify It's Working

```bash
# Check if container is running
docker ps

# Should see output like:
# CONTAINER ID   IMAGE                    ...   PORTS                NAMES
# abc123def456   honeypot-demo_honeypot   ...   0.0.0.0:80->80/tcp   honeypot-demo

# Test locally
curl http://localhost/

# Should see HTML response with "SecureStore Admin Portal"
```

**Test from your browser:**
- Open: `http://YOUR_PUBLIC_IP`
- You should see the fake login page!

## Part 7: Monitor Activity

### Watch logs live:
```bash
# Real-time logs
docker-compose logs -f

# Or just the access log
tail -f logs/access.log

# Pretty JSON output
tail -f logs/access.log | jq .
```

### Quick stats:
```bash
# Total requests
wc -l logs/access.log

# Unique IPs
cat logs/access.log | jq -r .ip | sort -u | wc -l

# Most common paths
cat logs/access.log | jq -r .path | sort | uniq -c | sort -rn | head
```

## Part 8: After Your Experiment

### Download Results (from local machine):
```bash
# Download logs
scp -i your-key.pem ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/logs/access.log ./

# Or download everything
scp -i your-key.pem -r ec2-user@YOUR_PUBLIC_IP:~/honeypot-demo/logs ./honeypot-logs
```

### Analyze Results (on EC2 or locally):
```bash
python3 analyze_logs.py
```

### Save Report:
```bash
python3 analyze_logs.py > honeypot-report.txt
cat honeypot-report.txt
```

## Part 9: CLEANUP (IMPORTANT!)

### Stop the honeypot:
```bash
docker-compose down
```

### Terminate EC2 Instance:

**Option A: AWS Console**
1. Go to EC2 Dashboard
2. Select your instance
3. Instance State → Terminate Instance
4. Confirm

**Option B: AWS CLI**
```bash
aws ec2 terminate-instances --instance-ids i-YOUR_INSTANCE_ID
```

**⚠️ Don't forget this step!** Running instances cost money.

## Expected Timeline

- **Minutes 0-5**: Quiet, maybe 1-2 random requests
- **Minutes 5-15**: First bots arrive (usually port scanners)
- **Minutes 15-30**: WordPress/PHPMyAdmin probes begin
- **Minutes 30-60**: Steady stream of attack attempts
- **After 60 min**: Hundreds of requests from dozens of IPs

## Troubleshooting

### Can't connect via SSH?
- Check Security Group allows your IP on port 22
- Verify you're using correct username (ec2-user or ubuntu)
- Ensure key file has correct permissions (400)

### Can't access on port 80?
- Check Security Group allows 0.0.0.0/0 on port 80
- Verify container is running: `docker ps`
- Check if something else uses port 80: `sudo netstat -tlnp | grep :80`

### Docker permission denied?
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in
exit
ssh -i your-key.pem ec2-user@YOUR_PUBLIC_IP
```

### No requests coming in?
- Wait longer (15-30 minutes)
- Verify security group allows HTTP from 0.0.0.0/0
- Test from browser: http://YOUR_PUBLIC_IP
- Check container logs: `docker-compose logs`

## Cost Estimate

**t2.micro (free tier):**
- First 750 hours/month: $0
- After free tier: ~$0.012/hour (~$0.01 for 1 hour)

**Data transfer:**
- Incoming: Free
- Outgoing: First 1 GB free (~negligible for this experiment)

**Total for 1-hour experiment: $0-0.01**

## Security Group Configuration Reference

```
Inbound Rules:
┌────────┬──────────┬──────────────┬─────────────┐
│ Type   │ Protocol │ Port Range   │ Source      │
├────────┼──────────┼──────────────┼─────────────┤
│ SSH    │ TCP      │ 22           │ My IP       │
│ HTTP   │ TCP      │ 80           │ 0.0.0.0/0   │
└────────┴──────────┴──────────────┴─────────────┘

Outbound Rules:
┌────────┬──────────┬──────────────┬─────────────┐
│ Type   │ Protocol │ Port Range   │ Destination │
├────────┼──────────┼──────────────┼─────────────┤
│ All    │ All      │ All          │ 0.0.0.0/0   │
└────────┴──────────┴──────────────┴─────────────┘
```

## Quick Command Reference

```bash
# Start honeypot
./deploy.sh

# Watch logs
docker-compose logs -f

# Quick stats
wc -l logs/access.log

# Analyze
python3 analyze_logs.py

# Stop
docker-compose down

# Download results (from local machine)
scp -i your-key.pem ec2-user@YOUR_IP:~/honeypot-demo/logs/access.log ./
```

Good luck with your experiment! 🎯
