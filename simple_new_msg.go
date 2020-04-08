package main

import (
	"log"
	"net/http"
	"os"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"
)

func simple_new_msg() {
	token := os.Getenv("TOKEN")
  myUsername := os.Getenv("MY_USERNAME")
  channelName := os.Getenv("CHANNEL_NAME")

	bot, err := tgbotapi.NewBotAPI(token)
	if err != nil {
		log.Fatal(err)
	}
	//bot.Debug = true
	log.Printf("Authorized on account %s", bot.Self.UserName)

	_, err = bot.SetWebhook(tgbotapi.NewWebhook("https://System-logger-bot.kaitojjj.repl.co:443/"))
	if err != nil {
		log.Fatal(err)
	}
	info, err := bot.GetWebhookInfo()
	if err != nil {
		log.Fatal(err)
	}
	if info.LastErrorDate != 0 {
		log.Printf("Telegram callback failed: %s", info.LastErrorMessage)
	}
	updates := bot.ListenForWebhook("/")
	go http.ListenAndServe("0.0.0.0:8443", nil)

	for update := range updates {
	  if update.Message == nil { // ignore any non-Message Updates
			continue
	  }
    log.Printf("[%s] %s", update.Message.From.UserName, update.Message.Text)
    if update.Message.From.UserName == myUsername {
      log.Printf("That's meeeeee")
      msg := tgbotapi.NewMessageToChannel(channelName, update.Message.Text)
      bot.Send(msg)
      log.Printf("Senttt")
    }
	}
}