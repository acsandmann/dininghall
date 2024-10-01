import json
import requests
import datetime
from scraper import Scraper
from concurrent.futures import ThreadPoolExecutor


def send_notification(menu_text, token, dh):
    chanify_url = f"https://api.chanify.net/v1/sender/{token}"

    payload = {
        "text": f"Dinner at the {dh} Dining Hall:\n{menu_text}",
        "action": f"Open|https://ithacadining.nutrislice.com/menu/{dh}-dining-hall/dinner"
    }

    response = requests.post(chanify_url, data=payload)

    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print(f"Failed to send notification: {response.status_code}, {response.text}")


def scrape_and_notify(dh, config):
    scraper = Scraper(config["ignore"], dh)
    menu = scraper.scrape()
    print(f"{dh} Menu fetched:\n", menu)
    send_notification(menu, config["token"], dh)


if __name__ == "__main__":
    with open('./config.json', 'r') as config:
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(scrape_and_notify, ["terrace", "campus-center"], [json.load(config)] * 2)
