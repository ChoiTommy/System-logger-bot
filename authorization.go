package main

import(
  "os"
  "log"
  tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"
)

func authorization() (tgbotapi.BotAPI){
  token := os.Getenv("TOKEN")
	bot, err := tgbotapi.NewBotAPI(token)
	if err != nil {
		log.Fatal(err)
	} else {
    log.Printf("Authorized on account %s", bot.Self.UserName)
  }
  return *bot
}