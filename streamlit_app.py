import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
from PIL import Image
import io
import numpy as np

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts = []
    
if 'analytics' not in st.session_state:
    st.session_state.analytics = {
        'total_profit': 0,
        'total_percentage': 0,
        'yoy_profit': 0,
        'daily_profit': 0,
        'daily_percentage': 0
    }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Calculate analytics
def calculate_analytics():
    if not st.session_state.posts:
        return
    
    total_profit = sum(post['profit_amount'] for post in st.session_state.posts)
    total_percentage = np.mean([post['profit_percent'] for post in st.session_state.posts])
    
    one_year_ago = datetime.now() - timedelta(days=365)
    yoy_posts = [post for post in st.session_state.posts 
                if datetime.strptime(post['date'], '%Y-%m-%d') >= one_year_ago]
    yoy_profit = sum(post['profit_amount'] for post in yoy_posts)
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    daily_posts = [post for post in st.session_state.posts if post['date'] == today_str]
    daily_profit = sum(post['profit_amount'] for post in daily_posts)
    daily_percentage = np.mean([post['profit_percent'] for post in daily_posts]) if daily_posts else 0
    
    st.session_state.analytics = {
        'total_profit': total_profit,
        'total_percentage': total_percentage,
        'yoy_profit': yoy_profit,
        'daily_profit': daily_profit,
        'daily_percentage': daily_percentage
    }

# Add new post
def add_post(date, profit_percent, profit_amount, total_stake, notes, screenshot, reaction, reaction_comment):
    new_post = {
        'date': date,
        'profit_percent': profit_percent,
        'profit_amount': profit_amount,
        'total_stake': total_stake,
        'notes': notes,
        'screenshot': screenshot,
        'reaction': reaction,
        'reaction_comment': reaction_comment,
        'timestamp': datetime.now()
    }
    st.session_state.posts.insert(0, new_post)
    calculate_analytics()

# Login page
def login_page():
    st.title("🔒 Trading Tracker Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username == "admin" and password == "password":
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

# Dashboard page (for updates)
def dashboard_page():
    st.title("📝 Trading Dashboard")
    st.subheader("Add new trading updates")
    
    with st.form("new_trade_form"):
        date = st.date_input("Date", value=datetime.now())
        profit_percent = st.number_input("Profit Percentage", step=0.01, format="%.2f")
        profit_amount = st.number_input("Profit Amount (USDT)", step=0.01, format="%.2f")
        total_stake = st.number_input("Total Stake (USDT)", step=0.01, format="%.2f")
        notes = st.text_area("Notes")
        
        screenshot = st.file_uploader("Upload Screenshot (optional)", type=['png', 'jpg', 'jpeg'])
        screenshot_data = None
        if screenshot is not None:
            screenshot_data = base64.b64encode(screenshot.read()).decode('utf-8')
        
        reaction = st.radio("Reaction", ["✅", "❌"])
        reaction_comment = st.text_input("Reaction Comment")
        
        submitted = st.form_submit_button("Add Trade")
        
        if submitted:
            add_post(
                date.strftime('%Y-%m-%d'),
                profit_percent,
                profit_amount,
                total_stake,
                notes,
                screenshot_data,
                reaction,
                reaction_comment
            )
            st.success("Trade added successfully!")

# Analytics page (styled like your image)
def analytics_page():
    st.title("📊 Trading Analytics")
    
    # Header with stats
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 1rem;
        color: #6c757d;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Profit</div>
            <div class="metric-value">${st.session_state.analytics['total_profit']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Profit %</div>
            <div class="metric-value">{st.session_state.analytics['total_percentage']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">YoY Profit</div>
            <div class="metric-value">${st.session_state.analytics['yoy_profit']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Daily Profit</div>
            <div class="metric-value">${st.session_state.analytics['daily_profit']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Daily %</div>
            <div class="metric-value">{st.session_state.analytics['daily_percentage']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent trades section styled like your image
    st.markdown("### Data/board")
    
    if st.session_state.posts:
        # Display last 4 trades in cards
        for post in st.session_state.posts[:4]:
            st.markdown(f"""
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                <div style="font-weight: bold; color: #495057;">RCS: {post['profit_percent']}%</div>
                <div style="font-size: 1.2rem; font-weight: bold;">${post['profit_amount']:,.2f}</div>
                <div style="color: #6c757d; font-size: 0.9rem;">{post['date']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No trades recorded yet")
    
    st.markdown("---")
    
    # Key Views section
    st.markdown("### Key Views")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Solidification (Left)**
        - Confidential Data
        - Market
        - Cash Credit
        - Payments
        """)
        
        st.markdown("""
        **Crypto Statistics**
        - License figures based on market comparisons
        """)
        
        # Table example
        df_stats = pd.DataFrame({
            'Range': ['', ''],
            'Number': ['', ''],
            'Percentage': ['', ''],
            'Shares': ['', ''],
            'UniShares': ['', '']
        })
        st.table(df_stats)
    
    with col2:
        st.markdown("""
        **Marks**
        - Value
        - Market Overview
        - License figures based on market comparisons
        """)
        
        # Table example
        df_marks = pd.DataFrame({
            'Date': ['', ''],
            '$1,079': ['', ''],
            '$11': ['', ''],
            '$5,482': ['', ''],
            '($6,000)': ['', ''],
            '($7,000)': ['', '']
        })
        st.table(df_marks)
        
        st.markdown("""
        **Taming**
        - Crypto
        - Amazon
        - Apple
        """)

# Tweets page (styled like your image)
def tweets_page():
    st.title("🐦 Trading Feed")
    
    # User profile header
    st.markdown("""
    <style>
    .profile-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .profile-pic {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin-right: 15px;
    }
    .tweet-card {
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
    }
    .tweet-stats {
        color: #657786;
        font-size: 0.9rem;
        margin-top: 10px;
        border-top: 1px solid #e1e8ed;
        padding-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="profile-header">
        <img src="https://via.placeholder.com/60" class="profile-pic">
        <div>
            <h3 style="margin: 0;">Jlade</h3>
            <p style="margin: 0; color: #657786;">@JladeTrades</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display tweets
    if st.session_state.posts:
        for post in st.session_state.posts:
            # Format time
            post_time = datetime.strptime(post['date'], '%Y-%m-%d').strftime('%I:%M %p · %d/%m/%Y')
            
            st.markdown(f"""
            <div class="tweet-card">
                <p>{post['notes']}</p>
                <p><strong>RCS:</strong> {post['profit_percent']}% · ${post['profit_amount']:,.2f} USDT</p>
                {f'<img src="data:image/png;base64,{post["screenshot"]}" style="max-width: 100%; border-radius: 8px; margin: 10px 0;">' if post['screenshot'] else ''}
                <div style="display: flex; align-items: center; margin-top: 10px;">
                    <span style="font-size: 1.2rem; margin-right: 10px;">{post['reaction']}</span>
                    <span>{post['reaction_comment']}</span>
                </div>
                <div class="tweet-stats">
                    {np.random.randint(50, 500)}K Views · 82 Retweets · 45 Quotes · 91 Likes · 78 Bookmarks
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No trading updates yet")

# Main app
def main():
    if not st.session_state.authenticated:
        login_page()
        return
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Analytics", "Tweets"])
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Tweets":
        tweets_page()
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
