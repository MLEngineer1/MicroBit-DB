import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64
from PIL import Image
import io
import plotly.express as px
import plotly.graph_objects as go

# Set dark blue theme
def set_theme():
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: #0a1128;
        color: #ffffff;
    }}
    .st-b7 {{
        color: #ffffff !important;
    }}
    .metric-card {{
        background-color: #1a2a4a;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border-left: 4px solid #4cc9f0;
    }}
    .metric-title {{
        font-size: 1rem;
        color: #a8dadc;
        margin-bottom: 5px;
    }}
    .metric-value {{
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: #1a2a4a;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #a8dadc;
    }}
    .stTabs [aria-selected="true"] {{
        background: #2a3a5a;
        color: #4cc9f0 !important;
    }}
    .stPlotlyChart {{
        background-color: #1a2a4a;
        border-radius: 10px;
        padding: 15px;
    }}
    .tweet-card {{
        background-color: #1a2a4a;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 3px solid #4cc9f0;
    }}
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'posts' not in st.session_state:
    st.session_state.posts = []
    
if 'analytics' not in st.session_state:
    st.session_state.analytics = {}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Generate sample data if empty
if not st.session_state.posts:
    start_date = datetime.now() - timedelta(days=365)
    for i in range(100):
        date = start_date + timedelta(days=i*3)
        profit_pct = np.random.uniform(-5, 10)
        profit_amt = np.random.uniform(-500, 2000)
        stake = np.random.uniform(5000, 20000)
        
        st.session_state.posts.append({
            'date': date.strftime('%Y-%m-%d'),
            'profit_percent': profit_pct,
            'profit_amount': profit_amt,
            'total_stake': stake,
            'notes': f"Trade #{i+1}",
            'screenshot': None,
            'reaction': "✅" if profit_amt > 0 else "❌",
            'reaction_comment': "Good trade" if profit_amt > 0 else "Bad trade",
            'timestamp': date
        })

# Calculate analytics for all timeframes
def calculate_analytics():
    if not st.session_state.posts:
        return
    
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
    
    st.session_state.analytics = analytics

calculate_analytics()

# Login page
def login_page():
    set_theme()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 Trading Tracker")
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
        reaction_comment = st.text_input("Reaction Comment")
        
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
                'reaction_comment': reaction_comment,
                'timestamp': datetime.now()
            })
            calculate_analytics()
            st.success("Trade added successfully!")

# Analytics page with tabs and charts
def analytics_page():
    set_theme()
    st.title("📊 Advanced Analytics")
    
    # Timeframe tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Daily", "Weekly", "Monthly", "Quarterly", "Yearly", "All Time"
    ])
    
    timeframes = {
        'Daily': 'daily',
        'Weekly': 'weekly',
        'Monthly': 'monthly',
        'Quarterly': 'quarterly',
        'Yearly': 'yearly',
        'All Time': 'all_time'
    }
    
    with tab1:
        display_timeframe_analytics('daily')
    with tab2:
        display_timeframe_analytics('weekly')
    with tab3:
        display_timeframe_analytics('monthly')
    with tab4:
        display_timeframe_analytics('quarterly')
    with tab5:
        display_timeframe_analytics('yearly')
    with tab6:
        display_timeframe_analytics('all_time')

def display_timeframe_analytics(timeframe):
    analytics = st.session_state.analytics.get(timeframe, {})
    data = analytics.get('data', pd.DataFrame())
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Profit</div>
            <div class="metric-value">${analytics.get('total_profit', 0):,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Profit %</div>
            <div class="metric-value">{analytics.get('avg_profit_pct', 0):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Principal</div>
            <div class="metric-value">${analytics.get('total_principal', 0):,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Win Rate</div>
            <div class="metric-value">{analytics.get('win_rate', 0)*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    if not data.empty:
        # Convert date to string for plotting
        plot_data = data.copy()
        plot_data['date_str'] = plot_data['date'].dt.strftime('%Y-%m-%d')
        
        # Profit over time chart
        fig1 = px.line(
            plot_data, 
            x='date', 
            y='profit_amount',
            title=f'Profit in USDT ({timeframe.capitalize()})',
            labels={'profit_amount': 'Profit (USDT)', 'date': 'Date'}
        )
        fig1.update_layout(
            plot_bgcolor='#1a2a4a',
            paper_bgcolor='#1a2a4a',
            font_color='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            hovermode='x unified'
        )
        fig1.update_traces(line_color='#4cc9f0')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Profit percentage over time
        fig2 = px.line(
            plot_data, 
            x='date', 
            y='profit_percent',
            title=f'Profit Percentage ({timeframe.capitalize()})',
            labels={'profit_percent': 'Profit (%)', 'date': 'Date'}
        )
        fig2.update_layout(
            plot_bgcolor='#1a2a4a',
            paper_bgcolor='#1a2a4a',
            font_color='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        fig2.update_traces(line_color='#a8dadc')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Profit distribution
        fig3 = px.histogram(
            plot_data,
            x='profit_amount',
            nbins=20,
            title=f'Profit Distribution ({timeframe.capitalize()})',
            labels={'profit_amount': 'Profit (USDT)'}
        )
        fig3.update_layout(
            plot_bgcolor='#1a2a4a',
            paper_bgcolor='#1a2a4a',
            font_color='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        fig3.update_traces(marker_color='#4cc9f0')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning(f"No data available for {timeframe} timeframe")

# Tweets page
def tweets_page():
    set_theme()
    st.title("🐦 Trading Feed")
    
    # User profile header
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        <img src="https://via.placeholder.com/60" style="width: 60px; height: 60px; border-radius: 50%; margin-right: 15px;">
        <div>
            <h3 style="margin: 0; color: white;">Jlade</h3>
            <p style="margin: 0; color: #a8dadc;">@JladeTrades</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display tweets
    if st.session_state.posts:
        for post in st.session_state.posts[:20]:  # Show most recent 20
            post_time = datetime.strptime(post['date'], '%Y-%m-%d').strftime('%I:%M %p · %d/%m/%Y')
            
            st.markdown(f"""
            <div class="tweet-card">
                <p style="color: white;">{post['notes']}</p>
                <p style="color: #a8dadc;"><strong>RCS:</strong> {post['profit_percent']}% · ${post['profit_amount']:,.2f} USDT</p>
                {f'<img src="data:image/png;base64,{post["screenshot"]}" style="max-width: 100%; border-radius: 8px; margin: 10px 0;">' if post['screenshot'] else ''}
                <div style="display: flex; align-items: center; margin-top: 10px;">
                    <span style="font-size: 1.2rem; margin-right: 10px; color: {'#4cc9f0' if post['reaction'] == '✅' else '#f72585'};">{post['reaction']}</span>
                    <span style="color: #a8dadc;">{post['reaction_comment']}</span>
                </div>
                <div style="color: #6c757d; font-size: 0.9rem; margin-top: 10px; border-top: 1px solid #2a3a5a; padding-top: 10px;">
                    {post_time} · {np.random.randint(50, 500)}K Views · 82 Retweets · 45 Quotes · 91 Likes · 78 Bookmarks
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
