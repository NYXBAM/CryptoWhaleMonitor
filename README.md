# Crypto Whale Monitor

🐋 **Crypto Whale Monitor** is a real-time monitoring tool for tracking large cryptocurrency transactions ("whales") across multiple blockchains including BTC, ETH, and Polygon (MATIC). Alerts are sent directly to a Telegram channel for instant notifications.

---

## Features

- Monitor large transactions on **Bitcoin, Ethereum, and Polygon**.
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
- **SQLite** for local storage
- **dotenv** for configuration management
- Optional APIs: WalletExplorer for tagging addresses (e.g., exchanges)

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
```

Then run main.py file 
```bash
python main.py
```
