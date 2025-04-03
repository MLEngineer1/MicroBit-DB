import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from PIL import Image
import io

# Initialize session state for posts if it doesn't exist
if 'posts' not in st.session_state:
    st.session_state.posts = []

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

# Function to display posts in Twitter-like format
def display_posts():
    for idx, post in enumerate(st.session_state.posts):
        with st.container():
            st.markdown(f"### 📅 {post['date']}")
            
            # Display metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Profit %", f"{post['profit_percent']}%")
            with col2:
                st.metric("Profit Amount", f"{post['profit_amount']} USDT")
            with col3:
                st.metric("Total Stake", f"{post['total_stake']} USDT")
            
            # Display notes
            st.markdown(f"**Notes:** {post['notes']}")
            
            # Display screenshot if available
            if post['screenshot'] is not None:
                try:
                    image = Image.open(io.BytesIO(base64.b64decode(post['screenshot'])))
                    st.image(image, caption="Trade Screenshot", width=300)
                except:
                    st.warning("Could not display image")
            
            # Display reaction
            reaction_col, comment_col = st.columns([1, 10])
            with reaction_col:
                st.write(f"{post['reaction']}")
            with comment_col:
                st.write(f"{post['reaction_comment']}")
            
            st.markdown("---")  # Divider between posts

# Main app
st.title("📊 Trading Tracker")
st.subheader("Daily Trading Updates")

# Form for new post
with st.form("new_post_form"):
    st.write("Add New Trading Update")
    
    # Get current date as default
    default_date = datetime.now().strftime('%Y-%m-%d')
    
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
    
    submitted = st.form_submit_button("Post Update")
    
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
        st.success("Update posted!")

# Display all posts
st.header("Your Trading Updates")
if st.session_state.posts:
    display_posts()
else:
    st.info("No updates yet. Add your first trading update above!")
