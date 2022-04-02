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
                updater.bot.send_message(chat_id=config['telegram']['group'],
                                         text=f'Узел {site} в статусе HTTP ' + str(resp.status))
            print(site, resp.status)
    except Exception as error:
        print('Request failed:', error)
        return 1


async def get_host(host):
    if 'username' in host and host['username'] is not None and host['password'] is not None:
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(
                host['username'],
                host['password'])) as session:
            return await fetch(session, host['site'])
    else:
        async with aiohttp.ClientSession() as session:
            return await fetch(session, host['site'])


async def check_http():
    while True:
        for host in config['http']['sites']:
            error_count = 0
            if await get_host(host) is not None:
                for repeat in range(config['http']['repeat'] - 1):
                    if await get_host(host) is not None:
                        error_count += 1
                if error_count == config['http']['repeat'] - 1:
                    updater.bot.send_message(chat_id=config['telegram']['group'],
                                             text=f'Узел {host["site"]} не доступен')
        await asyncio.sleep(config['main']['repeat_period'])


async def check_icmp():
    while True:
        for host in config['icmp']['hosts']:
            req = ping(host, config['icmp']['timeout'], unit='ms')
            if req is None:
                updater.bot.send_message(chat_id=config['telegram']['group'], text=f'Узел {host} с ошибкой ICMP')
            elif req > config['icmp']['timedelay']:
                updater.bot.send_message(chat_id=config['telegram']['group'],
                                         text=f'Узел {host} с задержкой ICMP= ' + str(req))
        await asyncio.sleep(config['main']['delay'])


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Привет, я бот мониторинга! Ваш (группы) идентификатор = "
                                  + str(update.message.chat_id))


def list_group(update, context):
    message = 'На мониторинге следующие сайты (HTTP):\n'
    if config['http']['sites'] is not None:
        for host in config['http']['sites']:
            if isinstance(host, dict):
                message = message + str(host['site']) + '\n'
            else:
                message = message + str(host) + '\n'
    message = message +'\nНа мониторинге следующие ресурсы (ICMP):\n'
    if config['icmp']['hosts'] is not None:
        for host in config['icmp']['hosts']:
            message = message + str(host) + '\n'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('list', list_group))
updater.start_polling()

try:
    if config['http']['sites'] is not None:
        asyncio.run(check_http())
    if config['icmp']['hosts'] is not None:
        asyncio.run(check_icmp())
except Exception as e:
    print(f"Error: [Exception] {type(e).__name__}: {e}")
