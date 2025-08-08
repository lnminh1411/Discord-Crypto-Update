import os
import datetime
import dotenv
import okx.Account as account
import okx.MarketData as market
import okx.PublicData as public
import okx.TradingData as trading_data
import okx.Status as status


PAIRS = {"BTC-USDT", "ETH-USDT", "SOL-USDT"}

# Load environment variables from .env file
dotenv.load_dotenv()
key = os.getenv("API_KEY")
passphrase = os.getenv("PASSPHRASE")
secret = os.getenv("SECRET_KEY")
demo = os.getenv("DEMO_MODE", "false").lower() in ["1", "true"]
debug = os.getenv("DEBUG_MODE", "false").lower() in ["1", "true"]
pair = os.getenv("TRADING_PAIR", "BTC-USDT-SWAP")

# Initialize API connection
accountAPI = account(key, secret, passphrase, True, 0)

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