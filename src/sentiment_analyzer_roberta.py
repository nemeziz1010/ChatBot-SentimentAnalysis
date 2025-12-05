from transformers import pipeline
import numpy as np


class SentimentAnalyzer:
    """
    Production-grade sentiment analysis using CardiffNLP RoBERTa models.
    Uses a hybrid architecture with separate sentiment and irony detection.
    """
    
    def __init__(self):
        print("Loading sentiment analysis models...")
        
        # Sentiment Analysis Model
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            truncation=True,
            max_length=512
        )
        
        # Irony/Sarcasm Detection Model (same research group)
        self.irony_detector = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-irony",
            truncation=True,
            max_length=512
        )
        
        print("✓ Models loaded successfully!")
    
    def analyze_message(self, text: str) -> tuple:
        """
        Analyze sentiment using confidence arbitration between sentiment and irony models.
        The model with higher confidence wins.
        
        Args:
            text: The message to analyze
            
        Returns:
            tuple: (sentiment_label, scores_dict)
        """
        if not text or not text.strip():
            return "Neutral", {'compound': 0.0, 'label': 'neutral'}
        
        # Step 1: Get sentiment prediction
        sentiment_result = self.sentiment_analyzer(text)[0]
        sentiment_label = sentiment_result['label'].lower()
        sentiment_confidence = sentiment_result['score']
        
        # Step 2: Get irony prediction
        irony_result = self.irony_detector(text)[0]
        irony_detected = irony_result['label'] == 'irony'
        irony_confidence = irony_result['score']
        
        # Step 3: Map sentiment labels
        if sentiment_label == 'positive':
            sentiment = "Positive"
            compound = sentiment_confidence
        elif sentiment_label == 'negative':
            sentiment = "Negative"
            compound = -sentiment_confidence
        else:  # neutral
            sentiment = "Neutral"
            compound = 0.0
        
        # Step 4: Confidence Arbitration
        flipped = False
        
        # Case 1: Positive sentiment + Irony detected
        if sentiment == "Positive" and irony_detected:
            # Only flip if irony is SIGNIFICANTLY more confident (margin of 0.05)
            confidence_gap = irony_confidence - sentiment_confidence
            if confidence_gap > 0.05:
                sentiment = "Negative"
                compound = -abs(compound) * 0.7
                flipped = True
            # Otherwise: sentiment model wins, keep as Positive (genuine excitement)
        
        # Case 2: Neutral sentiment + Very High irony confidence
        elif sentiment == "Neutral" and irony_detected and irony_confidence > 0.80:
            # Only flip if irony is VERY confident (0.80+) and sentiment is truly neutral
            if sentiment_confidence < 0.70:  # Sentiment must be unsure
                sentiment = "Negative"
                compound = -0.5
                flipped = True
        
        scores = {
            'compound': round(compound, 3),
            'label': sentiment_label,
            'confidence': round(sentiment_confidence, 3),
            'irony_detected': irony_detected,
            'irony_confidence': round(irony_confidence, 3),
            'flipped': flipped
        }
        
        return sentiment, scores
    
    def _analyze_sentiment_trajectory(self, messages: list) -> dict:
        """
        Analyze how sentiment changes over the conversation.
        Detects improving, declining, or stable emotional trajectory.
        """
        if len(messages) < 2:
            return {
                'trajectory': 'stable',
                'shift_detected': False,
                'first_half_avg': 0.0,
                'second_half_avg': 0.0,
                'final_sentiment': 0.0
            }
        
        # Analyze each message
        sentiments = []
        for msg in messages:
            _, scores = self.analyze_message(msg)
            sentiments.append(scores['compound'])
        
        # Split conversation into halves
        mid = len(sentiments) // 2
        first_half = sentiments[:mid] if mid > 0 else sentiments
        second_half = sentiments[mid:] if mid > 0 else sentiments
        
        # Calculate averages
        first_avg = sum(first_half) / len(first_half) if first_half else 0
        second_avg = sum(second_half) / len(second_half) if second_half else 0
        
        # Detect shift
        shift = second_avg - first_avg
        
        if shift > 0.3:
            trajectory = 'improving'
            shift_detected = True
        elif shift < -0.3:
            trajectory = 'declining'
            shift_detected = True
        else:
            trajectory = 'stable'
            shift_detected = False
        
        return {
            'trajectory': trajectory,
            'shift_detected': shift_detected,
            'shift_magnitude': round(shift, 3),
            'first_half_avg': round(first_avg, 3),
            'second_half_avg': round(second_avg, 3),
            'final_sentiment': round(sentiments[-1], 3) if sentiments else 0.0,
            'sentiment_scores': [round(s, 3) for s in sentiments]
        }
    
    def analyze_conversation(self, messages: list) -> dict:
        """
        Analyze entire conversation sentiment with trajectory awareness.
        Recent messages are weighted more heavily (recency bias).
        
        Args:
            messages: List of user messages (strings)
            
        Returns:
            dict with comprehensive sentiment analysis
        """
        if not messages:
            return {
                "sentiment": "Neutral",
                "compound": 0.0,
                "summary": "No messages to analyze",
                "message_count": 0,
                "trajectory": "stable"
            }
        
        # Analyze trajectory
        trajectory_info = self._analyze_sentiment_trajectory(messages)
        
        # Calculate weighted average (recent messages matter more)
        individual_scores = []
        for i, msg in enumerate(messages):
            _, scores = self.analyze_message(msg)
            # Weight increases linearly toward end
            weight = 1 + (i / len(messages))
            individual_scores.append((scores['compound'], weight))
        
        # Weighted compound score
        total_weight = sum(w for _, w in individual_scores)
        weighted_compound = sum(s * w for s, w in individual_scores) / total_weight if total_weight > 0 else 0
        
        # Boost positive outcome if trajectory is improving
        if trajectory_info['trajectory'] == 'improving' and trajectory_info['final_sentiment'] > 0.1:
            weighted_compound = max(weighted_compound, trajectory_info['final_sentiment'] * 0.8)
        
        # Final classification
        if weighted_compound >= 0.05:
            sentiment = "Positive"
        elif weighted_compound <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        # Add trajectory context labels
        if trajectory_info['shift_detected']:
            if trajectory_info['trajectory'] == 'improving' and sentiment == "Positive":
                sentiment = "Positive (Resolved)"
            elif trajectory_info['trajectory'] == 'declining' and sentiment == "Negative":
                sentiment = "Negative (Escalating)"
        
        # Generate summary
        summary = self._generate_summary(sentiment, weighted_compound, len(messages), trajectory_info)
        
        return {
            "sentiment": sentiment,
            "compound": round(weighted_compound, 3),
            "summary": summary,
            "message_count": len(messages),
            "trajectory": trajectory_info['trajectory'],
            "trajectory_details": trajectory_info
        }
    
    def _generate_summary(self, sentiment: str, compound: float, num_messages: int, trajectory: dict) -> str:
        """Generate human-readable conversation summary."""
        abs_compound = abs(compound)
        
        # Determine intensity
        if abs_compound > 0.5:
            intensity = "strongly"
        elif abs_compound > 0.2:
            intensity = "moderately"
        else:
            intensity = "slightly"
        
        base_sentiment = sentiment.split(" ")[0]
        
        # Trajectory-based summaries
        if trajectory['shift_detected']:
            if trajectory['trajectory'] == 'improving':
                return f"Conversation shifted from negative to positive across {num_messages} message(s) - issue resolved"
            elif trajectory['trajectory'] == 'declining':
                return f"Conversation shifted from positive to negative across {num_messages} message(s) - growing dissatisfaction"
        
        # Standard summaries
        if base_sentiment == "Positive":
            return f"Overall {intensity} positive tone across {num_messages} message(s) - general satisfaction"
        elif base_sentiment == "Negative":
            return f"Overall {intensity} negative tone across {num_messages} message(s) - general dissatisfaction"
        else:
            return f"Neutral/balanced tone across {num_messages} message(s) - no strong emotional direction"
