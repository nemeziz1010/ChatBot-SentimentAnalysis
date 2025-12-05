from src.sentiment_analyzer_roberta import SentimentAnalyzer

# Initialize
print("Loading models for Confidence Arbitration Testing...")
bot = SentimentAnalyzer()

# Extended Test Suite
test_cases = [
    # --- TEST 1: The "Slang" Safeguard (Sentiment > Irony) ---
    {
        "text": "Shut up! You actually fixed it? That's insane!", 
        "expected": "Positive",
        "logic": "Sentiment Conf (should be ~0.98) > Irony Conf (should be ~0.85)"
    },
    {
        "text": "This new feature is sick! Fast as hell.",
        "expected": "Positive",
        "logic": "Sentiment Conf (should be ~0.99) > Irony Conf (should be Low)"
    },
    {
        "text": "No way! This works perfectly!",
        "expected": "Positive",
        "logic": "Genuine excitement - Sentiment should win"
    },
    {
        "text": "OMG this is amazing! You're a lifesaver!",
        "expected": "Positive",
        "logic": "Strong positive with high sentiment confidence"
    },

    # --- TEST 2: The "Sarcasm" Flip (Irony > Sentiment) ---
    {
        "text": "Thanks for deleting my data. Really helpful.",
        "expected": "Negative",
        "logic": "Sentiment Conf (low/confused ~0.60) < Irony Conf (high ~0.95)"
    },
    {
        "text": "Great, another crash. Just what I needed.",
        "expected": "Negative",
        "logic": "Sentiment Conf (confused by 'Great') < Irony Conf (Strong)"
    },
    {
        "text": "Thanks for making me wait 20 minutes. Impressive efficiency.",
        "expected": "Negative",
        "logic": "Irony model should detect sarcasm and win"
    },
    {
        "text": "Oh wonderful, the server crashed again.",
        "expected": "Negative",
        "logic": "Positive words + sarcasm context, irony wins"
    },
    {
        "text": "Perfect timing for the app to freeze.",
        "expected": "Negative",
        "logic": "Sarcastic positive word with negative context"
    },

    # --- TEST 3: The "Neutral" Trap (Neutral + High Irony) ---
    {
        "text": "I guess that's fine, whatever.",
        "expected": "Negative",
        "logic": "Neutral Label + Irony Conf > 0.75 -> Flip to Negative"
    },
    {
        "text": "Sure, if you say so.",
        "expected": "Negative",
        "logic": "Passive aggressive - neutral with high irony"
    },

    # --- TEST 4: Clear Positive (No Sarcasm) ---
    {
        "text": "I love this service!",
        "expected": "Positive",
        "logic": "Clear positive, no irony"
    },
    {
        "text": "Thank you so much! This really helped.",
        "expected": "Positive",
        "logic": "Genuine gratitude, sentiment wins"
    },
    {
        "text": "The problem is solved, I appreciate your help.",
        "expected": "Positive",
        "logic": "Resolved issue, positive sentiment"
    },

    # --- TEST 5: Clear Negative (No Sarcasm) ---
    {
        "text": "I hate this terrible experience.",
        "expected": "Negative",
        "logic": "Direct negative, no sarcasm"
    },
    {
        "text": "This is broken and frustrating.",
        "expected": "Negative",
        "logic": "Clear complaint, no irony needed"
    },
    {
        "text": "I'm furious! My account is locked!",
        "expected": "Negative",
        "logic": "Strong negative emotion, direct"
    },

    # --- TEST 6: Neutral (No Strong Signal) ---
    {
        "text": "I have a question about my account.",
        "expected": "Neutral",
        "logic": "Informational, no emotion"
    },
    {
        "text": "What time does the service open?",
        "expected": "Neutral",
        "logic": "Simple question, neutral"
    },
]

print(f"\n{'INPUT TEXT':<55} | {'SENT':<5} | {'IRONY':<5} | {'WINNER':<10} | {'RESULT'}")
print("-" * 110)

passed = 0
failed = 0

for case in test_cases:
    # Run analysis
    final_label, scores = bot.analyze_message(case["text"])
    
    # Extract scores for debugging
    sent_conf = scores['confidence']
    irony_conf = scores['irony_confidence']
    
    # Determine who won the vote
    if sent_conf > irony_conf:
        winner = "Sentiment"
    elif irony_conf > sent_conf:
        winner = "Irony"
    else:
        winner = "Tie"

    # Check pass/fail
    is_pass = final_label.startswith(case["expected"])
    status = "✅ PASS" if is_pass else "❌ FAIL"
    
    if is_pass:
        passed += 1
    else:
        failed += 1
    
    # Print formatted row
    text_display = case['text'][:52] + "..." if len(case['text']) > 52 else case['text']
    print(f"{text_display:<55} | {sent_conf:.2f}  | {irony_conf:.2f}  | {winner:<10} | {status} {final_label}")

# Summary
print("\n" + "=" * 110)
print(f"📊 TEST SUMMARY: {passed}/{len(test_cases)} passed ({(passed/len(test_cases)*100):.1f}%)")
print("=" * 110)

if failed > 0:
    print(f"\n⚠️  {failed} test(s) failed. Review the logic above.")
else:
    print("\n🎉 All tests passed! Confidence arbitration is working correctly.")
