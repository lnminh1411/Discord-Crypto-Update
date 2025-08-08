import os
import datetime
import dotenv
import okx.Trade as trade
import okx.Account as account
import okx.MarketData as market
import okx.PublicData as public
import okx.TradingData as trading_data
import okx.Status as status
import okx.Funding as funding
import okx.Convert as convert
import okx.websocket as ws
from okx.websocket import WebSocketPublic
import threading


TOP_SPOT_PAIRS = {"BTC-USDT", "ETH-USDT", "SOL-USDT"}
TOP_SWAP_PAIRS = {"BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"}

# Load environment variables from .env file
dotenv.load_dotenv()
key = os.getenv("API_KEY")
passphrase = os.getenv("PASSPHRASE")
secret = os.getenv("SECRET_KEY")
demo = os.getenv("DEMO_MODE", "false").lower() in ["1", "true"]
debug = os.getenv("DEBUG_MODE", "false").lower() in ["1", "true"]
pair = os.getenv("TRADING_PAIR", "BTC-USDT-SWAP")

# Initialize API connection
accountAPI = account(key, secret, passphrase, True, "1" if demo else "0")

# Reload environment variables
def reload_env():
    dotenv.load_dotenv()
    return {
        "key": os.getenv("API_KEY"),
        "passphrase": os.getenv("PASSPHRASE"),
        "secret": os.getenv("SECRET_KEY"),
        "demo": os.getenv("DEMO_MODE", "false").lower() in ["1", "true"],
        "debug": os.getenv("DEBUG_MODE", "false").lower() in ["1", "true"],
        "pair": os.getenv("TRADING_PAIR", "BTC-USDT-SWAP"),
    }
    
def get_bot_data():
    try:
        # Fetch account information
        account_info = accountAPI.get_account()
        if debug:
            print("Account Info:", account_info)

        # Fetch balance
        balance = accountAPI.get_balance()
        if debug:
            print("Balance:", balance)
            
        # Return the fetched data
        return {
            "account_info": account_info,
            "balance": balance,
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
def get_market_data():
    try:
        # Fetch market data
        market_data = market.get_ticker(pair)
        if debug:
            print("Market Data:", market_data)
        order_book = market.get_order_book(pair)
        if debug:
            print("Order Book:", order_book)    
        trades = market.get_trades(pair)
        if debug:   
            print("Recent Trades:", trades) 
        # Return the market data
        return {   
            "ticker": market_data,
            "order_book": order_book,
            "trades": trades,
        }
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None
    
def get_trading_pair():
    try:
        # Fetch trading pair information
        trading_pair_info = public.get_instruments(pair)
        if debug:
            print("Trading Pair Info:", trading_pair_info)
        return trading_pair_info
    except Exception as e:
        print(f"Error fetching trading pair info: {e}")
        return None
    
def convert_currency(from_currency, to_currency, amount):
    try:
        # Convert currency
        conversion = convert.convert(from_currency, to_currency, amount)
        if debug:
            print("Conversion Result:", conversion)
        return conversion
    except Exception as e:
        print(f"Error converting currency: {e}")
        return None
    
def get_coin_data():
    try:
        # Fetch coin data
        coin_data = public.get_coins()
        if debug:
            print("Coin Data:", coin_data)
        return coin_data
    except Exception as e:
        print(f"Error fetching coin data: {e}")
        return None
    
def get_candles(pair, instType):
    now = datetime.datetime.now()
    candles = {}

    def fetch(bar, days):
        after = int((now - datetime.timedelta(days=days)).timestamp() * 1000)
        return market.get_candlesticks(pair, bar, after)

    if pair in TOP_SPOT_PAIRS or pair in TOP_SWAP_PAIRS:
        candles["1m"] = fetch("1m", 4)
        candles["5m"] = fetch("5m", 7)
        candles["30m"] = fetch("30m", 14)
        candles["1h"] = fetch("1H", 28)
        candles["1d"] = fetch("1D", 60)
    else:
        candles["1m"] = fetch("1m", 4)
        candles["5m"] = fetch("5m", 7)

    return candles

def live_candles(pair, bar="1m"):
    ws = WebSocketPublic()
    ws.start()

    def on_message(msg):
        print(f"Live {bar} candle for {pair}: {msg}")

    channel = "candle" + bar
    instType = "SPOT" if pair in TOP_SPOT_PAIRS else "SWAP"
    ws.subscribe(instType, channel, pair, on_message)

    # Keep thread alive
    threading.Event().wait()

