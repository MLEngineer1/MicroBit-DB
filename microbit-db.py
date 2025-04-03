import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64
from PIL import Image
import io
import plotly.express as px

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts = []
    
if 'analytics' not in st.session_state:
    st.session_state.analytics = {}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = ""

# Set dark theme with improved text visibility
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
    .st-b7, .st-cg, .st-ch, .st-ci, .stTextInput>div>div>input, .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea, .stSelectbox>div>div>select, .stDateInput>div>div>input {{
        color: var(--text) !important;
    }}
    .stButton>button {{
        color: var(--text);
        background-color: var(--card);
        border: 1px solid var(--primary);
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }}
    .stButton>button:hover {{
        color: var(--text);
        background-color: #2a3a5a;
        border: 1px solid var(--primary);
    }}
    .metric-card {{
        background-color: var(--card);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-left: 4px solid var(--primary);
    }}
    .tweet-card {{
        background-color: var(--card);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 3px solid var(--primary);
    }}
    .positive {{
        color: var(--primary);
    }}
    .negative {{
        color: var(--danger);
    }}
    </style>
    """, unsafe_allow_html=True)

# Trading platforms and types
TRADING_PLATFORMS = [
    "Binance", "Bybit", "Bitunix", "HFM", "FBS", 
    "HTX", "Kraken", "PocketOption", "Weex", "Mexc"
]

TRADING_TYPES = [
    "Arbitrage", "Futures", "Forex", "Crypto", "Options", "Stocks"
]

# Calculate analytics
def calculate_analytics():
    if not st.session_state.posts:
        return {}
    
    df = pd.DataFrame(st.session_state.posts)
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
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
        'weekly': df[(df['date'].dt.isocalendar().week == current_week) & (df['date'].dt.year == current_year)],
        'monthly': df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)],
        'quarterly': df[(df['date'].dt.quarter == current_quarter) & (df['date'].dt.year == current_year)],
        'yearly': df[df['date'].dt.year == current_year],
        'all_time': df
    }
    
    analytics = {}
    for timeframe, data in timeframes.items():
        if len(data) > 0:
            analytics[timeframe] = {
                'total_profit': data['profit_amount'].sum(),
                'avg_profit_pct': data['profit_percent'].mean(),
                'total_principal': data['total_stake'].sum(),
                'win_rate': len(data[data['profit_amount'] > 0]) / len(data),
                'data': data
            }
        else:
            analytics[timeframe] = {
                'total_profit': 0,
                'avg_profit_pct': 0,
                'total_principal': 0,
                'win_rate': 0,
                'data': pd.DataFrame()
            }
    
    return analytics

# Login page
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

# Dashboard page
def dashboard_page():
    set_theme()
    st.title("📝 Trading Dashboard")
    
    with st.form("new_trade_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime.now())
            trading_platform = st.selectbox("Trading Platform", TRADING_PLATFORMS)
            trading_type = st.selectbox("Trading Type", TRADING_TYPES)
            profit_percent = st.number_input("Profit Percentage", step=0.01, format="%.2f")
        with col2:
            profit_amount = st.number_input("Profit Amount (USDT)", step=0.01, format="%.2f")
            total_stake = st.number_input("Total Stake (USDT)", step=0.01, format="%.2f")
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

# Analytics page
def analytics_page():
    set_theme()
    st.title("📊 Trading Analytics")
    
    if not st.session_state.analytics:
        st.warning("No analytics data available. Add trades first.")
        return
    
    # Timeframe tabs
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
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Total Profit</div>
                        <div class="metric-value {'positive' if data['total_profit'] >= 0 else 'negative'}">
                            ${data['total_profit']:,.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Avg Profit %</div>
                        <div class="metric-value {'positive' if data['avg_profit_pct'] >= 0 else 'negative'}">
                            {data['avg_profit_pct']:.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Total Principal</div>
                        <div class="metric-value">
                            ${data['total_principal']:,.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Win Rate</div>
                        <div class="metric-value">
                            {data['win_rate']*100:.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Charts
                df = data['data'].sort_values('date')
                
                # Profit over time
                fig1 = px.line(
                    df, 
                    x='date', 
                    y='profit_amount',
                    title=f'Profit in USDT ({label})',
                    labels={'profit_amount': 'Profit (USDT)', 'date': 'Date'},
                    color_discrete_sequence=['#4cc9f0']
                )
                fig1.update_layout(
                    plot_bgcolor='#1a2a4a',
                    paper_bgcolor='#1a2a4a',
                    font_color='white',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False),
                    hovermode='x unified'
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                # Platform distribution
                fig2 = px.pie(
                    df,
                    names='trading_platform',
                    title=f'Trading Platform Distribution ({label})',
                    color_discrete_sequence=px.colors.qualitative.Dark24
                )
                fig2.update_layout(
                    plot_bgcolor='#1a2a4a',
                    paper_bgcolor='#1a2a4a',
                    font_color='white'
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Trading type performance
                fig3 = px.bar(
                    df.groupby('trading_type')['profit_amount'].sum().reset_index(),
                    x='trading_type',
                    y='profit_amount',
                    title=f'Profit by Trading Type ({label})',
                    labels={'profit_amount': 'Profit (USDT)', 'trading_type': 'Trading Type'},
                    color='profit_amount',
                    color_continuous_scale='bluered'
                )
                fig3.update_layout(
                    plot_bgcolor='#1a2a4a',
                    paper_bgcolor='#1a2a4a',
                    font_color='white',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig3, use_container_width=True)
                
            else:
                st.warning(f"No data available for {label} timeframe")

# Tweets page
def tweets_page():
    set_theme()
    st.title("🐦 Trading Feed")
    
    # Profile header
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <div style="font-size: 3rem;">💰</div>
        <div style="margin-left: 15px;">
            <h3 style="margin: 0; color: white;">{st.session_state.username}</h3>
            <p style="margin: 0; color: #a8dadc;">@{st.session_state.username}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display simplified tweets
    if st.session_state.posts:
        for post in reversed(st.session_state.posts):  # Show newest first
            with st.container():
                st.write(f"**{post['trading_platform']} - {post['trading_type']}**")
                st.write(post['notes'])
                
                if post['screenshot']:
                    try:
                        image = Image.open(io.BytesIO(base64.b64decode(post['screenshot'])))
                        st.image(image, caption="Trade Screenshot", width=300)
                    except:
                        st.warning("Could not display image")
                
                st.write(f"{post['reaction']} {post['date']}")
                st.markdown("---")
    else:
        st.info("No trading updates yet")

# Main app
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
