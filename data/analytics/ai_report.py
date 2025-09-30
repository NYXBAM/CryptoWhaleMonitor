import logging
import time
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict

import requests
import markdown
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from data.models import WhaleTransaction
from utils.get_price import CryptoPriceClient
from utils.send_telegram_channel import send_telegram_report
from config import *  

load_dotenv()
Base = declarative_base()
logger = logging.getLogger("AiReport")

class WhaleTransactionFetcher:
    DATABASE_URL = DATABASE_URL

    def __init__(self):
        self.engine = create_engine(self.DATABASE_URL, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def get_recent_transactions(self, hours: int = 1) -> List[Dict]:
          ''' fetching transactions from DB, exclude $TON transactions, because, there are not classificated'''
          with self.Session() as db:
            time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
            transactions = (
                db.query(WhaleTransaction)
                .filter(
                    WhaleTransaction.timestamp >= time_threshold,
                    WhaleTransaction.blockchain != "TON"
                )
                .all()
            )
            return [
                {
                    "blockchain": tx.blockchain,
                    "txid": tx.txid,
                    "from_address": tx.from_address,
                    "to_address": tx.to_address,
                    "amount": tx.amount,
                    "price": tx.price,
                    "classification": tx.classification,
                    "timestamp": tx.timestamp.isoformat(),
                }
                for tx in transactions
            ]

class GenerateAiReportAnalytics(WhaleTransactionFetcher):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            api_key=os.getenv("API_INTELLIGENCE"),
            base_url="https://api.intelligence.io.solutions/api/v1/"
        )

    def build_prompt(self, transactions: List[Dict], language=REPORT_LANGUAGE) -> str:
          if language == "EN":
                return f"""
Here is the list of transactions from the last few hours:
{transactions}
Current rates:
- BTC: ${CryptoPriceClient.get_price("BTC")}
- ETH: ${CryptoPriceClient.get_price("ETH")}
- XRP: ${CryptoPriceClient.get_price("XRP")}
- Make a short trading overview:
- total volume for each blockchain and its ratio to the current rate
- which addresses/exchanges are the most active, whether there are any "whales" (large players)
- recurring large transfers as possible signals of accumulation/distribution
- possible impact of these transactions on liquidity and price in the short term
- final conclusion: neutral / bullish / bearish signal              
"""
          
          if language == "RU":
                return f"""
Вот список транзакций за последние несколько часов:
{transactions}

Актуальный курс:
- BTC: ${CryptoPriceClient.get_price("BTC")}
- ETH: ${CryptoPriceClient.get_price("ETH")}
- XRP: ${CryptoPriceClient.get_price("XRP")}

Сделай краткий торговый обзор:
- общий объем по каждому блокчейну и соотношение к текущему курсу
- какие адреса/биржи наиболее активны, видны ли "киты" (крупные игроки)
- повторяющиеся крупные переводы как возможные сигналы накопления/разгрузки
- возможное влияние этих транзакций на ликвидность и цену в краткосрочной перспективе
- финальный вывод: нейтральный / бычий / медвежий сигнал
"""
          
        

    def generate_report(self, transactions: List[Dict]) -> str:
        prompt = self.build_prompt(transactions)
        try:
          response = self.client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[
                  {"role": "system", "content": "You are a blockchain transaction analyst and crypto trader."},
                  {"role": "user", "content": prompt}
              ],
              temperature=0.1
          )
          return response.choices[0].message.content
        
        except Exception as e:
          print(e)
            
        
    
    @staticmethod
    def convert_to_html(markdown_text: str) -> str:
        return markdown.markdown(markdown_text, extensions=["extra", "tables", "fenced_code"])

    @staticmethod
    def save_to_html(html_content: str, filename: str = "report.html"):
        html_doc = f"""
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="utf-8">
  <title>Report</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 800px;
      margin: 2rem auto;
      padding: 1rem;
      line-height: 1.6;
      color: #222;
    }}
    h1, h2, h3, h4 {{
      margin-top: 1.5rem;
      margin-bottom: 0.5rem;
    }}
    pre {{
      background: #f4f4f4;
      padding: 10px;
      border-radius: 6px;
      overflow-x: auto;
    }}
    code {{
      font-family: monospace;
      background: #f4f4f4;
      padding: 2px 4px;
      border-radius: 4px;
    }}
    blockquote {{
      border-left: 4px solid #ccc;
      padding-left: 1rem;
      color: #555;
      margin-left: 0;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin: 1rem 0;
    }}
    th, td {{
      border: 1px solid #ccc;
      padding: 8px;
      text-align: left;
    }}
    th {{
      background: #f9f9f9;
    }}
    ul, ol {{
      margin: 0.5rem 0 0.5rem 1.5rem;
    }}
  </style>
</head>
<body>
{html_content}
</body>
</html>
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_doc)

def generate_and_send():
        generator = GenerateAiReportAnalytics()
        transactions = generator.get_recent_transactions(hours=2)  
        markdown_report = generator.generate_report(transactions)
        html_report = generator.convert_to_html(markdown_report)
        generator.save_to_html(html_report, "AiAnalytics.html.html")
        send_telegram_report("AiAnalytics.html.html")