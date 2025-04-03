import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
from PIL import Image
import io
import numpy as np

# Initialize session state for posts and analytics if they don't exist
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

# Function to calculate analytics
def calculate_analytics():
    if not st.session_state.posts:
        return
    
    # Calculate totals
    total_profit = sum(post['profit_amount'] for post in st.session_state.posts)
    total_percentage = np.mean([post['profit_percent'] for post in st.session_state.posts])
    
    # Calculate YoY (simplified as last 365 days)
    one_year_ago = datetime.now() - timedelta(days=365)
    yoy_posts = [post for post in st.session_state.posts 
                if datetime.strptime(post['date'], '%Y-%m-%d') >= one_year_ago]
    yoy_profit = sum(post['profit_amount'] for post in yoy_posts)
    
    # Calculate daily (today's posts)
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

# Function to add a new post
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
    st.session_state.posts.insert(0, new_post)  # Add to beginning to show newest first
    calculate_analytics()

# Function to display posts in Twitter-like format
def display_tweets():
    for idx, post in enumerate(st.session_state.posts):
        with st.container():
            # Header with date and user info
            col1, col2 = st.columns([1, 20])
            with col1:
                st.image("https://via.placeholder.com/50", width=50)
            with col2:
                st.markdown(f"**Jlade** @JladeTrades · {post['date']}")
            
            # Post content
            st.markdown(f"{post['notes']}")
            
            # Display metrics in a compact format
            st.markdown(f"""
            **RCS:** {post['profit_percent']}%  
            ${post['profit_amount']:,.2f} USDT  
            **Stake:** ${post['total_stake']:,.2f} USDT
            """)
            
            # Display screenshot if available
            if post['screenshot'] is not None:
                try:
                    image = Image.open(io.BytesIO(base64.b64decode(post['screenshot'])))
                    st.image(image, caption="Trade Screenshot", width=300)
                except:
                    st.warning("Could not display image")
            
            # Reaction and engagement (simulated)
            st.markdown(f"{post['reaction']} {post['reaction_comment']}")
            
            # Simulated engagement metrics
            views = np.random.randint(1000, 100000)
            st.markdown(f"""
            <div style="color: #666; font-size: 0.9em; margin-top: -15px;">
                {views:,} Views · 82 Retweets · 45 Quotes · 91 Likes · 78 Bookmarks
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")  # Divider between posts

# Dashboard page
def dashboard_page():
    st.title("📊 Trading Dashboard")
    
    # Display key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Profit", f"${st.session_state.analytics['total_profit']:,.2f}")
    with col2:
        st.metric("Avg Profit %", f"{st.session_state.analytics['total_percentage']:.2f}%")
    with col3:
        st.metric("YoY Profit", f"${st.session_state.analytics['yoy_profit']:,.2f}")
    with col4:
        st.metric("Daily Profit", f"${st.session_state.analytics['daily_profit']:,.2f}")
    with col5:
        st.metric("Daily %", f"{st.session_state.analytics['daily_percentage']:.2f}%")
    
    st.markdown("---")
    
    # Recent trades table
    st.subheader("Recent Trades")
    if st.session_state.posts:
        recent_posts = pd.DataFrame(st.session_state.posts[:10])  # Show last 10
        st.dataframe(recent_posts[['date', 'profit_percent', 'profit_amount', 'total_stake', 'reaction']])
    else:
        st.info("No trades recorded yet")
    
    st.markdown("---")
    
    # Add new trade form
    st.subheader("Add New Trade")
    with st.form("new_trade_form"):
        date = st.date_input("Date", value=datetime.now())
        profit_percent = st.number_input("Profit Percentage", step=0.01, format="%.2f")
        profit_amount = st.number_input("Profit Amount (USDT)", step=0.01, format="%.2f")
        total_stake = st.number_input("Total Stake (USDT)", step=0.01, format="%.2f")
        notes = st.text_area("Notes")
        
        # Screenshot upload
        screenshot = st.file_uploader("Upload Screenshot (optional)", type=['png', 'jpg', 'jpeg'])
        screenshot_data = None
        if screenshot is not None:
            screenshot_data = base64.b64encode(screenshot.read()).decode('utf-8')
        
        # Reaction
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

# Tweets page
def tweets_page():
    st.title("📈 Trading Feed")
    st.subheader("Your trading updates in a social format")
    
    # Display all posts in Twitter-like format
    if st.session_state.posts:
        display_tweets()
    else:
        st.info("No updates yet. Add your first trading update in the Dashboard!")
    
    # Quick add form in sidebar
    with st.sidebar:
        st.subheader("Quick Add Trade")
        with st.form("quick_trade_form"):
            quick_date = st.date_input("Date", value=datetime.now(), key="quick_date")
            quick_profit = st.number_input("Profit %", step=0.01, format="%.2f", key="quick_profit")
            quick_amount = st.number_input("Amount (USDT)", step=0.01, format="%.2f", key="quick_amount")
            quick_notes = st.text_area("Notes", key="quick_notes")
            
            quick_submitted = st.form_submit_button("Post Update")
            
            if quick_submitted:
                add_post(
                    quick_date.strftime('%Y-%m-%d'),
                    quick_profit,
                    quick_amount,
                    0,  # Stake not required in quick add
                    quick_notes,
                    None,  # No screenshot in quick add
                    "✅",  # Default reaction
                    ""    # No comment
                )
                st.success("Update posted!")

# Main app with page navigation
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Tweets"])
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Tweets":
        tweets_page()

if __name__ == "__main__":
    main()
