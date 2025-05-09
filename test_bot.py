import requests

BOT_TOKEN = '7924978090:AAHWtTWOpkY8fNu0dh_1QnSf_7dWLh9yFjk'
CHAT_ID = '516208916'

def test_bot():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    message = "🔔 Test Message\nThis is a test message to verify the bot is working correctly."
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Test message sent successfully!")
        print("Please check your Telegram for the test message.")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    test_bot() 