# Python HTTP(S) check availability sites script over Telegram bot

## Python script to monitor the availability of HTTP (S) nodes through the return code 200 C notification via Telegram bot.
(Python скрипт для мониторинга доступности HTTP(S) узлов через возврат кода 200 c уведомлением через Telegram бота.)

## Install (Установка)
1. Скачайте необходимый репозиторий.
2. Модифицируйте под ствои нужнды.
3. Запустите командой sudo docker-compose up -d

##Main settings (Основные настройки)
Вводим токен telegram бота
token = 'TOKEN'

По необходимости реквизиты SOCKS5 сервера
REQUEST_KWARGS = {
    'proxy_url': 'socks5://proxy.server.org:41000/',
    'urllib3_proxy_kwargs': {
        'username': 'user',
        'password': 'pass',
    }
}

Идентификатор группы для уведомлений
telegram_group = -1111111

Перечень сайтов для мониторинга
sites = {'http://xxx.ru/',
         'https://yyy.ru/ru_RU/'
         }

Перечень сайтов для мониторинга с аутентификацией
auth_sites = {'http://zzz.ru:88'
              }

Реквизиты аутентификации
auth=aiohttp.BasicAuth('user', 'pass')

Период мониторинга в сек.
await asyncio.sleep(30)

