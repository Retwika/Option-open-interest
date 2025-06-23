"""
Plotting Utilities Module
========================

This module contains all plotting functions for both US and Indian markets.
Separated from the Streamlit app for better code organization and reusability.

"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def generate_us_plots(df, symbol):
    """Generate Matplotlib figures for US market options dashboard."""
    if df is None or df.empty:
        return None, None

    sns.set_style("whitegrid")

    # 1. Open Interest (Calls vs Puts)
    oi_summary = df.groupby('Type')['Open_Interest'].sum()
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    if not oi_summary.empty and oi_summary.sum() > 0:
        color_map = {'Call': 'g', 'Put': 'r'}
        pie_colors = [color_map.get(label) for label in oi_summary.index]
        oi_summary.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=pie_colors, ax=ax1)
        ax1.set_title(f'Open Interest Distribution for {symbol}')
        ax1.set_ylabel('')
    else:
        ax1.text(0.5, 0.5, 'No Open Interest Data', horizontalalignment='center', verticalalignment='center')
    
    # 2. Volume by Strike Price (Top 20 most active strikes)
    top_strikes_df = df.groupby('Strike')['Volume'].sum().nlargest(20).reset_index()
    plot_df = df[df['Strike'].isin(top_strikes_df['Strike'])]
    
    fig2, ax2 = plt.subplots(figsize=(15, 7))
    if not plot_df.empty and plot_df['Volume'].sum() > 0:
        sns.barplot(data=plot_df, x='Strike', y='Volume', hue='Type', 
                   palette={'Call': 'g', 'Put': 'r'}, 
                   order=sorted(plot_df['Strike'].unique()), ax=ax2)
        ax2.set_title(f'Volume by Strike Price for {symbol} (Top 20 Active Strikes)')
        ax2.set_xlabel('Strike Price')
        ax2.set_ylabel('Volume')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    else:
        ax2.text(0.5, 0.5, 'No Volume Data', horizontalalignment='center', verticalalignment='center')
    
    fig2.tight_layout()
    return fig1, fig2

def generate_nifty_plots(df):
    """Generate plots specifically for NIFTY options data."""
    if df is None or df.empty:
        return None, None, None

    sns.set_style("whitegrid")

    # 1. Open Interest Distribution
    oi_summary = df.groupby('Type')['Open_Interest'].sum()
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    if not oi_summary.empty and oi_summary.sum() > 0:
        color_map = {'CE': 'g', 'PE': 'r'}
        pie_colors = [color_map.get(label) for label in oi_summary.index]
        oi_summary.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=pie_colors, ax=ax1)
        ax1.set_title('NIFTY Open Interest Distribution')
        ax1.set_ylabel('')
    else:
        ax1.text(0.5, 0.5, 'No Open Interest Data', horizontalalignment='center', verticalalignment='center')
    
    # 2. Volume by Strike Price
    top_strikes_df = df.groupby('Strike')['Volume'].sum().nlargest(20).reset_index()
    plot_df = df[df['Strike'].isin(top_strikes_df['Strike'])]
    
    fig2, ax2 = plt.subplots(figsize=(15, 7))
    if not plot_df.empty and plot_df['Volume'].sum() > 0:
        sns.barplot(data=plot_df, x='Strike', y='Volume', hue='Type', 
                   palette={'CE': 'g', 'PE': 'r'}, 
                   order=sorted(plot_df['Strike'].unique()), ax=ax2)
        ax2.set_title('NIFTY Volume by Strike Price (Top 20 Active Strikes)')
        ax2.set_xlabel('Strike Price')
        ax2.set_ylabel('Volume')
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    else:
        ax2.text(0.5, 0.5, 'No Volume Data', horizontalalignment='center', verticalalignment='center')
    
    # 3. Put-Call Ratio
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    if not df.empty:
        pc_ratio = df.groupby('Type')['Open_Interest'].sum()
        if 'PE' in pc_ratio and 'CE' in pc_ratio and pc_ratio['CE'] > 0:
            ratio = pc_ratio['PE'] / pc_ratio['CE']
            ax3.bar(['Put-Call Ratio'], [ratio], color='orange')
            ax3.set_title(f'NIFTY Put-Call Ratio: {ratio:.2f}')
            ax3.set_ylabel('Ratio')
            ax3.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Neutral (1.0)')
            ax3.legend()
        else:
            ax3.text(0.5, 0.5, 'Insufficient data for Put-Call Ratio', 
                    horizontalalignment='center', verticalalignment='center')
    
    fig2.tight_layout()
    fig3.tight_layout()
    return fig1, fig2, fig3 
