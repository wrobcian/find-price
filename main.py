from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CHROME_DRIVER_PATH = "D:\gith\chromedriver-win64/chromedriver.exe"

TARGET_PRICE = 350
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CHECK_INTERVAL = 3600

URL = "https://www.adidas.pl/search?q=real+madrid"

def get_real_madrid_products(url, max_price):
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

                if "koszulka" in name.lower() and price <= max_price:
                    results.append((name, price, link))
            except Exception as e:
                print(f"Error while reading products: {e}")

        return results
    finally:
        driver.quit()

# if products:
#     print("Produkty poniżej 400 zł:")
#     for name, price, link in products:
#         print(f"{name} - {price} zł - {link}")
# else:
#     print("Could not find products under 400 zł.")
    
    
# Function to send email
def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, login, app_password):
    try:
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = to_email
        message.attach(MIMEText(body, "plain"))
 
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(login, app_password)
            server.sendmail(from_email, to_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
              

# Main function
if __name__ == "__main__":
    login = input("Your Gmail address: ")
    app_password = input("Your Gmail App Password: ")
    to_email = input("Recipient's email address: ")
 
    while True:
        products = get_real_madrid_products(URL, TARGET_PRICE)
 
        if products:
            email_body = "Products below target price:\n\n"
            email_body += "\n".join([f"{name} - {price} zł - {link}" for name, price, link in products])
            send_email(
                subject="Notification: Products below 400 zł",
                body=email_body,
                to_email=to_email,
                from_email=login,
                smtp_server=SMTP_SERVER,
                smtp_port=SMTP_PORT,
                login=login,
                app_password=app_password
            )
        else:
            print("No products found matching criteria.")
 
        print("Waiting for the next check...")
 
        for x in range(CHECK_INTERVAL, 0, -1):
            print(f"\r{x // 60}m {x % 60}s   ", end="")
            time.sleep(1)