import streamlit as st
from src.chatbot import Chatbot
from src.sentiment_analyzer_roberta import SentimentAnalyzer
from src.conversation_manager import ConversationManager


# Page configuration
st.set_page_config(
    page_title="Chatbot with Sentiment Analysis",
    page_icon="🤖",
    layout="centered"
)


def initialize_session_state():
    """Initialize all session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = Chatbot()
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = SentimentAnalyzer()
    if 'conversation' not in st.session_state:
        st.session_state.conversation = ConversationManager()
    if 'chat_active' not in st.session_state:
        st.session_state.chat_active = True


def display_header():
    """Display the app header."""
    st.title("🤖 Chatbot with Sentiment Analysis")
    st.markdown("*A conversational AI with real-time sentiment tracking*")
    st.markdown("---")


def display_conversation():
    """Display the conversation history with real-time sentiment (Tier 2)."""
    for msg in st.session_state.conversation.get_conversation():
        if msg["speaker"] == "user":
            with st.chat_message("user"):
                st.write(msg["message"])
                
                # Tier 2: Display sentiment under each user message
                sentiment = msg.get("sentiment", "N/A")
                compound = msg.get("compound", 0)
                
                # Emoji and color based on sentiment
                if sentiment == "Positive":
                    emoji = "😊"
                    color = "green"
                elif sentiment == "Negative":
                    emoji = "😞"
                    color = "red"
                else:
                    emoji = "😐"
                    color = "gray"
                
                # Display sentiment inline
                st.caption(f":{color}[{emoji} **{sentiment}** (score: {compound:.2f})]")
        else:
            with st.chat_message("assistant"):
                st.write(msg["message"])


def handle_user_input(user_input: str):
    """Process user input and generate bot response."""
    # Analyze sentiment
    sentiment, scores = st.session_state.analyzer.analyze_message(user_input)
    
    # Add user message to history
    st.session_state.conversation.add_message("user", user_input, sentiment, scores)
    
    # Generate and add bot response
    bot_response = st.session_state.chatbot.generate_response(user_input, sentiment)
    st.session_state.conversation.add_message("bot", bot_response)


def generate_mood_shift_summary(user_messages):
    """Generate a natural language summary of mood shifts (UI display only)."""
    if len(user_messages) < 2:
        return "📊 Not enough messages to detect mood shifts."
    
    # READ existing analyzed data - no new analysis
    sentiments = [msg.get('compound', 0) for msg in user_messages]
    labels = [msg.get('sentiment', 'Neutral') for msg in user_messages]
    
    first_sentiment = sentiments[0]
    last_sentiment = sentiments[-1]
    first_label = labels[0]
    last_label = labels[-1]
    
    # Negative → Positive shift
    if first_sentiment < -0.05 and last_sentiment > 0.05:
        for i, score in enumerate(sentiments):
            if score > 0.05:
                return f"🔄 **Mood Shift:** Started {first_label.lower()} → improved to {last_label.lower()} by message {i + 1}"
    
    # Positive → Negative shift
    elif first_sentiment > 0.05 and last_sentiment < -0.05:
        for i, score in enumerate(sentiments):
            if score < -0.05:
                return f"📉 **Mood Shift:** Started {first_label.lower()} → declined to {last_label.lower()} by message {i + 1}"
    
    # Consistent positive
    elif all(s > 0.05 for s in sentiments):
        return "😊 **Consistent Mood:** Positive throughout the conversation"
    
    # Consistent negative
    elif all(s < -0.05 for s in sentiments):
        return "😞 **Consistent Mood:** Negative throughout the conversation"
    
    # Consistent neutral
    elif all(-0.05 <= s <= 0.05 for s in sentiments):
        return "😐 **Consistent Mood:** Neutral throughout the conversation"
    
    # Mixed
    else:
        pos_count = sum(1 for s in sentiments if s > 0.05)
        neg_count = sum(1 for s in sentiments if s < -0.05)
        neu_count = len(sentiments) - pos_count - neg_count
        return f"🔀 **Fluctuating Mood:** Mixed emotions ({pos_count} positive, {neu_count} neutral, {neg_count} negative)"


def display_tier2_analysis():
    """Display message-level sentiment analysis (Tier 2)."""
    st.markdown("---")
    st.subheader("📝 Message-Level Sentiment Analysis (Tier 2)")
    
    user_messages = [msg for msg in st.session_state.conversation.get_conversation() if msg["speaker"] == "user"]
    
    if not user_messages:
        st.info("No messages to analyze yet.")
        return
    
    # --- BONUS: Mood Shift Summary ---
    mood_summary = generate_mood_shift_summary(user_messages)
    st.info(mood_summary)
    
    # Create a table view
    st.markdown("##### Individual Message Breakdown:")
    
    for i, msg in enumerate(user_messages, 1):
        sentiment = msg.get("sentiment", "N/A")
        compound = msg.get("compound", 0)
        timestamp = msg.get("timestamp", "N/A")
        
        # Emoji based on sentiment
        if sentiment == "Positive":
            emoji = "😊"
            color = "green"
        elif sentiment == "Negative":
            emoji = "😞"
            color = "red"
        else:
            emoji = "😐"
            color = "gray"
        
        # Display each message in an expander
        with st.expander(f"Message {i}: \"{msg['message'][:50]}...\" {emoji}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Sentiment", f"{emoji} {sentiment}")
            
            with col2:
                st.metric("Score", f"{compound:.3f}")
            
            with col3:
                st.metric("Time", timestamp)
            
            # Show full message
            st.markdown(f"**Full Message:** {msg['message']}")
            
            # Show irony detection if available
            if 'irony_detected' in msg:
                irony_status = "🎭 Yes" if msg.get('irony_detected') else "✓ No"
                st.caption(f"Irony/Sarcasm Detected: {irony_status}")


def display_tier1_analysis():
    """Display overall conversation analysis (Tier 1)."""
    st.markdown("---")
    st.subheader("📊 Overall Conversation Analysis (Tier 1)")
    
    # Get overall sentiment analysis
    user_msgs = st.session_state.conversation.get_user_messages()
    overall = st.session_state.analyzer.analyze_conversation(user_msgs)
    
    # Parse sentiment for display
    sentiment = overall["sentiment"]
    base_sentiment = sentiment.split(" ")[0]
    
    # Emoji based on sentiment keywords
    if "Positive" in sentiment:
        emoji = "😊"
    elif "Negative" in sentiment:
        emoji = "😞"
    else:
        emoji = "😐"
    
    # Trajectory emoji
    trajectory = overall.get("trajectory", "stable")
    if trajectory == "improving":
        traj_emoji = "📈"
        traj_text = "Improving"
    elif trajectory == "declining":
        traj_emoji = "📉"
        traj_text = "Declining"
    else:
        traj_emoji = "➡️"
        traj_text = "Stable"
    
    # Adjusted weights: [1.5, 1, 1.5, 1]
    # This gives Sentiment and Trajectory 50% more space than Score and Messages
    col1, col2, col3, col4 = st.columns([1.5, 1, 1.5, 1])
    
    with col1:
        # FIX: Only truncate if the text is very long, otherwise show full text
        sentiment_display = sentiment if len(sentiment) < 20 else base_sentiment
        st.metric("Overall Sentiment", f"{emoji} {sentiment_display}", help="Overall emotional tone")
    
    with col2:
        st.metric("Compound Score", f"{overall['compound']:.3f}", help="Sentiment intensity")
        
    with col3:
        st.metric("Trajectory", f"{traj_emoji} {traj_text}", help="How sentiment changed")
        
    with col4:
        st.metric("Messages", overall["message_count"], help="Total user messages")

    # Show status tag if resolved/escalating
    if "(Resolved)" in sentiment:
        st.success("✅ **Status: Issue Resolved** - Conversation ended positively")
    elif "(Escalating)" in sentiment:
        st.error("⚠️ **Status: Escalating** - Customer dissatisfaction increasing")
    
    # Display summary
    st.info(f"💬 **Summary:** {overall['summary']}")
    
    # Detailed breakdown
    if 'pos' in overall and 'neu' in overall and 'neg' in overall:
        with st.expander("📈 View Detailed Sentiment Breakdown"):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("😊 Positive", f"{overall['pos']:.1%}", help="Percentage of positive messages")
            with col_b:
                st.metric("😐 Neutral", f"{overall['neu']:.1%}", help="Percentage of neutral messages")
            with col_c:
                st.metric("😞 Negative", f"{overall['neg']:.1%}", help="Percentage of negative messages")



def main():
    """Main application entry point."""
    # --- CSS FIX for metric font size ---
    st.markdown("""
    <style>
    /* Target the value part of the metric */
    [data-testid="stMetricValue"] {
        font-size: 20px; /* Reduced to prevent truncation */
    }
    </style>
    """, unsafe_allow_html=True)
    # --- END CSS FIX ---

    initialize_session_state()
    display_header()
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        display_conversation()
    
    # Input area (only when chat is active)
    if st.session_state.chat_active:
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            handle_user_input(user_input)
            st.rerun()
        
        # End conversation button
        st.markdown("---")
        if st.button("🛑 End Conversation & Analyze", type="primary"):
            if st.session_state.conversation.get_user_message_count() > 0:
                st.session_state.chat_active = False
                st.rerun()
            else:
                st.warning("Please send at least one message before ending the conversation.")
    
    # Show analysis when conversation ends (Tier 1 & Tier 2)
    if not st.session_state.chat_active:
        display_tier2_analysis()  # Tier 2: Message-level
        display_tier1_analysis()  # Tier 1: Overall conversation
        
        # Export and restart options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Export conversation
            json_data = st.session_state.conversation.to_json()
            st.download_button(
                label="📥 Download Conversation",
                data=json_data,
                file_name="conversation.json",
                mime="application/json"
            )
        
        with col2:
            if st.button("🔄 Start New Conversation"):
                st.session_state.conversation.clear()
                st.session_state.chat_active = True
                st.rerun()


if __name__ == "__main__":
    main()
