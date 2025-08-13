import os
import time
import dotenv
import okx.Account as account
import okx.MarketData as market
import okx.PublicData as public
import okx.TradingData as trading_data
import okx.Status as status
import datetime
import json

MAIN_PAIRS = {"BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT", "LINK-USDT", "BNB-USDT"}

# Load environment variables from .env file
dotenv.load_dotenv()
key = os.getenv("API_KEY")
passphrase = os.getenv("PASSPHRASE")
secret = os.getenv("SECRET_KEY")
flag = "0"
debug = os.getenv("DEBUG_MODE", "false").lower() in ["1", "true"]

def get_ticker_price_main():
    prices = {}
    for pair in MAIN_PAIRS:
        try:
            ticker = market.MarketAPI(flag=flag).get_index_ticker(instId=pair)
            if ticker and 'data' in ticker and len(ticker['data']) > 0:
                info = ticker['data'][0]
                prices[pair] = {
                    'instId': info.get('instId'),
                    'idxPx': float(info.get('idxPx', 0)),
                    'high24h': float(info.get('high24h', 0)),
                    'low24h': float(info.get('low24h', 0))
                }
            else:
                print(f"Invalid response for {pair}")
        except Exception as e:
            print(f"Error fetching ticker for {pair}: {e}")
    return json.dumps(prices)