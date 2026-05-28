import os
import sys
import requests
from playwright.sync_api import sync_playwright

def send_telegram_message(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, json=payload).raise_for_status()
    except Exception as e:
        print(f"Failed to send: {e}")

def check_stock():
    url = "https://www.marukyu-koyamaen.co.jp/english/shop/products/catalog/matcha/principal"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Add user-agent to avoid simple bot detection
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"})
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            content = page.content()
            
            # Simple stock check logic
            if "Sold out" not in content and "Out of stock" not in content:
                send_telegram_message(f"補貨通知：網頁顯示可能已補貨！請儘速確認：{url}")
                print("Stock detected! Notification sent.")
            else:
                print("Still out of stock.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_stock()
