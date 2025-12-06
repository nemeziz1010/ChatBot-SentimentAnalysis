from datetime import datetime
import json
import os


class ConversationManager:
    """
    Manages conversation history and data persistence.
    Stores messages with timestamps and sentiment data.
    """
    
    def __init__(self):
        self.conversation = []
        self.user_messages = []
    
    def add_message(self, speaker: str, message: str, sentiment: str = None, scores: dict = None):
        """
        Add a message to the conversation history.
        
        Args:
            speaker: "user" or "bot"
            message: The message text
            sentiment: Sentiment label (for user messages)
            scores: Scores dict (for user messages)
        """
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "speaker": speaker,
            "message": message
        }
        
        # Add sentiment data for user messages
        if sentiment:
            entry["sentiment"] = sentiment
            entry["compound"] = round(scores.get('compound', 0), 3) if scores else 0.0
            
            # Store irony detection info if available
            if 'irony_detected' in scores:
                entry['irony_detected'] = scores['irony_detected']
                entry['irony_confidence'] = scores.get('irony_confidence', 0)
        
        self.conversation.append(entry)
        
        # Track user messages separately for Tier 1 overall analysis
        if speaker == "user":
            self.user_messages.append(message)
    
    def get_conversation(self) -> list:
        """Get the full conversation history."""
        return self.conversation
    
    def get_user_messages(self) -> list:
        """Get only user messages for overall sentiment analysis."""
        return self.user_messages
    
    def get_message_count(self) -> int:
        """Get total number of messages."""
        return len(self.conversation)
    
    def get_user_message_count(self) -> int:
        """Get number of user messages."""
        return len(self.user_messages)
    
    def save_conversation(self, filename: str = None) -> str:
        """
        Save conversation to a JSON file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            The path to the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/conversation_{timestamp}.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "conversation": self.conversation,
                "exported_at": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def clear(self):
        """Clear all conversation history."""
        self.conversation = []
        self.user_messages = []
    
    def to_json(self) -> str:
        """Export conversation as JSON string."""
        return json.dumps({
            "conversation": self.conversation,
            "exported_at": datetime.now().isoformat()
        }, indent=2, ensure_ascii=False)
