from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

CHROME_DRIVER_PATH = "D:\gith\chromedriver-win64/chromedriver.exe"

TARGET_PRICE = 350

url = "https://www.adidas.pl/search?q=real+madrid"

def get_real_madrid_products():
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get(url)
        time.sleep(5)

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        products = driver.find_elements(By.CSS_SELECTOR, ".product-card_product-card-content___bjeq")
        results = []

        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, ".product-card-description_name__xHvJ2").get_attribute('innerHTML')

                price_text = product.find_element(By.CSS_SELECTOR, ".gl-price-item").get_attribute('innerHTML')
                price = float(price_text.replace("zł", "").replace(",", ".").strip())
                
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")

                if price <= TARGET_PRICE:
                    results.append((name, price, link))
            except Exception as e:
                print(f"Błąd przy odczycie produktu: {e}")

        return results
    finally:
        driver.quit()
products = get_real_madrid_products()

if products:
    print("Produkty poniżej 400 zł:")
    for name, price, link in products:
        print(f"{name} - {price} zł - {link}")
else:
    print("Nie znaleziono produktów poniżej 400 zł.")