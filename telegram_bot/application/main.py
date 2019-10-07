import asyncio
import aiohttp
import yaml
from telegram.ext import Updater
from telegram.ext import CommandHandler
from ping3 import ping

with open("config.yaml", 'r') as yamlfile:
    config = yaml.safe_load(yamlfile)

telegram_group = config['telegram']['group']

REQUEST_KWARGS = {
    'proxy_url': config['telegram']['proxy']['proxy_url'],
    'urllib3_proxy_kwargs': {
        'username': config['telegram']['proxy']['username'],
        'password': config['telegram']['proxy']['password'],
    }
}

updater = Updater(token=config['telegram']['token'], use_context=True, request_kwargs=REQUEST_KWARGS)
dispatcher = updater.dispatcher


async def fetch(session, site):
    try:
        async with session.get(site, ssl=False) as resp:
            if resp.status != 200:
                updater.bot.send_message(chat_id=config['telegram']['group'], text='Узел %s в статусе HTTP ' % site + str(resp.status))
            print(site, resp.status)
    except Exception as e:
        print('Request failed:', e)
        updater.bot.send_message(chat_id=config['telegram']['group'], text='Узел %s с ошибкой ' % site + str(e))
        # body = await resp.text()
        # print(body)


async def check_http():
    while True:
        for host in config['http']['sites']:
            async with aiohttp.ClientSession() as session:
                await fetch(session, host)
        print(' ')
        await asyncio.sleep(config['main']['delay'])


async def check_auth_http():
    while True:
        for host in config['http']['auth_sites']:
            async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(
                    config['http']['BasicAuth']['username'],
                    config['http']['BasicAuth']['password'])) as session:
                await fetch(session, host)
        print(' ')
        await asyncio.sleep(config['main']['delay'])


async def check_icmp():
    while True:
        for host in config['icmp']['hosts']:
            req = ping(host, config['icmp']['timeout'], unit='ms')
            if req is None:
                updater.bot.send_message(chat_id=config['telegram']['group'], text='Узел %s с ошибкой ICMP ' % host)
            elif req > config['icmp']['timedelay']:
                updater.bot.send_message(chat_id=config['telegram']['group'], text='Узел %s с задержкой ICMP= ' % host + str(req))
        await asyncio.sleep(config['main']['delay'])


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Привет, я бот мониторинга! Ваш (группы) идентификатор = "
                                  + str(update.message.chat_id))


def list_group(update, context):
    message = 'На мониторинге следующие ресурсы:' + '\n'
    if config['http']['sites'] is not None:
        for host in config['http']['sites']:
            message = message + str(host) + '\n'

    if config['http']['auth_sites'] is not None:
        for host in config['http']['auth_sites']:
            message = message + str(host) + '\n'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('list', list_group))
updater.start_polling()

try:
    loop = asyncio.get_event_loop()
    if config['http']['sites'] is not None:
        loop.create_task(check_http())
    if config['http']['auth_sites'] is not None:
        loop.create_task(check_auth_http())
    if config['icmp']['hosts'] is not None:
        loop.create_task(check_icmp())
    loop.run_forever()
except Exception as e:
    print("Error: [Exception] %s: %s" % (type(e).__name__, e))