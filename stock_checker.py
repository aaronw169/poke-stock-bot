import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
import random
import os
import json
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN and CHAT_ID environment variables must be set")

# Browser configurations
BROWSER_CONFIGS = [
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"'
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
]

# Define websites to monitor
WEBSITES = {
    'pokemon_center': {
        'name': 'Pokémon Center',
        'url': 'https://www.pokemoncenter.com/en-gb/category/elite-trainer-box',
        'product_selector': 'div.product-grid__products > div',
        'title_selector': 'h2.product-tile__name',
        'price_selector': 'span.product-tile__price',
        'stock_selector': 'div.product-tile__add-to-cart',
        'link_selector': 'a.product-tile__link',
        'base_url': 'https://www.pokemoncenter.com',
        'requires_js': True
    },
    'magic_madhouse': {
        'name': 'Magic Madhouse',
        'url': 'https://magicmadhouse.co.uk/pokemon/pokemon-sealed-product/elite-trainer-boxes',
        'product_selector': 'div.product-grid-item',
        'title_selector': 'h3.product-name',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link',
        'base_url': 'https://magicmadhouse.co.uk',
        'requires_js': True
    },
    'board_game': {
        'name': 'Board Game',
        'url': 'https://www.board-game.co.uk/buy/pokemon-tcg/',
        'product_selector': 'div.product-item',
        'title_selector': 'h1.product-title',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link',
        'base_url': 'https://www.board-game.co.uk'
    },
    'smyths': {
        'name': 'Smyths Toys',
        'url': 'https://www.smythstoys.com/uk/en-gb/search?text=pokemon+etb',
        'product_selector': 'div.product-item',
        'title_selector': 'h2.product-title',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link'
    },
    'total_cards': {
        'name': 'Total Cards',
        'url': 'https://totalcards.net/collections/pokemon-elite-trainer-boxes',
        'product_selector': 'div.product-item',
        'title_selector': 'h2.product-title',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link'
    },
    'titan_cards': {
        'name': 'Titan Cards',
        'url': 'https://titancards.co.uk/collections/collection-boxes',
        'product_selector': 'div.product-item',
        'title_selector': 'h2.product-title',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link'
    },
    'argos': {
        'name': 'Argos',
        'url': 'https://www.argos.co.uk/browse/toys/family-games/trading-cards-and-card-games/c:30425/brands:pokemon/',
        'product_selector': 'div.product-item',
        'title_selector': 'h2.product-title',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link'
    },
    'chaos_cards': {
        'name': 'Chaos Cards',
        'url': 'https://www.chaoscards.co.uk/shop/card-games/pokemon/elite-trainer-boxes-pokemon',
        'product_selector': 'div.product-item',
        'title_selector': 'h2.product-title',
        'price_selector': 'span.price',
        'stock_selector': 'div.stock-status',
        'link_selector': 'a.product-link',
        'base_url': 'https://www.chaoscards.co.uk',
        'requires_js': True
    }
}

# Keywords to identify booster boxes and elite trainer boxes
TARGET_PRODUCTS = [
    'booster box',
    'elite trainer box',
    'etb'
]

def create_session():
    """Create a requests session with randomized browser headers."""
    session = requests.Session()
    headers = random.choice(BROWSER_CONFIGS)
    session.headers.update(headers)
    return session

def add_random_delay():
    """Add a random delay between requests to avoid rate limiting."""
    delay = random.uniform(2.5, 5.5)
    time.sleep(delay)

def send_telegram_message(message):
    """Send a message to Telegram with retry logic."""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
            payload = {'chat_id': CHAT_ID, 'text': message}
            
            session = create_session()
            response = session.post(url, data=payload)
            response.raise_for_status()
            
            logging.info(f"Telegram message sent successfully: {message}")
            return True
            
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                logging.error(f"Failed to send Telegram message after {max_retries} attempts: {e}")
                return False

def get_product_links(website_config, session):
    """Get all product links from the category page."""
    try:
        # Add random delay between requests
        add_random_delay()
        
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

def check_product_stock(product, website_config, session):
    """Check if a specific product is in stock."""
    try:
        title = product.select_one(website_config['title_selector'])
        price = product.select_one(website_config['price_selector'])
        stock = product.select_one(website_config['stock_selector'])
        link = product.select_one(website_config['link_selector'])
        
        if not all([title, price, stock, link]):
            return
        
        title_text = title.text.strip()
        price_text = price.text.strip()
        link_href = urljoin(website_config['base_url'], link['href']) if 'href' in link.attrs else None
        
        # Different sites have different ways to indicate stock
        is_in_stock = False
        stock_text = stock.text.strip().lower()
        
        if website_config['name'] == 'Pokémon Center':
            is_in_stock = not any(x in stock.get('class', []) for x in ['disabled', 'out-of-stock'])
        else:
            is_in_stock = any(x in stock_text for x in ['in stock', 'available', 'add to cart'])
        
        if is_in_stock:
            message = (
                f"🎉 Pokémon TCG Item In Stock!\n"
                f"Store: {website_config['name']}\n"
                f"Product: {title_text}\n"
                f"Price: {price_text}\n"
                f"Link: {link_href}"
            )
            send_telegram_message(message)
            logging.info(f"Found in stock: {title_text} at {website_config['name']}")
        else:
            logging.info(f"Out of stock: {title_text} at {website_config['name']}")
            
    except Exception as e:
        logging.error(f"Error checking product at {website_config['name']}: {e}")

def check_website_stock(website_config, session):
    """Check all products on a website for stock."""
    try:
        logging.info(f"Checking {website_config['name']}...")
        
        if website_config.get('requires_js', False):
            logging.info(f"{website_config['name']} requires JavaScript - skipping for now")
            return
        
        response = session.get(website_config['url'])
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.select(website_config['product_selector'])
        
        if not products:
            logging.warning(f"Could not find products on {website_config['name']}")
            return
        
        logging.info(f"Found {len(products)} products on {website_config['name']}")
        
        for product in products:
            check_product_stock(product, website_config, session)
            add_random_delay()  # Add delay between product checks
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {website_config['name']}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error checking {website_config['name']}: {e}")

def check_all_products():
    """Check all products for stock across all websites."""
    logging.info("Starting product check...")
    
    session = create_session()
    
    for website_name, website_config in WEBSITES.items():
        try:
            check_website_stock(website_config, session)
            add_random_delay()  # Add delay between website checks
        except Exception as e:
            logging.error(f"Error checking {website_name}: {e}")
    
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