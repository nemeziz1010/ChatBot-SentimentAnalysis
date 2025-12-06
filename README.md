# ChatBot with Sentiment Analysis 🤖

## Overview
This project delivers a chatbot with real-time sentiment analysis powered by advanced NLP models. It allows users to interact conversationally while analyzing sentiment at the message and conversation levels.

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/nemeziz1010/ChatBot-SentimentAnalysis.git
   cd ChatBot-SentimentAnalysis
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
4. Open the Streamlit UI in your browser and start chatting!

## Technologies Used
- **Programming Language:** Python (100%)
- **Framework:** Streamlit for the web interface
- **NLP Models:** CardiffNLP's RoBERTa for sentiment and irony detection
- **Libraries:**
  - `transformers` for pre-trained models
  - Streamlit for interactive web applications

## Explanation of Sentiment Logic
### Sentiment Analysis
- **Message-Level (Tier 2):** Identifies sentiment (Positive/Negative/Neutral) for individual user messages using pre-trained RoBERTa models.
- **Conversation-Level (Tier 1):** Provides overall sentiment and trajectory analysis for the entire conversation, summarizing mood shifts and dissatisfaction levels.

### Irony Detection
Uses a specialized RoBERTa model tuned for text classification to recognize sarcasm or irony in user inputs.

### Analysis Features:
- Compound score calculation for detailed sentiment intensity.
- Mood shift summary to indicate if the interaction is improving or escalating.

## Status of Tier 2 Implementation
- Message-level sentiment analysis is fully operational and integrated into the chatbot interface.
- Real-time feedback is displayed under user messages via emojis and sentiment scores.

## Optional Highlights
### Innovations
- Interactive features that allow users to end conversations and download their history in JSON format.
- Natural language summaries to explain sentiment trends over the interaction.

### Additional Features
- The chatbot extracts topics from user messages (e.g., price, quality, delivery) to provide context-aware responses.
- Incorporates trajectory-based sentiment summaries, improving customer support applications.

### Enhancements
- Future implementations can focus on integrating voice support and multilingual sentiment detection.

---

## Author
This project was developed by [@nemeziz1010](https://github.com/nemeziz1010).

Check out the application and explore sentiment-driven conversational AI!
