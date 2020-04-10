package main

import (
	"log"
	"net/http"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"
)

func configure_webhook(bot tgbotapi.BotAPI) tgbotapi.UpdatesChannel{
  _, err := bot.SetWebhook(tgbotapi.NewWebhook("https://System-logger-bot--kaitojjj.repl.co:443/"))
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
  return updates
}
