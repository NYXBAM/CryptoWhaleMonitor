# Crypto Whale Monitor

🐋 **Crypto Whale Monitor** is a real-time monitoring tool for tracking large cryptocurrency transactions ("whales") across multiple blockchains including BTC, ETH, and other. Alerts are sent directly to a Telegram channel for instant notifications.

### TG CHANNEL:  https://t.me/CryptoTransac

<img width="422" height="375" alt="image" src="https://github.com/user-attachments/assets/19b9cfa0-9209-41f0-8fb6-318fa87c1147" />
<img width="318" height="479" alt="image" src="https://github.com/user-attachments/assets/1f9963ca-74e6-48c3-b7ee-810742cda7d9" />




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
