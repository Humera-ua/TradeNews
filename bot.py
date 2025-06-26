import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import ccxt # <-- Нова бібліотека для отримання цін

# --- Налаштування API та константи ---
# ВАЖЛИВО: Отримайте свій безкоштовний ключ на https://min-api.cryptocompare.com/pricing
CRYPTOCOMPARE_API_KEY = os.environ.get('CRYPTOCOMPARE_API_KEY', 'YOUR_API_KEY_HERE')

# --- Функції-помічники для отримання даних ---

def fetch_price_data(symbol):
    """Отримує дані про ціну з біржі Binance за допомогою ccxt."""
    try:
        exchange = ccxt.binance()
        # Формуємо пару, зазвичай це символ до USDT
        ticker = f'{symbol.upper()}/USDT'
        data = exchange.fetch_ticker(ticker)
        return {
            "price": data['last'],
            "change_24h": data['percentage']
        }
    except (ccxt.BadSymbol, ccxt.NetworkError, Exception) as e:
        print(f"Помилка отримання ціни для {symbol}: {e}")
        return None

def fetch_latest_news():
    """Отримує останні новини з CryptoCompare API."""
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/news/?lang=EN&api_key={CRYPTOCOMPARE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status() # Перевірка на HTTP помилки
        news_data = response.json()['Data']
        # Повертаємо 3 останні новини
        return news_data[:3]
    except (requests.RequestException, KeyError) as e:
        print(f"Помилка отримання новин: {e}")
        return None

def fetch_fear_and_greed_index():
    """Отримує індекс страху та жадібності."""
    try:
        # API від alternative.me, повертає 1 останнє значення
        url = "https://api.alternative.me/fng/?limit=1"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data'][0]
        return {
            "value": data['value'],
            "classification": data['value_classification']
        }
    except (requests.RequestException, KeyError) as e:
        print(f"Помилка отримання індексу страху та жадібності: {e}")
        return None

# --- Оновлені функції для команд ---

def start(update, context):
    """Відправляє вітальне повідомлення при команді /start."""
    welcome_text = (
        "Вітаю! Я ваш персональний крипто-трейдер бот.\n"
        "Я аналізую ринкові дані в реальному часі, щоб надавати вам актуальну інформацію.\n\n"
        "*Основні команди:*\n"
        "/price `BTC` - Дізнатись ціну (напр. /price ETH, /price SOL).\n"
        "/news - Отримати 3 останні новини ринку.\n"
        "/digest - Отримати аналітичний дайджест ринку.\n"
    )
    update.message.reply_text(welcome_text, parse_mode=telegram.ParseMode.MARKDOWN)

def get_news(update, context):
    """Відправляє добірку реальних новин."""
    update.message.reply_text("⏳ *Шукаю свіжі новини...*")
    news_items = fetch_latest_news()

    if not news_items:
        update.message.reply_text("❌ Не вдалося завантажити новини. Спробуйте пізніше.")
        return

    formatted_news = []
    for item in news_items:
        formatted_news.append(f"📰 *{item['title']}*\n[Читати далі]({item['url']})")

    update.message.reply_text("\n\n".join(formatted_news), parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)

def get_price(update, context):
    """Відправляє реальну ціну для вказаної криптовалюти."""
    if not context.args:
        update.message.reply_text("Будь ласка, вкажіть символ криптовалюти.\n*Приклад:* `/price BTC`", parse_mode=telegram.ParseMode.MARKDOWN)
        return

    symbol = context.args[0].upper()
    update.message.reply_text(f"⏳ *Запитую ціну для {symbol}...*")
    price_data = fetch_price_data(symbol)

    if not price_data:
        update.message.reply_text(f"❌ Не вдалося знайти дані для *{symbol}*. Перевірте символ або спробуйте інший (напр. ETH, SOL, DOGE).", parse_mode=telegram.ParseMode.MARKDOWN)
        return

    price = price_data['price']
    change = price_data['change_24h']
    sign = "📈" if change >= 0 else "📉"
    
    message = f"*{symbol}/USDT*\n\n*Ціна:* `${price:,.4f}`\n*Зміна за 24г:* {sign} `{change:.2f}%`"
    update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)

def get_digest(update, context):
    """Відправляє аналітичний дайджест на основі реальних даних."""
    update.message.reply_text("⏳ *Аналізую ринок та готую дайджест...*")
    
    # 1. Отримуємо дані
    btc_data = fetch_price_data("BTC")
    fng_data = fetch_fear_and_greed_index()
    news_data = fetch_latest_news()

    # 2. Формуємо текст дайджесту
    digest_parts = ["*📊 Щоденний аналітичний дайджест:*"]

    # Блок про Bitcoin
    if btc_data:
        sign = "📈" if btc_data['change_24h'] >= 0 else "📉"
        btc_part = (
            f"\n*Головний актив (BTC):*\n"
            f"Ціна: `${btc_data['price']:,.2f}`\n"
            f"Зміна за 24г: {sign} `{btc_data['change_24h']:.2f}%`"
        )
        digest_parts.append(btc_part)

    # Блок про настрої ринку
    if fng_data:
        fng_part = (
            f"\n*Настрої ринку (Індекс страху та жадібності):*\n"
            f"Значення: *{fng_data['value']}* з 100\n"
            f"Оцінка: *{fng_data['classification']}*"
        )
        digest_parts.append(fng_part)

    # Блок з ключовою новиною
    if news_data:
        top_news = news_data[0]
        news_part = f"\n*Ключова новина:*\n[{top_news['title']}]({top_news['url']})"
        digest_parts.append(news_part)

    # 3. Відправляємо повідомлення
    if len(digest_parts) == 1: # Якщо жодні дані не завантажились
        update.message.reply_text("❌ Не вдалося зібрати дані для дайджесту. Спробуйте пізніше.")
    else:
        update.message.reply_text("\n".join(digest_parts), parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)


def unknown(update, context):
    """Обробка невідомих команд."""
    update.message.reply_text("Вибачте, я не зрозумів цю команду. Натисніть /start, щоб побачити список доступних команд.")

# --- Основна логіка бота ---

def main():
    """Запуск бота."""
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        print("Помилка: Не знайдено TELEGRAM_TOKEN.")
        return
    
    if CRYPTOCOMPARE_API_KEY == 'YOUR_API_KEY_HERE':
        print("УВАГА: Не знайдено CRYPTOCOMPARE_API_KEY. Функції новин та дайджесту можуть не працювати.")
        print("Отримайте ключ на https://min-api.cryptocompare.com та додайте його.")


    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("news", get_news))
    dp.add_handler(CommandHandler("price", get_price))
    dp.add_handler(CommandHandler("digest", get_digest))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    print("Бот запущено з динамічними даними...")
    updater.idle()

if __name__ == '__main__':
    main()
