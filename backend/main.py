from fastapi import FastAPI, BackgroundTasks
import ccxt
import asyncio

app = FastAPI()

# Sample exchanges
binance = ccxt.binance()
kraken = ccxt.kraken()

symbol = "BTC/USDT"
profit_threshold = 50  # USD

@app.get("/")
def read_root():
    return {"message": "Spread Hunter 2.0 - Arbitrage Engine Online"}

@app.get("/scan")
async def scan_arbitrage(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_arbitrage)
    return {"message": "Arbitrage scan started"}

async def run_arbitrage():
    while True:
        try:
            binance_ticker = binance.fetch_ticker(symbol)
            kraken_ticker = kraken.fetch_ticker(symbol)

            binance_ask = binance_ticker['ask']
            kraken_bid = kraken_ticker['bid']

            if kraken_bid - binance_ask > profit_threshold:
                print(f"Opportunity: Buy on Binance at {binance_ask}, sell on Kraken at {kraken_bid}")

            kraken_ask = kraken_ticker['ask']
            binance_bid = binance_ticker['bid']

            if binance_bid - kraken_ask > profit_threshold:
                print(f"Opportunity: Buy on Kraken at {kraken_ask}, sell on Binance at {binance_bid}")

        except Exception as e:
            print(f"Error during arbitrage scan: {e}")

        await asyncio.sleep(10)
