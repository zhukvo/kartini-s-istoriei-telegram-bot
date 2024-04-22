# Программа бот - Картины с историей - t.me/yandex_kartini_bot.
# Автор: Жук Владимир, 2024

import logging
import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import requests
from bs4 import BeautifulSoup


STORY, NEWSTORY, UPLOADPHOTO, SAVESTORY = range(4)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)



logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def decl(number: int, titles: list):
    cases = [ 2, 0, 1, 1, 1, 2 ]
    if 4 < number % 100 < 20:
        idx = 2
    elif number % 10 < 5:
        idx = cases[number % 10]
    else:
        idx = cases[5]

    return titles[idx]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Друзья, приветствую вас на моем познавательном телеграмм канале. Позвольте представиться - меня зовут Скалик. Я бот-искусствовед.\
 Вас ждут увлекательные рассказы о картинах и истории их создания. Подписывайтесь на мой канал.\n\n"
        "Отправь /story чтобы послушать мою новую историю.\n"
        "Отправь /newstory чтобы рассказать свою историю.\n"
        "Отправь /subscribe <minutes> чтобы подписаться на новые истории.\n"
        "Отправь /unsubscribe чтобы отписаться.",
    )

    return ConversationHandler.END

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Отправь /story чтобы послушать мою новую историю.\n"
        "Отправь /newstory чтобы рассказать свою историю.\n"
        "Отправь /subscribe <minutes> чтобы подписаться на новые истории.\n"
        "Отправь /unsubscribe чтобы отписаться.",
    )

    return ConversationHandler.END

def loadStories():
    url = 'https://kartinysistoriey.ru/page/3/'
    response = requests.get(url)
    html = response.text

    # Создание объекта BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Находим все элементы, содержащие микроразметку для BlogPosting
    posts = soup.find_all('div', {'itemtype': 'http://schema.org/BlogPosting'})

    # Массив для хранения результатов
    result = []

    # Перебираем найденные элементы с микроразметкой BlogPosting
    for post in posts:
        # Извлекаем заголовок (name), текст статьи (articleBody) и ссылку на изображение (image)
        caption = post.find(itemprop='name').text.strip() if post.find(itemprop='name') else ''
        articleBody = post.find(itemprop='articleBody').text.strip() if post.find(itemprop='articleBody') else ''
        
        # Для изображения используем атрибут src у тега img
        image_element = post.find(itemprop='image')
        imageUrl = image_element['src'] if image_element and 'src' in image_element.attrs else ''

        # извлекаем ссылку
        url = post.find('a', href=True)['href']

        # Добавляем данные в массив результатов
        result.append([
            imageUrl,
            caption,
            articleBody,
            url,
        ])

    return result

def findRandomStory():
    results = loadStories()
    return random.choice(results)


async def story(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Ask story from %s: %s", user.first_name, update.message.text)

    story_image, story_caption, story_text, story_url = findRandomStory()

    await update.message.reply_photo(story_image,
            caption=story_caption)   

    await update.message.reply_text(
        f"{story_text}... {story_url}",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END

async def addNewStory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Загрузи фото картины о которой ты хочешь рассказать",
        reply_markup=ReplyKeyboardRemove(),
    )
    return UPLOADPHOTO


async def uploadPhoto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()

    context.user_data["file_unique_id"] = photo_file.file_unique_id

    await photo_file.download_to_drive(f"user-stories/user-story-{photo_file.file_unique_id}.jpg")
    logger.info("Photo of %s: %s", user.first_name, f"user-stories/user-story-{photo_file.file_unique_id}.jpg")

    await update.message.reply_text(
        "Прекрасно! Теперь расскажи историю которую ты знаешь или отправь /skip если ты не хочешь этого делать."
    )

    return SAVESTORY


async def saveStory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    file_unique_id = context.user_data["file_unique_id"]

    logger.info("История от %s: %s", user.first_name, update.message.text)

    f = open(f"user-stories/user-story-{file_unique_id}.txt", "w", encoding='utf-8')
    f.write(update.message.text)
    await update.message.reply_text("Спасибо! Я записал. Надеюсь, я скоро услышу новую историю.")
    f.close()
    
    return ConversationHandler.END


async def skip_addNewStory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s cancel new story.", user.first_name)
    await update.message.reply_text(
        "До встречи! Надеюсь, я скоро услышу новую историю. Хорошего дня.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "До встречи! Хорошего дня.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        if len(context.args) > 0:
            due = int(context.args[0])
        else:
            due = 1  # by default every minute

        if due < 0:
            await update.effective_message.reply_text("Простите машина времени еще не изобретена!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due * 60, chat_id=chat_id, name=str(chat_id), data=due)

        sMinutes = decl(due, ["минуту", "минуты", "минут"])
        sWord = decl(due, ["каждую", "каждые", "каждые"])
        text = f"Я буду отправлять вам новую историю {sWord} {due} {sMinutes}!"

        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /subscribe <minutes>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Автоматические истории отменены!" 
    await update.message.reply_text(text)


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job

    logger.info(f"Alarm! {job.data} minutes are over!")
    
    #await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

    story_image, story_caption, story_text, story_url = findRandomStory()

    await context.bot.send_photo(job.chat_id, story_image, caption=story_caption)   

    await context.bot.send_message(job.chat_id, f"{story_text}... {story_url}")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("story", story))
    application.add_handler(CommandHandler("subscribe", set_timer))
    application.add_handler(CommandHandler("unsubscribe", unset))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("newstory", addNewStory)],
        states={
            NEWSTORY: [CommandHandler("newstory", addNewStory), CommandHandler("skip", skip_addNewStory)],
            UPLOADPHOTO: [MessageHandler(filters.PHOTO & ~filters.COMMAND, uploadPhoto), CommandHandler("skip", skip_addNewStory)],
            SAVESTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, saveStory), CommandHandler("skip", skip_addNewStory)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()