from fastapi import FastAPI, BackgroundTasks, Query
import ccxt
import asyncio
from datetime import datetime
import json
import os

app = FastAPI()

# Simulated user database (in-memory)
users = {
    "user1": {
        "premium": True,
        "api_keys": {
            "binance": "user1_binance_key",
            "kraken": "user1_kraken_key"
        }
    }
}

# Sample exchanges (public endpoints only for now)
binance = ccxt.binance()
kraken = ccxt.kraken()

symbol = "BTC/USDT"
profit_threshold = 50  # USD
log_file = "trade_log.json"

@app.get("/")
def read_root():
    return {"message": "Spread Hunter 2.0 - Enhanced Engine Online"}

@app.get("/scan")
async def scan_arbitrage(user: str = Query(...), background_tasks: BackgroundTasks = None):
    if user not in users:
        return {"error": "User not found"}
    background_tasks.add_task(run_arbitrage, user)
    return {"message": f"Arbitrage scan started for {user}"}

async def run_arbitrage(user: str):
    user_data = users[user]
    while True:
        try:
            binance_ticker = binance.fetch_ticker(symbol)
            kraken_ticker = kraken.fetch_ticker(symbol)

            binance_ask = binance_ticker['ask']
            binance_bid = binance_ticker['bid']
            kraken_ask = kraken_ticker['ask']
            kraken_bid = kraken_ticker['bid']

            timestamp = datetime.utcnow().isoformat()

            if kraken_bid - binance_ask > profit_threshold:
                log_trade(user, timestamp, "binance", "kraken", binance_ask, kraken_bid)
                if user_data["premium"]:
                    print(f"[AUTO TRADE] Buy on Binance at {binance_ask}, sell on Kraken at {kraken_bid}")

            elif binance_bid - kraken_ask > profit_threshold:
                log_trade(user, timestamp, "kraken", "binance", kraken_ask, binance_bid)
                if user_data["premium"]:
                    print(f"[AUTO TRADE] Buy on Kraken at {kraken_ask}, sell on Binance at {binance_bid}")

        except Exception as e:
            print(f"Error: {e}")

        await asyncio.sleep(10)

def log_trade(user, timestamp, buy_exchange, sell_exchange, buy_price, sell_price):
    trade = {
        "user": user,
        "timestamp": timestamp,
        "buy_from": buy_exchange,
        "sell_to": sell_exchange,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "profit": round(sell_price - buy_price, 2),
        "platform_fee": round((sell_price - buy_price) * 0.15, 2)
    }

    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(trade)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)
