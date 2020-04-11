package main
import (
	"os"
	"log"
  "strings"
	"github.com/go-telegram-bot-api/telegram-bot-api"
  "strconv"
)

var inlineButtonQuiz = tgbotapi.NewInlineKeyboardMarkup(
	tgbotapi.NewInlineKeyboardRow(
		tgbotapi.NewInlineKeyboardButtonURL("Give it a try","https://t.me/system_logger_bot"),
	),
)

const IMAGE_PATH="Resources/image.png"

func quiz() {
	bot := authorization()
	//bot.Debug = true
	updates := configure_webhook(bot)
	
	channelid, _ := strconv.ParseInt(os.Getenv("CHANNEL_ID"), 10, 64)

	photo := tgbotapi.NewPhotoUpload(channelid, IMAGE_PATH)
  photo.Caption = QUESTION + INSTRUCTION
  photo.ParseMode = tgbotapi.ModeHTML
	photo.ReplyMarkup = inlineButtonQuiz
  log.Printf("DOne")
  message, _ := bot.Send(photo)
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
