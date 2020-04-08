package main
import (
	"os"
	"log"
  "strings"
	"github.com/go-telegram-bot-api/telegram-bot-api"
  "strconv"
  "net/http"
)

var inlineButtonQuiz = tgbotapi.NewInlineKeyboardMarkup(
	tgbotapi.NewInlineKeyboardRow(
		tgbotapi.NewInlineKeyboardButtonURL("Give it a try","https://t.me/kaito_bot"),
	),
)

const IMAGE_PATH="image.png"

func quiz() {
	token := os.Getenv("TOKEN")
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
	
	channelid, err := strconv.ParseInt(os.Getenv("CHANNEL_ID"), 10, 64)

	photo := tgbotapi.NewPhotoUpload(channelid, IMAGE_PATH)
  photo.Caption = QUESTION + INSTRUCTION
  photo.ParseMode = tgbotapi.ModeHTML
	photo.ReplyMarkup = inlineButtonQuiz
  log.Printf("DOne")
  message, err := bot.Send(photo)
  log.Printf("Sent")

  for update := range updates {
    if update.Message == nil { // ignore any non-Message Updates
			continue
		}

    log.Printf("[%s] %s: %s", update.Message.From.UserName, update.Message.From.FirstName + update.Message.From.LastName, update.Message.Text)

    if (strings.ToUpper(update.Message.Text) == (COMMAND + ANSWER)) {
      text := QUESTION + REPLY_TEXT + update.Message.From.FirstName + update.Message.From.LastName
      msg := tgbotapi.NewEditMessageText(message.Chat.ID, message.MessageID, text)
      msg.ParseMode = tgbotapi.ModeHTML
      msg.DisableWebPagePreview = true
      bot.Send(msg)

      msgReply := tgbotapi.NewMessage(update.Message.Chat.ID, "That's correct. Don't steal too much u bitch.")
      msgReply.ReplyToMessageID = update.Message.MessageID
      bot.Send(msgReply)
      break

	  } else if strings.Contains(strings.ToUpper(update.Message.Text), COMMAND) {
	    msgReply := tgbotapi.NewMessage(update.Message.Chat.ID, "WRong dude")
	    msgReply.ReplyToMessageID = update.Message.MessageID
	    bot.Send(msgReply)
	  }
}
  log.Printf("Program end.")
}
