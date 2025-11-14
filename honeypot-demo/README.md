# 🍯 Internet Honeypot - Educational Bot Demonstration

A minimal web application designed to attract and log malicious bot activity for educational purposes. Deploy this for an hour and watch the bots find you!

## 🎯 What This Shows

This honeypot demonstrates:
- **Bot discovery**: How quickly bots find exposed services
- **Attack patterns**: What vulnerabilities bots look for (WordPress, PHPMyAdmin, config files)
- **Automated attacks**: SQL injection, credential stuffing, path traversal
- **Internet background noise**: The constant scanning happening 24/7

## 🏗️ What's Inside

- **Fake vulnerable app** with realistic-looking login forms
- **Common bot targets**: `/wp-admin`, `/phpmyadmin`, `/.env`, `/admin`, etc.
- **Detailed logging**: Every request logged with IP, headers, payloads
- **Realistic responses**: Keeps bots engaged with fake error messages
- **Analysis tools**: Parse logs and generate reports

## 🚀 Quick Start (EC2 Deployment)

### Prerequisites
- AWS account with EC2 access
- Basic familiarity with SSH and AWS console

### Step 1: Launch EC2 Instance

```bash
# Launch a simple t2.micro instance (free tier eligible)
# - AMI: Amazon Linux 2023 or Ubuntu 22.04
# - Instance Type: t2.micro
# - Security Group: Allow inbound on port 80 (HTTP) and 22 (SSH)
```

**Security Group Rules:**
```
Inbound:
- Port 22 (SSH) - Your IP only
- Port 80 (HTTP) - 0.0.0.0/0 (anywhere)
```

### Step 2: Connect and Install Docker

```bash
# SSH into your instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y  # Amazon Linux
# OR
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Docker
sudo yum install docker -y  # Amazon Linux
# OR
sudo apt install docker.io -y  # Ubuntu

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes
exit
```

### Step 3: Deploy Honeypot

```bash
# SSH back in
ssh -i your-key.pem ec2-user@your-instance-ip

# Clone or upload the honeypot files
# Option A: If you have this in a repo
git clone https://github.com/yourusername/honeypot-demo.git
cd honeypot-demo

# Option B: Or create files manually
mkdir honeypot-demo && cd honeypot-demo
# Then upload files via scp or copy-paste

# Build and run
docker-compose up -d

# Verify it's running
docker ps
curl localhost
```

### Step 4: Watch the Logs!

```bash
# Watch logs in real-time (Ctrl+C to stop)
docker-compose logs -f

# Or view the JSON access log
tail -f logs/access.log

# After some time, analyze the logs
python3 analyze_logs.py
```

## 📊 Analyzing Results

After running for 30-60 minutes:

```bash
# Generate analysis report
python3 analyze_logs.py

# View raw JSON logs
cat logs/access.log | jq .

# Count total requests
wc -l logs/access.log

# See unique IPs
cat logs/access.log | jq -r .ip | sort -u | wc -l

# Most common paths
cat logs/access.log | jq -r .path | sort | uniq -c | sort -rn | head -20
```

## 🎥 Creating Content From This

### Blog Post Ideas
1. "I exposed a server to the internet for 1 hour. Here's what happened."
2. "What are bots actually looking for? A honeypot experiment"
3. "Understanding web security through malicious bot traffic"

### Video Script Outline
1. **Intro** (1 min): Why internet security matters
2. **Setup** (2 min): Quick EC2 + Docker deployment walkthrough
3. **Watch Live** (3 min): Screen recording of logs scrolling, pointing out interesting requests
4. **Analysis** (3 min): Run the analysis script, discuss findings
5. **Takeaways** (1 min): What this teaches about internet security

### Key Visuals to Capture
- Terminal showing rapid log entries
- The analysis report output
- Top attacked paths (WordPress, PHPMyAdmin, etc.)
- Geographic map of source IPs (optional: use MaxMind GeoIP)
- Timeline showing when bots discovered the server

## 🧪 Testing Locally First

Before deploying to EC2, test locally:

```bash
# Build and run locally
docker-compose up

# In another terminal, test it
curl http://localhost/
curl http://localhost/wp-admin
curl http://localhost/.env
curl -X POST http://localhost/admin/login -d "username=admin&password=test"

# Analyze local logs
python3 analyze_logs.py
```

## 🛡️ Safety Notes

**IMPORTANT:**
- This is for **educational purposes only**
- Run for short periods (1 hour max initially)
- **DO NOT** put real credentials, API keys, or sensitive data in the app
- Monitor your AWS costs (t2.micro should be pennies)
- **ALWAYS** terminate the EC2 instance when done
- The fake .env file is intentionally fake - never expose real config!

## 📈 What to Expect

Based on typical results:
- **First 5 minutes**: Usually quiet, maybe a few random scans
- **15-30 minutes**: Shodan, Censys, and other scanners find you
- **30-60 minutes**: Steady stream of WordPress probes, SQL injection attempts
- **1+ hours**: Continued attacks from various bot networks

Typical stats per hour:
- 50-500 requests (depends on luck)
- 10-50 unique IPs
- 80%+ WordPress/PHPMyAdmin related
- Multiple SQL injection attempts
- Several credential stuffing attempts

## 📁 Project Structure

```
honeypot-demo/
├── app.py              # Main Flask application
├── Dockerfile          # Container definition
├── docker-compose.yml  # Easy deployment
├── requirements.txt    # Python dependencies
├── analyze_logs.py     # Log analysis script
├── logs/              # Volume mount for logs
│   ├── access.log     # Detailed JSON logs
│   └── summary.json   # Analysis summary
└── README.md          # This file
```

## 🔧 Customization Ideas

1. **Add more fake endpoints**: Modify `app.py` to add more realistic routes
2. **Fake database responses**: Return SQL-looking data to keep bots engaged
3. **Rate limiting**: Track repeat offenders
4. **GeoIP lookup**: Show where attacks come from (requires MaxMind DB)
5. **Real-time dashboard**: Build a simple web UI showing live stats
6. **Slack/Discord notifications**: Alert when interesting attacks happen

## 🧹 Cleanup

```bash
# Stop and remove containers
docker-compose down

# On EC2: Terminate the instance
# Go to AWS Console -> EC2 -> Instances -> Select instance -> Instance State -> Terminate
```

## 📚 Learning Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Shodan](https://shodan.io) - The search engine for internet-connected devices
- [Project Honeypot](https://www.projecthoneypot.org/)
- [SANS Internet Storm Center](https://isc.sans.edu/)

## 🤝 Contributing

This is an educational project! Ideas for improvement:
- More realistic fake responses
- Additional common bot targets
- Better visualization of results
- Detection of specific bot frameworks

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. The author is not responsible for any misuse or damage caused by this software. Always ensure you have permission to run security research tools on any network.

---

**Have fun learning about internet security! 🎓**
