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
                # 1. 載入網頁
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # 2. 精準等待主商品的庫存文字區塊出現（畫面上那一行的 class 通常是產品的購物資訊）
                # 我們直接定位包含 "out of stock" 或購物車按鈕的區域
                page.wait_for_timeout(3000) 
                
                # 3. 抓取「主商品描述與價格區域」的文字，排除下方推薦商品的干擾
                # 這裡使用丸久小山園主內容的 selector：.product-short-description 或 #product-detail
                # 為了保險，我們直接抓取前半段主要核心區塊
                main_content = page.locator("id=content").inner_text()

                # 4. 新的精準判斷邏輯
                # 如果主視覺區塊明確寫著 "out of stock" 或 "sold out"，那就是真的沒貨
                if "out of stock" in main_content.lower() or "sold out" in main_content.lower():
                    print(f"URL {url[-9:]} is still out of stock. (Confirmed)")
                else:
                    # 如果這兩個詞都沒出現在主商品區，代表可能真的轉成可以購買的按鈕了！
                    send_telegram_message(f"補貨通知：網頁顯示可能已補貨！請儘速確認：{url}")
                    print(f"Stock detected for {url}! Notification sent.")
                    
            except Exception as e:
                print(f"Error checking {url}: {e}")

if __name__ == "__main__":
    check_stock()
