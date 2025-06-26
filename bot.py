import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests

# --- Функції для команд ---

def start(update, context):
    """Відправляє вітальне повідомлення при команді /start."""
    welcome_text = (
        "Вітаю! Я ваш персональний крипто-трейдер бот. "
        "Я допоможу вам бути в курсі останніх новин та ринкових тенденцій.\n\n"
        "Доступні команди:\n"
        "/news - Отримати останні новини криптовалют.\n"
        "/price <СИМВОЛ> - Дізнатись ціну (напр. /price BTC).\n"
        "/digest - Отримати короткий аналітичний дайджест ринку.\n"
    )
    update.message.reply_text(welcome_text)

def get_news(update, context):
    """Відправляє добірку новин."""
    # У реальному боті тут буде код для парсингу новин з сайтів або через API
    # Зараз для прикладу використаємо статичні дані
    news_headlines = [
        "📈 *Аналіз цін:* Бики BTC готуються до ривка вище $85,000, що може потягнути за собою альткоїни.",
        "📉 *Корекція ринку:* Аналітики вважають поточне падіння ціни Bitcoin тимчасовим 'струсом' перед наступним етапом зростання.",
        "🇪🇺 *Регуляція:* ЄС продовжує обговорення нових правил для крипто-компаній, що може вплинути на ринок в середньостроковій перспективі.",
        "💰 *Інституціонали:* Goldman Sachs тримає понад $400 млн у біткоїн-ETF, що свідчить про зростаючу довіру великих гравців."
    ]
    update.message.reply_text("📰 *Останні новини ринку:*\n\n" + "\n\n".join(news_headlines), parse_mode=telegram.ParseMode.MARKDOWN)

def get_price(update, context):
    """Відправляє ціну для вказаної криптовалюти."""
    try:
        symbol = context.args[0].upper()
        # У реальному боті тут буде запит до API (наприклад, CoinGecko, Binance)
        # Імітуємо відповідь API
        if symbol == 'BTC':
            price = "61,543.21"
            change = "+1.25%"
        elif symbol == 'ETH':
            price = "2,015.89"
            change = "-0.5%"
        else:
            update.message.reply_text(f"Вибачте, я поки не відстежую {symbol}.")
            return

        message = f"Ціна для *{symbol}*:\n\n*Ціна:* ${price}\n*Зміна за 24г:* {change}"
        update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)

    except (IndexError, ValueError):
        update.message.reply_text("Будь ласка, вкажіть символ криптовалюти після команди. \n*Приклад:* /price BTC", parse_mode=telegram.ParseMode.MARKDOWN)

def get_digest(update, context):
    """Відправляє короткий аналітичний дайджест."""
    digest_text = (
        "📊 *Щоденний дайджест ринку:*\n\n"
        "Ринок демонструє ознаки консолідації після недавньої волатильності. Bitcoin утримує ключовий рівень підтримки, що є позитивним сигналом. "
        "Увага інвесторів прикута до майбутнього засідання ФРС, рішення якого може суттєво вплинути на ціну. "
        "Альткоїни слідують за динамікою BTC, але деякі проєкти в секторі GameFi, як-от TON, показують незалежне зростання на тлі позитивних новин."
    )
    update.message.reply_text(digest_text, parse_mode=telegram.ParseMode.MARKDOWN)

def unknown(update, context):
    """Обробка невідомих команд."""
    update.message.reply_text("Вибачте, я не зрозумів цю команду. Спробуйте /start, щоб побачити список доступних команд.")

# --- Основна логіка бота ---

def main():
    """Запуск бота."""
    # Отримання токену з системних змінних для безпеки
    token = os.environ.get('TELEGRAM_TOKEN')
    if not token:
        print("Помилка: Не знайдено TELEGRAM_TOKEN. Переконайтесь, що ви його додали.")
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    # Реєстрація обробників команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("news", get_news))
    dp.add_handler(CommandHandler("price", get_price))
    dp.add_handler(CommandHandler("digest", get_digest))

    # Обробник для невідомих команд
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Запуск бота
    updater.start_polling()
    print("Бот запущено...")
    updater.idle()

if __name__ == '__main__':
    main()
