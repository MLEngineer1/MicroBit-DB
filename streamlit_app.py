import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import base64
from PIL import Image
import io

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts = []
    
if 'analytics' not in st.session_state:
    st.session_state.analytics = {}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# Trading platforms and pairs
TRADING_PLATFORMS = [
    "Binance", "Bybit", "Weex", "Bitunix", "Mexc", 
    "Kraken", "HTX", "Bitget", "HFM", "FBS", "PocketOption"
]

COMMON_PAIRS = [
    "BTCUSD", "ETHUSD", "XRPUSD", "SOLUSD", "USDJPY",
    "EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "GOLD"
]

# Set dark theme with improved UI elements
def set_theme():
    st.markdown(f"""
    <style>
    :root {{
        --primary: #4cc9f0;
        --background: #0a1128;
        --card: #1a2a4a;
        --text: #ffffff;
        --text-secondary: #a8dadc;
        --danger: #f72585;
    }}
    .stApp {{
        background-color: var(--background);
        color: var(--text);
    }}
    .metric-tile {{
        background-color: var(--card);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-left: 4px solid var(--primary);
    }}
    .metric-title {{
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 5px;
    }}
    .metric-value {{
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--text);
    }}
    .metric-delta {{
        font-size: 0.9rem;
        margin-top: 5px;
    }}
    .positive {{
        color: var(--primary);
    }}
    .negative {{
        color: var(--danger);
    }}
    .tweet-card {{
        background-color: var(--card);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .tweet-header {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }}
    .tweet-metrics {{
        display: flex;
        gap: 15px;
        margin-top: 10px;
        flex-wrap: wrap;
    }}
    .tweet-metric {{
        background-color: #2a3a5a;
        padding: 8px 12px;
        border-radius: 8px;
        min-width: 80px;
    }}
    .tweet-metric-value {{
        font-weight: bold;
        margin-top: 3px;
    }}
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
        font-size: 1rem;
    }}
    </style>
    """, unsafe_allow_html=True)

def calculate_analytics():
    if not st.session_state.posts:
        return {}
    
    df = pd.DataFrame(st.session_state.posts)
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    df['quarter'] = (df['date'].dt.month - 1) // 3 + 1
    df['year'] = df['date'].dt.year
    
    today = datetime.now().date()
    current_week = datetime.now().isocalendar()[1]
    current_month = datetime.now().month
    current_quarter = (datetime.now().month - 1) // 3 + 1
    current_year = datetime.now().year
    
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

def login_page():
    set_theme()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 MicroBit-DB Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if username == "admin" and password == "password":
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")

def dashboard_page():
    set_theme()
    st.title("📝 Trading Dashboard")
    
    with st.form("new_trade_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime.now())
            trading_platform = st.selectbox("Trading Platform", TRADING_PLATFORMS)
            trading_type = st.selectbox("Trading Type", ["Arbitrage", "Futures", "Forex", "Crypto", "Options"])
            profit_percent = st.number_input("Profit Percentage", step=0.01, format="%.2f")
        with col2:
            profit_amount = st.number_input("Profit Amount (USDT)", step=0.01, format="%.2f")
            total_stake = st.number_input("Total Stake (USDT)", step=0.01, format="%.2f")
            trading_pair = st.selectbox("Trading Pair", COMMON_PAIRS + ["Other"])
            if trading_pair == "Other":
                trading_pair = st.text_input("Enter custom trading pair")
            notes = st.text_area("Notes")
        
        screenshot = st.file_uploader("Upload Screenshot (optional)", type=['png', 'jpg', 'jpeg'])
        screenshot_data = None
        if screenshot is not None:
            screenshot_data = base64.b64encode(screenshot.read()).decode('utf-8')
        
        reaction = st.radio("Reaction", ["✅", "❌"])
        
        submitted = st.form_submit_button("Add Trade")
        
        if submitted:
            st.session_state.posts.append({
                'date': date.strftime('%Y-%m-%d'),
                'trading_platform': trading_platform,
                'trading_type': trading_type,
                'trading_pair': trading_pair,
                'profit_percent': profit_percent,
                'profit_amount': profit_amount,
                'total_stake': total_stake,
                'notes': notes,
                'screenshot': screenshot_data,
                'reaction': reaction,
                'timestamp': datetime.now()
            })
            st.session_state.analytics = calculate_analytics()
            st.success("Trade added successfully!")

def analytics_page():
    set_theme()
    st.title("📊 Trading Analytics")
    
    if not st.session_state.analytics:
        st.warning("No analytics data available. Add trades first.")
        return
    
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
                cols = st.columns(5)
                metrics = [
                    ("Total Profit", f"${data['total_profit']:,.2f}", 
                     f"{data['total_profit']/data['total_principal']*100:.2f}%" if data['total_principal'] > 0 else None),
                    ("Avg Profit %", f"{data['avg_profit_pct']:.2f}%", None),
                    ("Total Principal", f"${data['total_principal']:,.2f}", None),
                    ("Win Rate", f"{data['win_rate']*100:.1f}%", None),
                    ("Trades Count", str(data['trades_count']), None)
                ]
                
                for col, (title, value, delta) in zip(cols, metrics):
                    with col:
                        delta_class = "positive" if delta and float(delta.replace('%','')) >= 0 else "negative" if delta else ""
                        st.markdown(f"""
                        <div class="metric-tile">
                            <div class="metric-title">{title}</div>
                            <div class="metric-value">{value}</div>
                            {f'<div class="metric-delta {delta_class}">↑ {delta}</div>' if delta else ''}
                        </div>
                        """, unsafe_allow_html=True)
                
                platform_tab, pair_tab = st.tabs(["By Platform", "By Trading Pair"])
                
                with platform_tab:
                    if data['platform_metrics']:
                        platform_df = pd.DataFrame.from_dict(data['platform_metrics'], orient='index')
                        platform_df = platform_df.sort_values('total_profit', ascending=False)
                        
                        st.subheader("Platform Performance")
                        st.dataframe(
                            platform_df.style.format({
                                'total_profit': '${:,.2f}',
                                'avg_profit_pct': '{:.2f}%',
                                'total_principal': '${:,.2f}',
                                'win_rate': '{:.1%}'
                            }),
                            use_container_width=True
                        )
                        
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
                
                with pair_tab:
                    if data['pair_metrics']:
                        pair_df = pd.DataFrame.from_dict(data['pair_metrics'], orient='index')
                        pair_df = pair_df.sort_values('total_profit', ascending=False)
                        
                        st.subheader("Pair Performance")
                        st.dataframe(
                            pair_df.style.format({
                                'total_profit': '${:,.2f}',
                                'avg_profit_pct': '{:.2f}%',
                                'total_principal': '${:,.2f}',
                                'win_rate': '{:.1%}'
                            }),
                            use_container_width=True
                        )
                        
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
                
                st.subheader("Profit Trend")
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

def tweets_page():
    set_theme()
    st.title("🐦 Trading Feed")
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="font-size: 3rem;">💰</div>
        <div style="margin-left: 15px;">
            <h3 style="margin: 0; color: white;">MicroBit-DB</h3>
            <p style="margin: 0; color: #a8dadc;">@MicroBitTrades</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.posts:
        for post in reversed(st.session_state.posts):
            profit_class = "positive" if post['profit_amount'] >= 0 else "negative"
            
            st.markdown(f"""
            <div class="tweet-card">
                <div class="tweet-header">
                    <strong>{post['trading_platform']} • {post['trading_type']} • {post['trading_pair']}</strong>
                    <span>{post['date']}</span>
                </div>
                <p>{post['notes']}</p>
                {f'<img src="data:image/png;base64,{post["screenshot"]}" style="max-width: 100%; border-radius: 8px; margin: 10px 0;">' if post['screenshot'] else ''}
                <div class="tweet-metrics">
                    <div class="tweet-metric">
                        <div>Profit</div>
                        <div class="tweet-metric-value {profit_class}">${post['profit_amount']:,.2f}</div>
                    </div>
                    <div class="tweet-metric">
                        <div>Profit %</div>
                        <div class="tweet-metric-value {profit_class}">{post['profit_percent']:.2f}%</div>
                    </div>
                    <div class="tweet-metric">
                        <div>Stake</div>
                        <div class="tweet-metric-value">${post['total_stake']:,.2f}</div>
                    </div>
                    <div style="margin-left: auto; font-size: 1.5rem; display: flex; align-items: center;">
                        {post['reaction']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No trading updates yet")

def main():
    if not st.session_state.authenticated:
        login_page()
        return
    
    set_theme()
    st.sidebar.title("MicroBit-DB")
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    
    page = st.sidebar.radio("Navigation", ["Dashboard", "Analytics", "Tweets"])
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Tweets":
        tweets_page()
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.experimental_rerun()

if __name__ == "__main__":
    main()
