from telegram.ext import Updater
from telegram.ext import CommandHandler
import asyncio
import aiohttp

# Вводим токен telegram бота
token = 'TOKEN'

# По необходимости реквизиты SOCKS5 сервера
REQUEST_KWARGS = {
    'proxy_url': 'socks5://proxy.server.org:41000/',
    'urllib3_proxy_kwargs': {
        'username': 'user',
        'password': 'pass',
    }
}

updater = Updater(token=token, use_context=True, request_kwargs=REQUEST_KWARGS)
dispatcher = updater.dispatcher

# Идентификатор группы для уведомлений
telegram_group = -1111111

# Перечень сайтов для мониторинга
sites = {'http://xxx.ru/',
         'https://yyy.ru/ru_RU/'
         }

# Перечень сайтов для мониторинга с аутентификацией
auth_sites = {'http://zzz.ru:88'
              }


async def fetch(session, site):
    try:
        async with session.get(site, ssl=False) as resp:
            if resp.status != 200:
                updater.bot.send_message(chat_id=telegram_group, text='Узел %s в статусе ' % site + str(resp.status))
            print(site, resp.status)
    except Exception as e:
        print('Request failed:', e)
        updater.bot.send_message(chat_id=telegram_group, text='Узел %s с ошибкой ' % site + str(e))


async def check_sites():
    while True:
        for site in sites:
            async with aiohttp.ClientSession() as session:
                await fetch(session, site)

        for site in auth_sites:
            async with aiohttp.ClientSession(auth=aiohttp.BasicAuth('user', 'pass')) as session:  # Реквизиты аутентификации
                await fetch(session, site)
        print(' ')
        await asyncio.sleep(30)  # Период мониторинга в сек.


def start(update, context):
    print(update.message.chat_id)
    message = 'Привет, я бот мониторинга' + '\n' + \
              'на мониторинге следующие ресурсы:' + '\n'
    for site in sites:
        message = message + str(site) + '\n'
    for site in sites:
        message = message + str(site) + '\n'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


dispatcher.add_handler(CommandHandler('start', start))
updater.start_polling()

try:
    loop = asyncio.get_event_loop()
    loop.create_task(check_sites())

    loop.run_forever()
except Exception as e:
    print("Error: [Exception] %s: %s" % (type(e).__name__, e))
