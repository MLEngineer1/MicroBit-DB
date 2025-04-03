import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts = []
    
if 'analytics' not in st.session_state:
    st.session_state.analytics = {}

# Trading platforms and pairs
TRADING_PLATFORMS = [
    "Binance", "Bybit", "Weex", "Bitunix", "Mexc", 
    "Kraken", "HTX", "Bitget", "HFM", "FBS", "PocketOption"
]

COMMON_PAIRS = [
    "BTCUSD", "ETHUSD", "XRPUSD", "SOLUSD", "USDJPY",
    "EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "GOLD"
]

# Calculate comprehensive analytics
def calculate_analytics():
    if not st.session_state.posts:
        return {}
    
    df = pd.DataFrame(st.session_state.posts)
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    df['quarter'] = (df['date'].dt.month - 1) // 3 + 1
    df['year'] = df['date'].dt.year
    
    # Current date filters
    today = datetime.now().date()
    current_week = datetime.now().isocalendar()[1]
    current_month = datetime.now().month
    current_quarter = (datetime.now().month - 1) // 3 + 1
    current_year = datetime.now().year
    
    # Timeframe calculations
    timeframes = {
        'daily': df[df['date'].dt.date == today],
        'weekly': df[(df['date'].dt.isocalendar().week == current_week) & 
                   (df['date'].dt.year == current_year)],
        'monthly': df[(df['date'].dt.month == current_month) & 
                    (df['date'].dt.year == current_year)],
        'quarterly': df[(df['date'].dt.quarter == current_quarter) & 
                      (df['date'].dt.year == current_year)],
        'yearly': df[df['date'].dt.year == current_year],
        'all_time': df
    }
    
    analytics = {}
    for timeframe, data in timeframes.items():
        timeframe_data = {}
        
        # Platform-specific analytics
        platform_metrics = {}
        for platform in TRADING_PLATFORMS:
            platform_df = data[data['trading_platform'] == platform]
            if not platform_df.empty:
                platform_metrics[platform] = {
                    'total_profit': platform_df['profit_amount'].sum(),
                    'avg_profit_pct': platform_df['profit_percent'].mean(),
                    'total_principal': platform_df['total_stake'].sum(),
                    'win_rate': len(platform_df[platform_df['profit_amount'] > 0]) / len(platform_df),
                    'trades_count': len(platform_df)
                }
        
        # Pair-specific analytics
        pair_metrics = {}
        unique_pairs = data['trading_pair'].unique()
        for pair in unique_pairs:
            pair_df = data[data['trading_pair'] == pair]
            if not pair_df.empty:
                pair_metrics[pair] = {
                    'total_profit': pair_df['profit_amount'].sum(),
                    'avg_profit_pct': pair_df['profit_percent'].mean(),
                    'total_principal': pair_df['total_stake'].sum(),
                    'win_rate': len(pair_df[pair_df['profit_amount'] > 0]) / len(pair_df),
                    'trades_count': len(pair_df)
                }
        
        # Overall timeframe metrics
        if not data.empty:
            timeframe_data = {
                'total_profit': data['profit_amount'].sum(),
                'avg_profit_pct': data['profit_percent'].mean(),
                'total_principal': data['total_stake'].sum(),
                'win_rate': len(data[data['profit_amount'] > 0]) / len(data),
                'trades_count': len(data),
                'platform_metrics': platform_metrics,
                'pair_metrics': pair_metrics,
                'data': data
            }
        else:
            timeframe_data = {
                'total_profit': 0,
                'avg_profit_pct': 0,
                'total_principal': 0,
                'win_rate': 0,
                'trades_count': 0,
                'platform_metrics': {},
                'pair_metrics': {},
                'data': pd.DataFrame()
            }
        
        analytics[timeframe] = timeframe_data
    
    return analytics

# Analytics page with enhanced features
def analytics_page():
    st.title("📊 Trading Analytics")
    
    if not st.session_state.posts:
        st.warning("No trading data available. Add trades to see analytics.")
        return
    
    st.session_state.analytics = calculate_analytics()
    
    # Main timeframe tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Daily", "Weekly", "Monthly", "Quarterly", "Yearly", "All Time"
    ])
    
    timeframes = {
        "Daily": "daily",
        "Weekly": "weekly",
        "Monthly": "monthly",
        "Quarterly": "quarterly",
        "Yearly": "yearly",
        "All Time": "all_time"
    }
    
    for tab, (label, timeframe) in zip([tab1, tab2, tab3, tab4, tab5, tab6], timeframes.items()):
        with tab:
            data = st.session_state.analytics.get(timeframe, {})
            
            if not data.get('data', pd.DataFrame()).empty:
                # Metrics row
                st.subheader(f"{label} Performance")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Profit", f"${data['total_profit']:,.2f}",
                            delta=f"{data['total_profit']/data['total_principal']*100:.2f}%" if data['total_principal'] > 0 else None)
                with col2:
                    st.metric("Avg Profit %", f"{data['avg_profit_pct']:.2f}%")
                with col3:
                    st.metric("Total Principal", f"${data['total_principal']:,.2f}")
                with col4:
                    st.metric("Win Rate", f"{data['win_rate']*100:.1f}%")
                with col5:
                    st.metric("Trades Count", data['trades_count'])
                
                # Platform and Pair tabs within each timeframe
                platform_tab, pair_tab = st.tabs(["By Platform", "By Trading Pair"])
                
                with platform_tab:
                    if data['platform_metrics']:
                        # Platform metrics table
                        platform_df = pd.DataFrame.from_dict(data['platform_metrics'], orient='index')
                        platform_df = platform_df.sort_values('total_profit', ascending=False)
                        st.dataframe(
                            platform_df.style.format({
                                'total_profit': '${:,.2f}',
                                'avg_profit_pct': '{:.2f}%',
                                'total_principal': '${:,.2f}',
                                'win_rate': '{:.1%}'
                            }),
                            use_container_width=True
                        )
                        
                        # Platform performance chart
                        fig1 = px.bar(
                            platform_df.reset_index(),
                            x='index',
                            y='total_profit',
                            title=f'Profit by Platform ({label})',
                            labels={'index': 'Platform', 'total_profit': 'Profit (USD)'},
                            color='total_profit',
                            color_continuous_scale='bluered'
                        )
                        fig1.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.warning(f"No platform data for {label} timeframe")
                
                with pair_tab:
                    if data['pair_metrics']:
                        # Pair metrics table
                        pair_df = pd.DataFrame.from_dict(data['pair_metrics'], orient='index')
                        pair_df = pair_df.sort_values('total_profit', ascending=False)
                        st.dataframe(
                            pair_df.style.format({
                                'total_profit': '${:,.2f}',
                                'avg_profit_pct': '{:.2f}%',
                                'total_principal': '${:,.2f}',
                                'win_rate': '{:.1%}'
                            }),
                            use_container_width=True
                        )
                        
                        # Pair performance chart
                        fig2 = px.bar(
                            pair_df.reset_index(),
                            x='index',
                            y='total_profit',
                            title=f'Profit by Trading Pair ({label})',
                            labels={'index': 'Trading Pair', 'total_profit': 'Profit (USD)'},
                            color='total_profit',
                            color_continuous_scale='tealrose'
                        )
                        fig2.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.warning(f"No pair data for {label} timeframe")
                
                # Profit over time chart
                st.subheader(f"Profit Trend ({label})")
                time_df = data['data'].sort_values('date')
                fig3 = px.line(
                    time_df,
                    x='date',
                    y='profit_amount',
                    color='trading_platform',
                    title=f'Profit Over Time ({label})',
                    labels={'profit_amount': 'Profit (USD)', 'date': 'Date'},
                    hover_data=['trading_pair', 'profit_percent']
                )
                fig3.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    hovermode='x unified'
                )
                st.plotly_chart(fig3, use_container_width=True)
                
            else:
                st.warning(f"No data available for {label} timeframe")

# Update your dashboard_page to include trading_pair field
def dashboard_page():
    # ... [previous dashboard code] ...
    with st.form("new_trade_form"):
        # ... [other form fields] ...
        trading_pair = st.selectbox(
            "Trading Pair",
            options=COMMON_PAIRS + ["Other"],
            index=0
        )
        if trading_pair == "Other":
            trading_pair = st.text_input("Enter custom trading pair")
        
        # ... [rest of form] ...
        
        if submitted:
            st.session_state.posts.append({
                # ... [other fields] ...
                'trading_pair': trading_pair,
                # ... [other fields] ...
            })
            st.success("Trade added successfully!")

# ... [rest of your app code] ...
