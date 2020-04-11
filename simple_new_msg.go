package main

import (
	"log"
	"os"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api"
)

func simple_new_msg() {
	
  myUsername := os.Getenv("MY_USERNAME")
  channelName := os.Getenv("CHANNEL_NAME")

	bot := authorization()
	//bot.Debug = true
	updates := configure_webhook(bot)

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