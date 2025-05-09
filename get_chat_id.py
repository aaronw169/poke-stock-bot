import requests

BOT_TOKEN = '7924978090:AAHWtTWOpkY8fNu0dh_1QnSf_7dWLh9yFjk'

def get_chat_id():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    response = requests.get(url)
    data = response.json()
    
    if data['ok'] and data['result']:
        for update in data['result']:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                print(f"Your chat ID is: {chat_id}")
                return chat_id
    else:
        print("No messages found. Please send a message to your bot first!")
        return None

if __name__ == "__main__":
    get_chat_id() 