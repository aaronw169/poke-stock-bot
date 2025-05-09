import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
import random
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_checker.log'),
        logging.StreamHandler()
    ]
)

# Get sensitive data from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', '7619245816:AAGk5_3isC3Qyx9skijUVHTiPB8ejfsXBCk')
CHAT_ID = os.getenv('CHAT_ID', '516208916')

# Define websites to monitor
WEBSITES = {
    'pokemon_center': {
        'name': 'Pokémon Center',
        'url': 'https://www.pokemoncenter.com/en-gb/category/elite-trainer-box',
        'product_selector': 'div.product-tile',
        'title_selector': 'div.product-name',
        'price_selector': 'span.price',
        'stock_selector': 'div.product-availability',
        'link_selector': 'a.product-link'
    },
    'board_game': {
        'name': 'Board Game',
        'url': 'https://www.board-game.co.uk/buy/pokemon-tcg/',
        'product_selector': 'div.product-item',
        'title_selector': 'h1.product-title',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link'
    }
}

# Keywords to identify booster boxes and elite trainer boxes
TARGET_PRODUCTS = [
    'booster box',
    'elite trainer box',
    'etb'
]

# More realistic browser headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

def create_session():
    """Create a requests session with proper headers."""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session

def send_telegram_message(message):
    """Send a message to Telegram."""
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {'chat_id': CHAT_ID, 'text': message}
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info(f"Telegram message sent successfully: {message}")
        return True
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

def test_telegram_notification():
    """Test the Telegram notification system."""
    test_message = (
        "🔔 Test Notification\n"
        "This is a test message to verify that the Telegram bot is working correctly.\n"
        "If you receive this message, the notification system is working!"
    )
    success = send_telegram_message(test_message)
    if success:
        logging.info("Telegram test notification sent successfully")
    else:
        logging.error("Failed to send Telegram test notification")
    return success

def get_product_links(website_config, session):
    """Get all product links from the category page."""
    try:
        # Add random delay between requests
        time.sleep(random.uniform(2, 5))
        
        res = session.get(website_config['url'])
        res.raise_for_status()
        
        # Save the HTML for debugging if needed
        with open(f"{website_config['name'].lower().replace(' ', '_')}_page.html", "w", encoding="utf-8") as f:
            f.write(res.text)
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Find all product links
        product_links = []
        for product in soup.find_all('div', class_=website_config['product_selector'].split('.')[-1]):
            link = product.find('a', class_=website_config['link_selector'].split('.')[-1])
            if link and 'href' in link.attrs:
                product_links.append(link['href'])
        
        logging.info(f"Found {len(product_links)} products on {website_config['name']}")
        return product_links
    except Exception as e:
        logging.error(f"Error getting product links from {website_config['name']}: {e}")
        return []

def is_target_product(title):
    """Check if the product is a booster box or elite trainer box."""
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in TARGET_PRODUCTS)

def check_product_stock(link, website_config, session):
    """Check if a specific product is in stock."""
    try:
        # Add random delay between requests
        time.sleep(random.uniform(2, 5))
        
        res = session.get(link)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Get product title
        title = soup.find(website_config['title_selector'].split('.')[0], 
                         class_=website_config['title_selector'].split('.')[-1])
        if not title:
            return
        
        title_text = title.text.strip()
        
        # Only check booster boxes and elite trainer boxes
        if not is_target_product(title_text):
            return
        
        # Check stock status
        stock_status = soup.find(website_config['stock_selector'].split('.')[0],
                               class_=website_config['stock_selector'].split('.')[-1])
        if not stock_status:
            return
        
        if "in stock" in stock_status.text.lower():
            price = soup.find(website_config['price_selector'].split('.')[0],
                            class_=website_config['price_selector'].split('.')[-1])
            price_text = price.text.strip() if price else "Price not available"
            
            message = (
                f"🎉 Pokémon TCG Item In Stock!\n"
                f"Store: {website_config['name']}\n"
                f"Product: {title_text}\n"
                f"Price: {price_text}\n"
                f"Link: {link}"
            )
            send_telegram_message(message)
            logging.info(f"Found in stock: {title_text} at {website_config['name']}")
        else:
            logging.info(f"Out of stock: {title_text} at {website_config['name']}")
            
    except Exception as e:
        logging.error(f"Error checking product {link} at {website_config['name']}: {e}")

def check_all_products():
    """Check all products for stock across all websites."""
    logging.info("Starting product check...")
    
    session = create_session()
    
    for website_name, website_config in WEBSITES.items():
        logging.info(f"Checking {website_name}...")
        product_links = get_product_links(website_config, session)
        
        for link in product_links:
            check_product_stock(link, website_config, session)
            time.sleep(random.uniform(2, 4))  # Random delay between requests
    
    logging.info("Finished checking all products")

def send_daily_status():
    """Send a daily status message at 20:00."""
    current_time = datetime.now().strftime("%H:%M")
    message = (
        f"🤖 Daily Status Update ({current_time})\n"
        f"Bot is still running and monitoring for Pokémon TCG products!\n"
        f"Monitoring websites:\n" + 
        "\n".join([f"• {config['name']}" for config in WEBSITES.values()])
    )
    send_telegram_message(message)

def main():
    """Main function to run the stock checker."""
    logging.info("Starting Pokémon TCG Stock Checker")
    
    # Test Telegram notifications first
    if not test_telegram_notification():
        logging.error("Telegram notification test failed. Please check your bot token and chat ID.")
        return
    
    last_status_time = None
    
    while True:
        try:
            current_time = datetime.now()
            
            # Send daily status at 20:00
            if current_time.hour == 20 and (last_status_time is None or 
                current_time.date() != last_status_time.date()):
                send_daily_status()
                last_status_time = current_time
            
            check_all_products()
            logging.info("Waiting 10 minutes before next check...")
            time.sleep(600)  # Check every 10 minutes
            
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()