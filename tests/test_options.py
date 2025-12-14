"""Test options endpoint"""
from dotenv import load_dotenv
import os
from datetime import date, timedelta

load_dotenv()

from alpaca_client import AlpacaClient, MarketDataAPI

client = AlpacaClient(os.environ['ALPACA_API_KEY'], os.environ['ALPACA_API_SECRET'], paper=True)
market_data = MarketDataAPI(client)

today = date.today()
next_month = today + timedelta(days=30)

print(f"Searching AAPL options: {today} to {next_month}")

try:
    contracts = market_data.get_options_contracts(
        underlying_symbols=['AAPL'],
        expiration_date_gte=today.isoformat(),
        expiration_date_lte=next_month.isoformat(),
        limit=5
    )
    
    options = contracts.get('option_contracts', [])
    print(f"Found {len(options)} contracts")
    
    for c in options[:5]:
        print(f"  {c['symbol']}: Strike ${c['strike_price']} Exp {c['expiration_date']}")
        
except Exception as e:
    print(f"Error: {e}")

client.close()
