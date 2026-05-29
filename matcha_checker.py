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
    # 欲監控的丸久小山園抹茶商品網頁清單
    urls = [
        "https://www.marukyu-koyamaen.co.jp/english/shop/products/1171020c1",
        "https://www.marukyu-koyamaen.co.jp/english/shop/products/1161020c1",
        "https://www.marukyu-koyamaen.co.jp/english/shop/products/1191040c1",
        "https://www.marukyu-koyamaen.co.jp/english/shop/products/11a1040c1",
        "https://www.marukyu-koyamaen.co.jp/english/shop/products/1181040c1"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # 設定 User-Agent 避免簡單的機器人偵測
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        })

        for url in urls:
            print(f"Checking: {url}")
            try:
                # 每個網頁獨立載入，逾時設為 60 秒
                page.goto(url, wait_until="networkidle", timeout=60000)
                content = page.content()

                # 補貨檢查邏輯：如果同時沒有 "Sold out" 且沒有 "Out of stock"
                if "Sold out" not in content and "Out of stock" not in content:
                    send_telegram_message(f"補貨通知：網頁顯示可能已補貨！請儘速確認：{url}")
                    print(f"Stock detected for {url}! Notification sent.")
                else:
                    print(f"URL {url[-9:]} is still out of stock.")
                    
            except Exception as e:
                print(f"Error checking {url}: {e}")
                
        browser.close()

if __name__ == "__main__":
    check_stock()
