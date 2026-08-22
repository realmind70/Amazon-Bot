import asyncio
from telegram import Bot
from scraper import scrape_amazon_uae
from db_manager import initialize_db, add_sent_product, is_product_sent

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

async def send_telegram_message(bot: Bot, message_text: str):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message_text, parse_mode='HTML', disable_web_page_preview=False)
        print("✅ پیام با موفقیت به تلگرام ارسال شد!")
    except Exception as e:
        print(f"❌ خطا در ارسال پیام تلگرام: {e}")

async def main():
    print("شروع جستجوی آمازون در سرور گیت‌هاب...")
    initialize_db()
    bot = Bot(token=BOT_TOKEN)
    
    deals = scrape_amazon_uae()
    new_deals_found = 0
    
    for deal in deals:
        product_id = deal['url'].split('?')[0]
        if not is_product_sent(product_id):
            message = (
                f"🚨 <b>New Deal ({deal['category']})</b> 🚨\n\n"
                f"🛍 <b>Product:</b> {deal['name'][:60]}...\n\n"
                f"🔥 <b>Discount:</b> {deal['discount']}% OFF\n"
                f"💰 <b>Current Price:</b> {deal['current_price']}\n"
                f"❌ <b>Original Price:</b> <s>{deal['original_price']}</s>\n\n"
                f"🔗 <a href='{deal['url']}'>Direct Amazon Link</a>"
            )
            await send_telegram_message(bot, message)
            add_sent_product(product_id)
            new_deals_found += 1
            await asyncio.sleep(2) 

    if new_deals_found == 0:
        print("تخفیف جدیدی یافت نشد.")
    else:
        print(f"{new_deals_found} پیام با موفقیت ارسال شد.")

if __name__ == "__main__":
    asyncio.run(main())
