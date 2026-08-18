<div align="center">

# 📦 GitHub Repo Size Checker Bot

### A fast, simple Telegram bot to instantly check the size of any GitHub repository.

*Stop guessing if a repository is too big to clone on your limited data plan. Just send a link, and get the exact size in KB, MB, and GB.*

![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram&logoColor=white)
![Deployment](https://img.shields.io/badge/Deployed_on-Fly.io-5C3EE8)

<br/>

<img src="RepoSizeCheckerBot.png" alt="Repo Size Checker Bot" width="400"/>

</div>

---

## ✨ Features

- **Instant Results**: Uses the GitHub REST API to fetch exact repository sizes instantly.
- **Smart URL Parsing**: Handles messy links gracefully. Whether you send `github.com/owner/repo`, or a deep link to an issue like `github.com/owner/repo/issues/1`, the bot knows exactly what to do.
- **Human-Readable Output**: Automatically converts GitHub's native KB output into Megabytes and Gigabytes for easy reading.
- **Bulletproof Error Handling**: Helpful error messages for private repos, broken links, typos, and API rate limits.
- **Docker-Ready**: Comes with a `Dockerfile` for instant, 24/7 cloud deployment.

---

## 🚀 Quick Start (Running Locally)

If you just want to run the bot on your own computer, follow these steps.

### Prerequisites
- Python 3.10+
- A Telegram Bot Token (Get one from [@BotFather](https://t.me/botfather) on Telegram)

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/github-size-bot.git
cd github-size-bot

# Create and activate a virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# For Mac/Linux use: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy the `.env.example` file (or just create a `.env` file) in the root directory and add your bot token:
```env
TELEGRAM_BOT_TOKEN=123456789:YOUR_SECRET_TOKEN_HERE
```

### 3. Run the Bot
```bash
python bot.py
```
*The bot is now polling for messages! Open Telegram and send it a GitHub link to test it out.*

---

## ☁️ Deploying for Free 24/7 (Fly.io)

This project is fully Dockerized and optimized for deployment on [Fly.io's](https://fly.io/) free tier. 

### 1. Install Fly.io CLI (`flyctl`)
- **Windows (PowerShell):** `iwr https://fly.io/install.ps1 -useb | iex`
- **Mac/Linux:** `curl -L https://fly.io/install.sh | sh`

### 2. Authenticate
```bash
fly auth login
```
*(This will open your browser to log in or sign up).*

### 3. Initialize the App
```bash
fly launch --name repo-size-bot
```
*(When asked if you want to tweak settings, you can say **No** to accept the defaults. This generates a `fly.toml` file).*

### 4. Set your Secret Token
Because we keep the `.env` file secure and out of the Docker container, we must provide the Telegram token directly to Fly.io as a secret:
```bash
fly secrets set TELEGRAM_BOT_TOKEN="your_token_here"
```

### 5. Ship it! 🚀
```bash
fly deploy
```
Once this command finishes, your bot is running live on Fly.io 24/7!

> [!TIP]
> **Monitoring your Bot**
> If you ever want to check if it's running okay or view any error logs, you can just open your terminal and run `fly logs`.

---

## 🛠️ Built With
- [python-telegram-bot](https://python-telegram-bot.org/) - The wrapper for the Telegram Bot API.
- [Requests](https://requests.readthedocs.io/en/latest/) - For lightning-fast HTTP calls to GitHub.
- [GitHub REST API](https://docs.github.com/en/rest) - To fetch the repository metadata.
