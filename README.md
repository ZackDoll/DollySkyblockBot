# 🎮 Hypixel Skyblock Patch Notes Bot

A Discord bot that automatically monitors the Hypixel Skyblock forum for new patch notes and delivers AI-powered summaries directly to your Discord DMs.

---

## ✨ Features

- **Automatic Monitoring** - Scans the Hypixel forum every hour for new patch notes
- **AI-Powered Summaries** - Uses GPT-4 to create concise, categorized summaries of patch changes
- **Smart Notifications** - Sends instant Discord DMs when new patches are released
- **Change Tracking** - Highlights all numerical changes and important updates
- **24/7 Uptime** - Runs continuously on AWS cloud infrastructure

---

## 🚀 How It Works

1. **Monitors** the [Hypixel Skyblock Patch Notes forum](https://hypixel.net/forums/skyblock-patch-notes.158/)
2. **Detects** when a new thread is posted
3. **Extracts** the full patch notes content
4. **Summarizes** the changes using ChatGPT with intelligent categorization
5. **Delivers** the summary via Discord DM with a link to the original post

  - This can be changed to a different link if you want to use it for a different purpose, just change the URL variable to something that you want

---

## 🛠️ Tech Stack

- **Python 3.12** - Core programming language
- **Discord.py** - Discord bot framework
- **OpenAI GPT-4** - AI summarization
- **BeautifulSoup4** - Web scraping
- **ScraperAntAPI** - Cloudflare bypass
- **AWS EC2** - Cloud hosting

---

## 📋 Prerequisites

- Python 3.12+
- Discord Bot Token
- OpenAI API Key
- ScraperAnt API Key (free tier available)
- AWS EC2 instance (optional, for 24/7 hosting)

---

## ⚙️ IF YOU WANT TO SWAP IT TO A DIFF FORUM
- URL variable (near the top) controls which link it checks over
