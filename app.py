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
    """Display the conversation history."""
    for msg in st.session_state.conversation.get_conversation():
        if msg["speaker"] == "user":
            with st.chat_message("user"):
                st.write(msg["message"])
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


def display_tier1_analysis():
    """Display overall conversation analysis (Tier 1)."""
    st.markdown("---")
    st.subheader("📊 Conversation Analysis")
    
    # Get overall sentiment analysis
    user_msgs = st.session_state.conversation.get_user_messages()
    overall = st.session_state.analyzer.analyze_conversation(user_msgs)
    
    # Parse sentiment for display
    sentiment = overall["sentiment"]
    base_sentiment = sentiment.split(" ")[0]  # Get base (Positive/Negative/Neutral)
    
    # Emoji based on base sentiment
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
    
    # Display sentiment metrics - 4 columns now
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Sentiment", f"{emoji} {base_sentiment}")
    
    with col2:
        st.metric("Compound Score", f"{overall['compound']:.3f}")
    
    with col3:
        st.metric("Trajectory", f"{traj_emoji} {traj_text}")
    
    with col4:
        st.metric("Messages", overall["message_count"])
    
    # Show status tag if resolved/escalating
    if "(Resolved)" in sentiment:
        st.success("✅ **Status: Issue Resolved** - Conversation ended positively")
    elif "(Escalating)" in sentiment:
        st.error("⚠️ **Status: Escalating** - Customer dissatisfaction increasing")
    
    # Display summary
    st.info(f"**Summary:** {overall['summary']}")
    
    # Detailed breakdown
    with st.expander("📈 Detailed Sentiment Breakdown"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Positive", f"{overall['pos']:.1%}")
        with col2:
            st.metric("Neutral", f"{overall['neu']:.1%}")
        with col3:
            st.metric("Negative", f"{overall['neg']:.1%}")


def display_conversation_history():
    """Display full conversation history with sentiment tracking."""
    st.markdown("---")
    st.subheader("💬 Conversation History")
    
    for msg in st.session_state.conversation.get_conversation():
        if msg["speaker"] == "user":
            sentiment = msg.get("sentiment", "N/A")
            compound = msg.get("compound", 0)
            
            # Color code based on sentiment
            if sentiment == "Positive":
                color = "green"
                emoji = "😊"
            elif sentiment == "Negative":
                color = "red"
                emoji = "😞"
            else:
                color = "gray"
                emoji = "😐"
            
            st.markdown(f"**You:** {msg['message']}")
            st.markdown(f"→ Sentiment: :{color}[{emoji} {sentiment}] (score: {compound:.2f})")
            st.markdown("")
        else:
            st.markdown(f"**🤖 Bot:** {msg['message']}")
            st.markdown("")


def main():
    """Main application entry point."""
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
    
    # Show analysis when conversation ends (Tier 1)
    if not st.session_state.chat_active:
        display_tier1_analysis()
        display_conversation_history()
        
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
