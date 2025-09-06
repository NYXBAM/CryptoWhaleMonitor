# Crypto Whale Monitor
[![GitHub stars](https://img.shields.io/github/stars/NYXBAM/CryptoWhaleMonitor?style=social)](https://github.com/NYXBAM/CryptoWhaleMonitor/stargazers)
Enjoying this project? Give it a ⭐ and join the community of supporters!


🐋 **Crypto Whale Monitor** is a real-time monitoring tool for tracking large cryptocurrency transactions ("whales") across multiple blockchains including BTC, ETH, and other. Alerts are sent directly to a Telegram channel for instant notifications.

### TG CHANNEL (Show how it`s work):  https://t.me/CryptoTransac

<p align="center">
  <img width="422" height="375" alt="image" src="https://github.com/user-attachments/assets/19b9cfa0-9209-41f0-8fb6-318fa87c1147" />
  
  <img width="422" height="375" alt="image" src="https://github.com/user-attachments/assets/7a81f942-a9a3-47f4-a465-803c1a47ed51" />
</p>


---

## Features

- Monitor large transactions on **Bitcoin, Ethereum, and other**.
- Identify **whale transactions** based on customizable thresholds.
- **Telegram alerts** with formatted HTML messages.
- Track **from/to addresses**, transaction amount, and link to blockchain explorers.
- Save transactions to **SQLite database** for historical analysis.
- Easily extensible for adding more blockchains or custom thresholds.

---

## Tech Stack

- **Python 3.13+**
- **Requests** for blockchain RPC calls and Telegram API
- **SQLAlchemy** for database ORM
- **dotenv** for configuration management
- **APIs:** Moralis for tagging addresses (e.g., exchanges)

---

## Setup

1. Clone the repository:

```bash
git clone https://github.com/NYXBAM/CryptoWhaleMonitor.git
cd CryptoWhaleMonitor
```

```bash
pip install -r requirements.txt
```
Create a .env file in the project root:
```
TG_BOT_TOKEN=your_telegram_bot_token
TG_CHAT_ID=-1001234567890   # your channel ID
# moralis api 
MORALIS_API_KEY=ealGJ # your moralis api key, it`s for free -> here https://admin.moralis.com/login
```

Then run main.py file 
```bash
python main.py
```
