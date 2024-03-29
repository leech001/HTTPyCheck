# Warning! Repository is deprecated please use the updated to GOLANG version [telegram-site-monitor](https://github.com/leech001/telegram-site-monitor)

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
        repeat_period: 30   #time to rechecking hosts (sec)

    telegram:
      token: 244516775:AAGZп55654ASsFFpbjyNA9su6gQU-Qs  #Token for you Telegram BOT
      group: 123456     # Telegram you ID or group ID (use command for BOT /start
      proxy:

Delete this block if proxy not use
#####
        proxy_url: socks5://xxx.xxx.org:4108/ # Address proxy server for Telegram (специально для Роскомнадзора)
        username: user  # proxy user
        password: pass  # proxy pass
#####

    http:
      repeat: 5   # number of rechecks
      timeout: 1  # HTTP(s) timeout (sec) 
      sites:
        - site: http://example.com/   # hosts for monitoring over HTTP or HTTPS with basic auth
          username: user  # user for basic auth if hosts need
          password: pass  # pass for basic auth if hosts need
        - site: https://example1.com/ # hosts for monitoring over HTTP or HTTPS

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

## Telegram BOT command
```
/start  # Print you ID or group ID need you for config
/list   # Print monitoring hosts
```
