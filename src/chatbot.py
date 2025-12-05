import random


class Chatbot:
    """
    Simple conversational chatbot with sentiment-aware responses.
    """
    
    def __init__(self):
        self.responses = {
            "negative": [
                "I'm sorry to hear that. Tell me more about what's bothering you.",
                "That sounds frustrating. How can I help?",
                "I understand. What specifically is the issue?",
                "Let's see what we can do about this. What's going on?",
            ],
            "positive": [
                "That's great to hear!",
                "Wonderful! Glad you're happy.",
                "Awesome! What else can I help with?",
                "That's fantastic!",
            ],
            "neutral": [
                "I see. Tell me more.",
                "Got it. How can I assist you?",
                "Okay. What do you need help with?",
                "Alright. What's on your mind?",
            ],
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What brings you here?",
                "Hey! What can I do for you?",
            ],
            "goodbye": [
                "Goodbye! Have a great day!",
                "Take care!",
                "See you later!",
            ],
        }
        
        self.greeting_keywords = ["hello", "hi", "hey"]
        self.goodbye_keywords = ["bye", "goodbye"]
    
    def generate_response(self, user_message: str, sentiment: str) -> str:
        """
        Generate response based on user message and sentiment.
        
        Args:
            user_message: The user's input text
            sentiment: Detected sentiment ("Positive", "Negative", or "Neutral")
            
        Returns:
            Bot response string
        """
        user_lower = user_message.lower().strip()
        
        # Check for standalone greetings
        if user_lower in self.greeting_keywords:
            return random.choice(self.responses["greeting"])
        
        # Check for goodbye
        if any(word in user_lower for word in self.goodbye_keywords):
            return random.choice(self.responses["goodbye"])
        
        # Sentiment-based response
        sentiment_key = sentiment.lower()
        if sentiment_key in self.responses:
            return random.choice(self.responses[sentiment_key])
        
        # Fallback to neutral
        return random.choice(self.responses["neutral"])
