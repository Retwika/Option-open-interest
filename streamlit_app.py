"""
Global Options Dashboard with Streamlit
======================================

This Streamlit app provides an interactive dashboard for both US and Indian market options data.
Users can view options chain data, including key metrics and visualizations for Open Interest and trading Volume.


"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import functions from separate modules
from data_fetchers import (
    get_stock_info, 
    fetch_options_chain, 
    process_options_data,
    fetch_nifty_options, 
    process_nifty_options_data
)
from plotting_utils import generate_us_plots, generate_nifty_plots

st.set_page_config(layout="wide")

# --- Streamlit App ---

st.title("📈 Global Options Dashboard")

# Create tabs for different markets
tab1, tab2 = st.tabs(["🇺🇸 US Market Options", "🇮🇳 Indian Market Options"])

# US Market Tab
with tab1:
    st.header("US Market Options Analysis")
    
    # Sidebar for user input
    st.sidebar.header("Select US Stock")
    symbols = [
        'AAPL', 'SPY', 'QQQ', 'TSLA', 'NVDA', 
        'AMD', 'MSFT', 'GOOGL', 'AMZN', 'META'
    ]
    selected_symbol = st.sidebar.selectbox("Choose a stock symbol:", symbols, key="us_symbol")

    if st.sidebar.button("Fetch US Options Data", key="us_fetch"):
        
        with st.spinner(f"Fetching data for {selected_symbol}..."):
            
            # Get and display stock info
            stock_info = get_stock_info(selected_symbol)
            if stock_info:
                st.subheader(f"{stock_info['name']} ({stock_info['symbol']})")
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Price", f"${stock_info['current_price']:.2f}")
                col2.metric("Market Cap", f"${stock_info['market_cap'] / 1e12:.2f}T")
                col3.metric("Sector", stock_info['sector'])
            
            # Fetch and process options data
            options_data = fetch_options_chain(selected_symbol)
            
            if options_data:
                df = process_options_data(options_data)
                
                if df is not None and not df.empty:
                    st.subheader("Options Analysis")
                    
                    # Generate and display plots
                    fig_oi, fig_volume = generate_us_plots(df, selected_symbol)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if fig_oi:
                            st.pyplot(fig_oi)
                    with col2:
                        if fig_volume:
                            st.pyplot(fig_volume)
                            
                    st.subheader("Options Chain Data")
                    st.dataframe(df)
                    
                else:
                    st.warning("Could not process options data.")
    else:
        st.info("Select a US stock symbol from the sidebar and click 'Fetch US Options Data' to begin.")

# Indian Market Tab
with tab2:
    st.header("Indian Market Options Analysis")
    st.subheader("NIFTY Options Chain")
    
    if st.button("Fetch NIFTY Options Data", key="nifty_fetch"):
        
        with st.spinner("Fetching NIFTY options data..."):
            
            # Fetch NIFTY data
            nifty_raw_data = fetch_nifty_options()
            
            if nifty_raw_data:
                # Process the data
                df_nifty = process_nifty_options_data(nifty_raw_data)
                
                if df_nifty is not None and not df_nifty.empty:
                    # Display summary metrics
                    st.subheader("NIFTY Options Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Contracts", len(df_nifty))
                    with col2:
                        ce_count = len(df_nifty[df_nifty['Type'] == 'CE'])
                        st.metric("Call Options (CE)", ce_count)
                    with col3:
                        pe_count = len(df_nifty[df_nifty['Type'] == 'PE'])
                        st.metric("Put Options (PE)", pe_count)
                    with col4:
                        if 'Underlying' in df_nifty.columns and not df_nifty['Underlying'].isna().all():
                            underlying_value = df_nifty['Underlying'].iloc[0]
                            st.metric("NIFTY Value", f"₹{underlying_value:,.2f}")
                        else:
                            st.metric("NIFTY Value", "N/A")
                    
                    # Generate and display plots
                    st.subheader("NIFTY Options Analysis")
                    fig_oi, fig_volume, fig_pc_ratio = generate_nifty_plots(df_nifty)
                    
                    # Display plots in columns
                    col1, col2 = st.columns(2)
                    with col1:
                        if fig_oi:
                            st.pyplot(fig_oi)
                    with col2:
                        if fig_pc_ratio:
                            st.pyplot(fig_pc_ratio)
                    
                    if fig_volume:
                        st.pyplot(fig_volume)
                    
                    # Display the data
                    st.subheader("NIFTY Options Chain Data")
                    
                    # Add filters
                    col1, col2 = st.columns(2)
                    with col1:
                        option_type_filter = st.selectbox("Filter by Option Type:", ["All", "CE", "PE"])
                    with col2:
                        if not df_nifty.empty:
                            min_strike = int(df_nifty['Strike'].min())
                            max_strike = int(df_nifty['Strike'].max())
                            strike_range = st.slider("Strike Price Range:", min_strike, max_strike, (min_strike, max_strike))
                        else:
                            strike_range = (0, 100)
                    
                    # Apply filters
                    filtered_df = df_nifty.copy()
                    if option_type_filter != "All":
                        filtered_df = filtered_df[filtered_df['Type'] == option_type_filter]
                    if not df_nifty.empty:
                        filtered_df = filtered_df[
                            (filtered_df['Strike'] >= strike_range[0]) & 
                            (filtered_df['Strike'] <= strike_range[1])
                        ]
                    
                    st.dataframe(filtered_df)
                    
                    # Download button
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download NIFTY Options Data as CSV",
                        data=csv,
                        file_name=f"nifty_options_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                else:
                    st.warning("Could not process NIFTY options data.")
            else:
                st.error("Failed to fetch NIFTY options data.")
    else:
        st.info("Click 'Fetch NIFTY Options Data' to load the latest NIFTY options chain data.") 
