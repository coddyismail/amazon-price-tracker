from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import mysql.connector
import smtplib
from email.mime.text import MIMEText
import time
import re

# ========================
# Email Configuration
# ========================
SENDER = "ismail.builds@gmail.com"
PASSWORD = "kwvp gxgg zoav yuuz"  # Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# ========================
# MySQL Configuration
# ========================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="price_tracker"
)
cursor = db.cursor(dictionary=True)

# ========================
# Function: Get Product Price
# ========================
def get_price(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        html = page.content()
        browser.close()

    # Save debug HTML
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Saved debug.html (open in browser to inspect)")

    soup = BeautifulSoup(html, "html.parser")

    # --- Title ---
    title_el = soup.select_one("#productTitle") or soup.select_one(".product-title-word-break")
    title = title_el.get_text(strip=True) if title_el else "Unknown Product"

    # --- Price ---
    price_selectors = [
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#corePriceDisplay_desktop_feature_div span.a-offscreen",
        ".priceBlockBuyingPriceString",
        ".a-price-whole",
        ".a-color-price"
    ]

    price_text = None
    for sel in price_selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            price_text = el.get_text(strip=True)
            break

    if not price_text:
        print("⚠️ Price not found for URL:", url)
        raise Exception("❌ Price not found. Check debug.html")

    price_text_clean = price_text.replace("₹", "").replace(",", "").strip()
    match = re.search(r"\d+(\.\d+)?", price_text_clean)
    if not match:
        print("⚠️ Could not parse numeric price from:", price_text_clean)
        raise Exception("❌ Price parsing failed. Check debug.html")

    return title, float(match.group())

# ========================
# Function: Send Email
# ========================
def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = to

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER, PASSWORD)
        server.sendmail(SENDER, to, msg.as_string())
    print(f"📧 Email sent to {to}")

# ========================
# Function: Check Prices Once
# ========================
def check_prices():
    cursor.execute("""
        SELECT p.id, p.product_url, p.last_price, u.email 
        FROM products p 
        JOIN users u ON p.user_id=u.id
    """)
    products = cursor.fetchall()

    for row in products:
        try:
            title, current_price = get_price(row["product_url"])
            last_price = row["last_price"] or current_price
            print(f"🔎 {title} | Last: {last_price} | Current: {current_price}")

            if current_price < last_price:
                subject = f"Price Drop Alert: {title}"
                body = f"{title}\nPrice dropped from ₹{last_price} to ₹{current_price}\n{row['product_url']}"
                send_email(row["email"], subject, body)

            cursor.execute("UPDATE products SET last_price=%s WHERE id=%s", (current_price, row["id"]))
            db.commit()

            time.sleep(5)

        except Exception as e:
            print("Error:", e)

# ========================
# Main Loop: Run Every Hour
# ========================
if __name__ == "__main__":
    while True:
        print("⏳ Checking prices...")
        check_prices()
        print("✅ Done. Sleeping for 1 hour...\n")
        time.sleep(3600)  # wait 1 hour before running again
