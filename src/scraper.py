from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import ssl
from datetime import datetime

ssl._create_default_https_context = ssl._create_stdlib_context

class Scraper:
    def __init__(self, ignore, dining_hall="terrace"):
        self.ignore = ignore
        self.dining_hall = dining_hall

        options = Options()
        #options.add_argument("--window-size=1920,1200")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

        opener = urllib.request.build_opener()
        opener.addheaders = [
            (
                "User-Agent",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
            )
        ]
        urllib.request.install_opener(opener)

    def scrape(self):
        url = f"https://ithacadining.nutrislice.com/menu/{self.dining_hall}-dining-hall/dinner/{datetime.now().strftime('%Y-%m-%d')}"
        soup = self.make_request(url)

        menu_items = soup.find_all('span', class_='food-name')

        if not menu_items:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'View Menus')]"))
                ).click()
                time.sleep(5)
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                menu_items = soup.find_all('span', class_='food-name')
            except Exception as e:
                print(f"Error navigating the page: {e}")
                return "No dinner items found."

        dinner_menu = self.filter_items([item.get_text(strip=True) for item in menu_items])

        return ", ".join(dinner_menu) if dinner_menu else "No dinner items found."

    def make_request(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            return soup
        except Exception as e:
            print(f"Failed to load page: {e}")
            return BeautifulSoup("", "html.parser")

    def filter_items(self, items):
        return [item for item in items if not any(ignored.lower() in item.lower() for ignored in self.ignore)]

    def close(self):
        self.driver.quit()

    def __del__(self):
        self.close()