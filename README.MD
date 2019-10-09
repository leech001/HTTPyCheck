# The Python HTTP(S) - PING check availability sites over Telegram bot project

Python script for checking and monitoring nodes through HTTP and HTTPS requests to nodes with a response code check other than '200'. There is also an additional check of nodes via PING (ICMP).

## Install and config
- Download the required repository;

```bash
$ git clone https://github.com/leech001/HTTPyCheck.git
```

- Change dir to HTTPyCheck/telegram_bot/application/ and edit config.yaml file;

```yaml
    main:
        delay: 30   #time to rechecking hosts

    telegram:
      token: 244516775:AAGZп55654ASsFFpbjyNA9su6gQU-Qs  #T oken for you Telegram BOT
      group: 123456     # Telegram you ID or group ID 
      proxy:
        proxy_url: socks5://xxx.xxx.org:4108/   # Address proxy server for Telegram (специально Роскомнадзора)
        username: user  # proxy user
        password: pass  # proxy pass

    http:
      BasicAuth:
        username: user  # user for basic auth if hosta need
        password: pass  # pass for basic auth if hosta need
      sites:
        - http://example.com/   # hosts for monitoring over HTTP or HTTPS
        - https://example2.com/
      auth_sites:
        - http://example.com/   # hosts for monitoring over HTTP or HTTPS with basic auth

    icmp:
      timeout: 4        # time out for ping error status (sec)
      timedelay: 100    # time delay for ping warning status (ms) 
    
      hosts:
        - google.com    # hosts for monitoring over ICMP
```

## Run
- Change dir to /HTTPyCheck and run docker container;
```bash
    $ sudo docker-compose up -d
```