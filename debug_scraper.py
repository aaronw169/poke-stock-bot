from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def debug_magic_madhouse():
    # Set up Firefox options
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    
    try:
        print("Setting up Firefox driver...")
        driver = webdriver.Firefox(options=firefox_options)
        
        print("Loading Magic Madhouse page...")
        driver.get('https://magicmadhouse.co.uk/pokemon/pokemon-sealed-product/elite-trainer-boxes')
        
        # Wait for products to load
        print("Waiting for products to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-list"))
        )
        
        # Let the page fully render
        time.sleep(2)
        
        # Get the page source
        content = driver.page_source
        
        # Save the HTML for inspection
        with open("magic_madhouse_debug.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Saved HTML to magic_madhouse_debug.html")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Try different selectors
        selectors = [
            'div.product-list-item',
            'div.product-item',
            'div.product',
            'div.product-list > div',
            'div.product-grid > div'
        ]
        
        print("\nTrying different selectors:")
        for selector in selectors:
            elements = soup.select(selector)
            print(f"\nSelector '{selector}':")
            print(f"Found {len(elements)} elements")
            
            if elements:
                # Print the first element's structure
                print("\nFirst element structure:")
                print(elements[0].prettify()[:500])
                
                # Try to find common product elements
                title = elements[0].find(['h1', 'h2', 'h3', 'h4']) or elements[0].find(class_=['title', 'name', 'product-name'])
                price = elements[0].find(class_=['price', 'product-price'])
                stock = elements[0].find(class_=['stock', 'availability', 'stock-status'])
                
                if title:
                    print(f"\nFound title: {title.text.strip()}")
                if price:
                    print(f"Found price: {price.text.strip()}")
                if stock:
                    print(f"Found stock status: {stock.text.strip()}")
        
        # Print all div classes to help identify the correct container
        print("\nAll div classes found on the page:")
        div_classes = set()
        for div in soup.find_all('div', class_=True):
            div_classes.update(div['class'])
        print(sorted(div_classes))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_magic_madhouse() 