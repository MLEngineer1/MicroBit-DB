import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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

# Set dark theme with improved text visibility
def set_theme():
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: #0a1128;
        color: #ffffff;
    }}
    .st-b7, .st-cg, .st-ch, .st-ci {{
        color: #ffffff !important;
    }}
    .stButton>button {{
        color: #ffffff;
        background-color: #1a2a4a;
        border: 1px solid #4cc9f0;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }}
    .stButton>button:hover {{
        color: #ffffff;
        background-color: #2a3a5a;
        border: 1px solid #4cc9f0;
    }}
    .metric-card {{
        background-color: #1a2a4a;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-left: 4px solid #4cc9f0;
    }}
    .tweet-card {{
        background-color: #1a2a4a;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 3px solid #4cc9f0;
    }}
    .profile-header {{
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Login page
def login_page():
    set_theme()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 Trading Tracker Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if username == "admin" and password == "password":
                    st.session_state.authenticated = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")

# Dashboard page
def dashboard_page():
    set_theme()
    st.title("📝 Trading Dashboard")
    
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
        
        submitted = st.form_submit_button("Add Trade")
        
        if submitted:
            st.session_state.posts.append({
                'date': date.strftime('%Y-%m-%d'),
                'profit_percent': profit_percent,
                'profit_amount': profit_amount,
                'total_stake': total_stake,
                'notes': notes,
                'screenshot': screenshot_data,
                'reaction': reaction,
                'timestamp': datetime.now()
            })
            st.success("Trade added successfully!")

# Analytics page
def analytics_page():
    set_theme()
    st.title("📊 Trading Analytics")
    st.write("Analytics dashboard would appear here")

# Simplified Tweets page
def tweets_page():
    set_theme()
    st.title("🐦 Trading Feed")
    
    # Profile header
    st.markdown("""
    <div class="profile-header">
        <div style="font-size: 3rem;">💰</div>
        <div style="margin-left: 15px;">
            <h3 style="margin: 0; color: white;">MicroBit-DB</h3>
            <p style="margin: 0; color: #a8dadc;">@MicroBitTrades</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display simplified tweets
    if st.session_state.posts:
        for post in st.session_state.posts:
            st.markdown(f"""
            <div class="tweet-card">
                <p style="color: white; margin-bottom: 10px;">{post['notes']}</p>
                {f'<img src="data:image/png;base64,{post["screenshot"]}" style="max-width: 100%; border-radius: 8px; margin-bottom: 10px;">' if post['screenshot'] else ''}
                <div style="font-size: 1.5rem;">{post['reaction']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No trading updates yet")

# Main app
def main():
    if not st.session_state.authenticated:
        login_page()
        return
    
    set_theme()
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Analytics", "Tweets"])
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Tweets":
        tweets_page()
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()
