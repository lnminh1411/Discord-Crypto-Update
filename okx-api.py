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

def convert_time(ts):
    try:
        dt = datetime.datetime.fromtimestamp(int(ts) / 1000, tz=datetime.timezone.utc)
        return dt.strftime("%H:%M:%S | %d/%m/%Y")
    except:
        return "N/A"

def get_status():
    SERVICE_MAP = {
        "0": "WebSocket",
        "5": "Trading service",
        "6": "Block trading",
        "7": "Trading bot",
        "8": "Trading service (in batches of accounts)",
        "9": "Trading service (in batches of products)",
        "10": "Spread trading",
        "11": "Copy trading",
        "99": "Others"
    }
    
    MAINT_MAP = {
        "1": "Scheduled maintenance",
        "2": "Unscheduled maintenance",
        "3": "System disruption"
    }
    
    status_api = status.StatusAPI(
        domain="https://www.okx.com",
        flag="0"
    )
    
    # Get scheduled events
    response = status_api.status(state="scheduled")
    
    # Validate API response
    if response.get('code') != '0':
        print(f"API Error: {response.get('msg', 'Unknown error')}")
        return json.dumps([])
    
    # Process events
    events = []
    for event in response.get('data', []):
        if event.get('env') != '1':
            continue
 
        processed = {
            "title": event.get("title", ""),
            "begin": convert_time(event.get("begin", "")),
            "end": convert_time(event.get("end", "")),
            "serviceType": SERVICE_MAP.get(event.get("serviceType", ""), "Unknown"),
            "href": event.get("href", ""),
            "mainType": MAINT_MAP.get(event.get("mainType", ""), "Unknown")
        }
        events.append(processed)
    
    return json.dumps(events)

