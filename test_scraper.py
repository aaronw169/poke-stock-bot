import requests
from bs4 import BeautifulSoup
import time
import random
import json

# Test configuration for Pokemon Center
TEST_SITE = {
    'name': 'Pokémon Center',
    'url': 'https://www.pokemoncenter.com/en-gb/category/elite-trainer-box',
    'product_selector': 'div.product-grid__products',  # Main products container
    'title_selector': 'h2.product-tile__name',  # Product title
    'price_selector': 'span.product-tile__price',  # Price
    'stock_selector': 'div.product-tile__add-to-cart',  # Add to cart button indicates stock
    'link_selector': 'a.product-tile__link'  # Product link
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}

def test_scraper():
    print(f"Testing scraper for {TEST_SITE['name']}...")
    
    try:
        # Create session with headers
        session = requests.Session()
        session.headers.update(HEADERS)
        
        # Get the page
        print("Fetching page...")
        response = session.get(TEST_SITE['url'])
        response.raise_for_status()
        
        # Save the HTML for debugging
        with open("pokemon_center_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the products container
        products_container = soup.select_one(TEST_SITE['product_selector'])
        if not products_container:
            print("Could not find products container")
            return
            
        # Find all products
        products = products_container.find_all('div', class_='product-tile')
        print(f"\nFound {len(products)} products")
        
        # Print details of first 3 products
        for i, product in enumerate(products[:3], 1):
            title = product.select_one(TEST_SITE['title_selector'])
            price = product.select_one(TEST_SITE['price_selector'])
            stock = product.select_one(TEST_SITE['stock_selector'])
            link = product.select_one(TEST_SITE['link_selector'])
            
            print(f"\nProduct {i}:")
            print(f"Title: {title.text.strip() if title else 'N/A'}")
            print(f"Price: {price.text.strip() if price else 'N/A'}")
            print(f"Stock Status: {'In Stock' if stock and not 'disabled' in stock.get('class', []) else 'Out of Stock'}")
            print(f"Link: {link['href'] if link and 'href' in link.attrs else 'N/A'}")
            
            # Print raw HTML for debugging
            print("\nRaw HTML:")
            print(product.prettify())
            
    except Exception as e:
        print(f"Error: {e}")
        # Print full traceback for debugging
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper() 