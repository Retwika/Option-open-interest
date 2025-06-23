"""
Data Fetchers Module
===================

This module contains all data fetching functions for both US and Indian markets.
Separated from the Streamlit app for better code organization and reusability.

Author: Data Analysis Project
Date: 2024
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from nsepython import nse_optionchain_scrapper

# --- US Market Functions ---

def get_stock_info(symbol):
    """Get basic information about a US stock."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'current_price': info.get('currentPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown')
        }
    except Exception as e:
        print(f"Error getting info for {symbol}: {e}")
        return None

def fetch_options_chain(symbol):
    """Fetch options chain data for a given US symbol for the nearest expiration."""
    try:
        ticker = yf.Ticker(symbol)
        expiration_dates = ticker.options
        if not expiration_dates:
            print(f"No options available for {symbol}")
            return None
        
        # Use the nearest expiration date
        expiration_date = expiration_dates[0]
        print(f"Using nearest expiration date: {expiration_date}")
        
        options = ticker.option_chain(expiration_date)
        return {
            'symbol': symbol,
            'expiration_date': expiration_date,
            'calls': options.calls,
            'puts': options.puts,
            'timestamp': datetime.now()
        }
    except Exception as e:
        print(f"Error fetching options for {symbol}: {e}")
        return None

def process_options_data(options_data):
    """Process the raw US options data into a structured format."""
    if not options_data:
        return None
    
    records = []
    symbol = options_data['symbol']
    expiration_date = options_data['expiration_date']
    
    # Process calls and puts
    for option_type in ['calls', 'puts']:
        if option_type in options_data and options_data[option_type] is not None:
            df_slice = options_data[option_type]
            for _, row in df_slice.iterrows():
                records.append({
                    'Symbol': symbol,
                    'Type': 'Call' if option_type == 'calls' else 'Put',
                    'Strike': row.get('strike', 0),
                    'Last_Price': row.get('lastPrice', 0),
                    'Bid': row.get('bid', 0),
                    'Ask': row.get('ask', 0),
                    'Volume': row.get('volume', 0),
                    'Open_Interest': row.get('openInterest', 0),
                    'Implied_Volatility': row.get('impliedVolatility', 0),
                    'Expiration_Date': expiration_date
                })
    
    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values(by=['Type', 'Strike'], inplace=True)
    return df

# --- Indian Market Functions ---

def fetch_nifty_options():
    """Fetch NIFTY options data using nsepython package."""
    try:
        print("Fetching NIFTY options data...")
        data = nse_optionchain_scrapper('NIFTY')
        print("NIFTY data fetched successfully!")
        return data
    except Exception as e:
        print(f"Error fetching NIFTY data: {str(e)}")
        return None

def process_nifty_options_data(data):
    """Process the raw NIFTY options data into a structured format."""
    if not data:
        return None
    
    records = []
    
    try:
        if 'records' in data and 'data' in data['records']:
            for item in data['records']['data']:
                strike_price = item.get('strikePrice')
                ce_data = item.get('CE')
                pe_data = item.get('PE')
                
                # Process Call (CE) options
                if ce_data:
                    records.append({
                        'Symbol': 'NIFTY',
                        'Type': 'CE',
                        'Strike': strike_price,
                        'Open_Interest': ce_data.get('openInterest'),
                        'Change_in_OI': ce_data.get('changeinOpenInterest'),
                        'Volume': ce_data.get('totalTradedVolume'),
                        'IV': ce_data.get('impliedVolatility'),
                        'Last_Price': ce_data.get('lastPrice'),
                        'Underlying': ce_data.get('underlyingValue'),
                        'Bid': ce_data.get('bidprice'),
                        'Ask': ce_data.get('askPrice'),
                        'Timestamp': datetime.now()
                    })
                
                # Process Put (PE) options
                if pe_data:
                    records.append({
                        'Symbol': 'NIFTY',
                        'Type': 'PE',
                        'Strike': strike_price,
                        'Open_Interest': pe_data.get('openInterest'),
                        'Change_in_OI': pe_data.get('changeinOpenInterest'),
                        'Volume': pe_data.get('totalTradedVolume'),
                        'IV': pe_data.get('impliedVolatility'),
                        'Last_Price': pe_data.get('lastPrice'),
                        'Underlying': pe_data.get('underlyingValue'),
                        'Bid': pe_data.get('bidprice'),
                        'Ask': pe_data.get('askPrice'),
                        'Timestamp': datetime.now()
                    })
        
        df = pd.DataFrame(records)
        if not df.empty:
            df.sort_values(by=['Type', 'Strike'], inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Error processing NIFTY data: {str(e)}")
        return None 