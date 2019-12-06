import asyncio
import aiohttp
import yaml
from telegram.ext import Updater
from telegram.ext import CommandHandler
from ping3 import ping

with open("config.yaml", 'r') as yamlfile:
    config = yaml.safe_load(yamlfile)

telegram_group = config['telegram']['group']
http_timeout = aiohttp.ClientTimeout(total=config['http']['timeout'])

if isinstance(config['telegram']['proxy'], dict):
    REQUEST_KWARGS = {'proxy_url': config['telegram']['proxy']['proxy_url'],
                      'urllib3_proxy_kwargs': {
                      'username': config['telegram']['proxy']['username'],
                      'password': config['telegram']['proxy']['password'],
                       }
                      }
    updater = Updater(token=config['telegram']['token'], use_context=True, request_kwargs=REQUEST_KWARGS)
else:
    updater = Updater(token=config['telegram']['token'], use_context=True)
dispatcher = updater.dispatcher


async def fetch(session, site):
    try:
        async with session.get(site, timeout=http_timeout, ssl=False) as resp:
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
            if 'username' in host and host['username'] is not None and host['password'] is not None:
                async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(
                        host['username'],
                        host['password'])) as session:
                    await fetch(session, host['site'])
            else:
                async with aiohttp.ClientSession() as session:
                    await fetch(session, host['site'])
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
            if isinstance(host, dict):
                message = message + str(host['site']) + '\n'
            else:
                message = message + str(host) + '\n'

    if config['icmp']['hosts'] is not None:
        for host in config['icmp']['hosts']:
            message = message + str(host) + '\n'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('list', list_group))
updater.start_polling()

try:
    loop = asyncio.get_event_loop()
    if config['http']['sites'] is not None:
        loop.create_task(check_http())
    if config['icmp']['hosts'] is not None:
        loop.create_task(check_icmp())
    loop.run_forever()
except Exception as e:
    print("Error: [Exception] %s: %s" % (type(e).__name__, e))