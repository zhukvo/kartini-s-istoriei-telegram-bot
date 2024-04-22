Программа бот - Картины с историей - t.me/yandex_kartini_bot
Автор: Жук Владимир, 2024. Проект в рамках Yandex.Лицей.

![image](https://github.com/zhukvo/kartini-s-istoriei-telegram-bot/assets/155824263/e6ee89f9-9f05-41a6-a1b3-f6792186b54c)

## Описание:

Друзья, приветствую вас на моем познавательном Телеграм канале.

Позвольте представиться - меня зовут Скалик. 

Я бот-искусствовед. Вас ждут увлекательные рассказы о картинах и истории их создания. Подписывайтесь на мой канал.

## Сценарии
* Отправь /story чтобы послушать мою новую историю.
* Отправь /newstory чтобы рассказать свою историю.
* Отправь /subscribe <minutes> чтобы подписаться на новые истории.
* Отправь /unsubscribe чтобы отписаться.
* Отправь /help чтобы получить подскажку

## Демонстрация
![Демо](demo.gif)

## Презентация
[Скачать презентацию](bot.pptx)

## Установка и запуск:

Перед запуском надо:
1. Установить необходимые пакеты:
    * pip install BeautifulSoup4
    * pip install python-telegram-bot
    * pip install python-telegram-bot[job-queue]
2. Получить и прописать Token. 
3. For a description of the Bot API, see this page: https://core.telegram.org/bots/api

## Программа содержит:
1) Файла "requirements.txt";
2) Работу с контекстом пользователя;
3) Загрузку и использование медиафайлов; Пользовательские фото и истории сохраняются в папке user-stories с уникальными именами.
4) Использование стороннего API. Данные для программы загружаются c сайта  https://kartinysistoriey.ru
