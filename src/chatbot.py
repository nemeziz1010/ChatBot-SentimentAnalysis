import random


class Chatbot:
    """
    Context-aware conversational chatbot with sentiment-aware responses.
    Extracts topics from user messages to provide more relevant responses.
    """
    
    def __init__(self):
        # Topic keywords for context extraction
        self.topic_patterns = {
            "service": ["service", "support", "help", "assistance", "customer service"],
            "product": ["product", "item", "purchase", "order", "bought"],
            "delay": ["delay", "wait", "waiting", "slow", "long time", "forever"],
            "price": ["price", "cost", "expensive", "cheap", "money", "refund", "charge"],
            "quality": ["quality", "broken", "defective", "damaged", "doesn't work", "not working"],
            "website": ["website", "site", "app", "login", "account", "password"],
            "delivery": ["delivery", "shipping", "shipment", "arrived", "package"],
            "feature": ["feature", "function", "option", "setting", "button"],
        }
        
        # Context-aware responses with {topic} placeholder
        self.responses = {
            "negative": {
                "with_topic": [
                    "I'm sorry to hear about the {topic} issue. Let me help you with that.",
                    "I understand your frustration with the {topic}. What specifically went wrong?",
                    "That's concerning about the {topic}. Can you tell me more details?",
                    "I apologize for the {topic} problem. Let's work on resolving this together.",
                    "Thank you for bringing up the {topic} issue. How can I make this right?",
                ],
                "without_topic": [
                    "I'm sorry to hear that. Tell me more about what's bothering you.",
                    "That sounds frustrating. How can I help?",
                    "I understand. What specifically is the issue?",
                    "Let's see what we can do about this. What's going on?",
                    "I hear your concern. Can you provide more details?",
                ],
            },
            "positive": {
                "with_topic": [
                    "That's wonderful to hear about the {topic}! Is there anything else I can help with?",
                    "I'm so glad the {topic} met your expectations!",
                    "Great feedback about the {topic}! We appreciate it.",
                    "Fantastic! Happy to hear the {topic} worked out well for you.",
                ],
                "without_topic": [
                    "That's great to hear! What else can I help with?",
                    "Wonderful! I'm glad you're happy.",
                    "Awesome! Is there anything else you need?",
                    "That's fantastic! Thanks for sharing.",
                    "I'm pleased to hear that! Anything else on your mind?",
                ],
            },
            "neutral": {
                "with_topic": [
                    "I see you're asking about the {topic}. What would you like to know?",
                    "Got it, this is about the {topic}. How can I assist?",
                    "Understood. What specifically about the {topic} do you need help with?",
                ],
                "without_topic": [
                    "I see. Tell me more.",
                    "Got it. How can I assist you?",
                    "Okay. What do you need help with?",
                    "Alright. What's on your mind?",
                    "I'm here to help. What would you like to discuss?",
                ],
            },
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What brings you here?",
                "Hey! What can I do for you?",
                "Welcome! How may I assist you?",
            ],
            "goodbye": [
                "Goodbye! Have a great day!",
                "Take care! Feel free to come back anytime.",
                "See you later! Thanks for chatting.",
                "Bye! Hope I was helpful today.",
            ],
            "follow_up": {
                "negative": [
                    "I'm still here to help. What else is troubling you?",
                    "Let's continue working on this. What other concerns do you have?",
                    "I want to make sure we address everything. What else?",
                ],
                "positive": [
                    "Glad things are improving! Anything else?",
                    "That's progress! What else can I do for you?",
                    "Great! Is there anything more you'd like to discuss?",
                ],
                "neutral": [
                    "Okay, what else would you like to talk about?",
                    "Got it. Anything else I can help with?",
                    "I see. What other questions do you have?",
                ],
            },
        }
        
        self.greeting_keywords = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        self.goodbye_keywords = ["bye", "goodbye", "see you", "take care", "thanks bye", "that's all"]
        
        # Track conversation context
        self.message_count = 0
    
    def _extract_topic(self, message: str) -> str:
        """Extract the main topic from the user's message."""
        message_lower = message.lower()
        
        for topic, keywords in self.topic_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return topic
        
        return None
    
    def _format_topic(self, topic: str) -> str:
        """Format topic for display in response."""
        topic_display = {
            "service": "service",
            "product": "product",
            "delay": "delay",
            "price": "pricing",
            "quality": "quality",
            "website": "website",
            "delivery": "delivery",
            "feature": "feature",
        }
        return topic_display.get(topic, topic)
    
    def generate_response(self, user_message: str, sentiment: str) -> str:
        """
        Generate context-aware response based on user message and sentiment.
        
        Args:
            user_message: The user's input text
            sentiment: Detected sentiment ("Positive", "Negative", or "Neutral")
            
        Returns:
            Bot response string
        """
        user_lower = user_message.lower().strip()
        self.message_count += 1
        
        # Check for standalone greetings
        if any(user_lower == greet or user_lower.startswith(greet + " ") for greet in self.greeting_keywords):
            return random.choice(self.responses["greeting"])
        
        # Check for goodbye
        if any(word in user_lower for word in self.goodbye_keywords):
            return random.choice(self.responses["goodbye"])
        
        # Extract topic for context-aware response
        topic = self._extract_topic(user_message)
        sentiment_key = sentiment.lower()
        
        # Use follow-up responses after first few messages
        if self.message_count > 2 and random.random() < 0.3:
            if sentiment_key in self.responses.get("follow_up", {}):
                return random.choice(self.responses["follow_up"][sentiment_key])
        
        # Get sentiment-based responses
        if sentiment_key in self.responses:
            response_dict = self.responses[sentiment_key]
            
            if isinstance(response_dict, dict):
                if topic and "with_topic" in response_dict:
                    template = random.choice(response_dict["with_topic"])
                    return template.format(topic=self._format_topic(topic))
                elif "without_topic" in response_dict:
                    return random.choice(response_dict["without_topic"])
            elif isinstance(response_dict, list):
                return random.choice(response_dict)
        
        # Fallback to neutral
        return random.choice(self.responses["neutral"]["without_topic"])
