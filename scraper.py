import requests
from bs4 import BeautifulSoup
import time
import re

session = requests.Session()

# هدرهای قدرتمند برای شبیه‌سازی مرورگر سافاری/کروم در مک
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

URLS = {
    "Footwear": "https://www.amazon.ae/s?k=shoes&rh=n%3A11497746031&dc",
    "Fragrances": "https://www.amazon.ae/s?k=fragrance&rh=n%3A11497746031&dc"
}

def extract_price(text):
    """استخراج عدد اعشاری از یک متن مثل 'AED 150.50'"""
    if not text:
        return None
    # پیدا کردن اعداد و اعشار از داخل متن با استفاده از Regex
    match = re.search(r'[\d,]+\.?\d*', text)
    if match:
        return float(match.group().replace(',', ''))
    return None

def scrape_amazon_uae():
    deals = []
    
    for category, url in URLS.items():
        print(f"Searching in category: {category}...")
        try:
            # ایجاد تاخیر بین درخواست‌ها برای جلوگیری از بلاک شدن
            time.sleep(2)
            
            response = session.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            # اگر صفحه کپچا بود، خطا چاپ کن و برو سراغ دسته بعدی
            if "captcha" in response.text.lower() or "Type the characters you see in this image" in response.text:
                print(f"⚠️ آمازون برای دسته {category} صفحه کپچا (ضد ربات) فرستاد.")
                continue

            products = soup.find_all("div", {"data-component-type": "s-search-result"})
            print(f"تعداد {len(products)} محصول در این صفحه پیدا شد.")
            
            for product in products:
                # 1. استخراج نام محصول
                title_elem = product.find("h2")
                name = title_elem.text.strip() if title_elem else "Unknown Product"
                
                # 2. استخراج لینک
                link_elem = product.find("a", class_="a-link-normal s-no-outline")
                product_url = "https://www.amazon.ae" + link_elem['href'] if link_elem else None
                if not product_url:
                    continue

                # 3. پیدا کردن بلوک‌های قیمت با جستجوی هوشمندتر
                # قیمت فعلی معمولاً در تگ span با کلاس a-price قرار دارد
                price_spans = product.find_all("span", class_="a-price")
                
                current_price = None
                original_price = None
                
                # اگر بیش از یک قیمت پیدا شد، معمولاً دومی (یا اونی که کلاس a-text-price داره) قیمت خط خورده است
                if price_spans:
                    # قیمت فعلی
                    current_price_elem = price_spans[0].find("span", class_="a-offscreen")
                    if current_price_elem:
                        current_price = extract_price(current_price_elem.text)
                    
                    # به دنبال قیمت اصلی (خط خورده) می‌گردیم
                    original_price_elem = product.find("span", class_="a-price a-text-price")
                    if original_price_elem:
                        offscreen = original_price_elem.find("span", class_="a-offscreen")
                        if offscreen:
                            original_price = extract_price(offscreen.text)
                
                # اگر هر دو قیمت را پیدا کردیم، تخفیف را حساب می‌کنیم
                if current_price and original_price and original_price > current_price:
                    discount_percentage = ((original_price - current_price) / original_price) * 100
                    
                    # 🔴 شرط تخفیف: الان روی 0 تنظیم شده تا تست کنیم. بعد از تست آن را 50 کنید.
                    if discount_percentage > 0:
                        deals.append({
                            "name": name,
                            "category": category,
                            "current_price": f"AED {current_price:.2f}",
                            "original_price": f"AED {original_price:.2f}",
                            "discount": int(discount_percentage),
                            "url": product_url
                        })
                        
        except Exception as e:
            print(f"Error scraping {category}: {e}")
            
    return deals

