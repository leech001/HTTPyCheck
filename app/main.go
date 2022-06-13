package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/go-ping/ping"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"gopkg.in/yaml.v3"
)

type Config struct {
	App struct {
		RepeatPeriod uint16 `yaml:"repeat_period"`
	}
	Telegram struct {
		Token string
		Group int64
	}
	Http struct {
		Repeat  uint8
		Timeout uint8
		Sites   []struct {
			Url      string
			Elements []string
		}
	}
	Icmp struct {
		Count     uint8
		Update    uint16
		Timeout   uint8
		Timedelay uint16
		Hosts     []string
	}
}

func main() {
	// Read config from yaml
	config := Config{}
	filename, _ := filepath.Abs("./config.yaml")
	yamlFile, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	// Parse yaml
	err = yaml.Unmarshal(yamlFile, &config)
	if err != nil {
		log.Fatalf("error: %v", err)
	}

	// Telegram bot
	bot, err := tgbotapi.NewBotAPI(config.Telegram.Token)
	if err != nil {
		panic(err)
	}
	go botUpdate(bot, config.Http.Sites, config.Icmp.Hosts)
	bot.Debug = true

	// Running ICMP checker
	for _, host := range config.Icmp.Hosts {
		go pinger(bot, config.Telegram.Group, host, config.Icmp.Count, config.Icmp.Update, config.Icmp.Timeout, config.Icmp.Timedelay)
	}

	// TODO Running HTTP checker

	// Loop
	for {
		time.Sleep(1 * time.Second)
	}

}

func pinger(bot *tgbotapi.BotAPI, group int64, host string, count uint8, update uint16, timeout uint8, timedelay uint16) {
	fmt.Println(host)
	pinger, err := ping.NewPinger(host)
	if err != nil {
		panic(err)
	}
	pinger.Count = int(count)
	pinger.Timeout = 60 * time.Second
	for {
		err = pinger.Run()
		if err != nil {
			panic(err)
		}
		stats := pinger.Statistics()

		if stats.MaxRtt.Seconds() > float64(timeout) {
			msg := tgbotapi.NewMessage(group, "Host "+host+" ICMP error")
			bot.Send(msg)
		} else if stats.MaxRtt.Milliseconds() > int64(timedelay) {
			msg := tgbotapi.NewMessage(group, "Host "+host+" ICMP delay is "+stats.MaxRtt.String())
			bot.Send(msg)
		}
		// fmt.Println(stats)
		time.Sleep(time.Duration(update) * time.Second)
	}
}

func botUpdate(bot *tgbotapi.BotAPI, sites []struct {
	Url      string
	Elements []string
}, hosts []string) {

	// Create string for HTTP(s) monitoring sites
	sitesString := ""
	for _, site := range sites {
		sitesString += site.Url + "\n"
	}

	// Create string for ICMP monitoring hosts
	hostsString := strings.Join(hosts[:], "\n")

	// Telegram bot listener
	u := tgbotapi.NewUpdate(0)
	u.Timeout = 300
	updates := bot.GetUpdatesChan(u)

	for update := range updates {
		if update.Message == nil { // ignore any non-Message updates
			continue
		}

		if !update.Message.IsCommand() { // ignore any non-command Messages
			continue
		}
		msg := tgbotapi.NewMessage(update.Message.Chat.ID, "")

		switch update.Message.Command() {
		case "start":
			msg.Text = "Hi, I am a monitoring bot! Your (group) ID = " + strconv.FormatInt(update.Message.Chat.ID, 10)
		case "list":
			msg.Text = "HTTP(s) monitoring sites:\n" + sitesString + "\nICMP monitoring hosts:\n" + hostsString
		default:
			msg.Text = "I don't know that command"
		}

		if _, err := bot.Send(msg); err != nil {
			log.Panic(err)
		}
	}
}
