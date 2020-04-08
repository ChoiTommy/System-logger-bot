package main
/*
 * https://godoc.org/github.com/go-telegram-bot-api/telegram-bot-api
 * https://stackoverflow.com/questions/49826038/how-to-add-variable-to-string-variable-in-golang
 * https://gobyexample.com/random-numbers
 */
import (
	"log"
  "strings"
  "net/http"
	"github.com/go-telegram-bot-api/telegram-bot-api"
  "os"
)

var inlineButton_Reply = tgbotapi.NewInlineKeyboardMarkup(
	tgbotapi.NewInlineKeyboardRow(
		tgbotapi.NewInlineKeyboardButtonURL("Join discussion","https://t.me/kaito_bot"),
	),
)

func main_reply() {
  CHANNEL_NAME := os.Getenv("CHANNEL_NAME")
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

  messageText := QUESTION_REPLY + INSTRUCTION_REPLY
  msg := tgbotapi.NewMessageToChannel(CHANNEL_NAME, messageText)
  msg.ParseMode = tgbotapi.ModeHTML
  msg.ReplyMarkup = inlineButton_Reply
  message, err := bot.Send(msg)
  log.Printf("Sent")

  counter := 0
  messageText = messageText + DIVIDE_LINE_REPLY

  for update := range updates {
    if update.Message == nil { // ignore any non-Message Updates
			continue
		}

    log.Printf("[%s] %s: %s", update.Message.From.UserName, update.Message.From.FirstName + update.Message.From.LastName, update.Message.Text)

    if update.Message.IsCommand() {
			switch update.Message.Command() {
			case "ans":
        text := "<b>" + update.Message.From.FirstName + update.Message.From.LastName + "</b> :" + strings.ReplaceAll(update.Message.Text, "/ans", " ")
        messageText = messageText + text + "\n"
        msg := tgbotapi.NewEditMessageText(message.Chat.ID, message.MessageID, messageText)
        msg.ParseMode = tgbotapi.ModeHTML
        bot.Send(msg)
        bot.Send(tgbotapi.NewEditMessageReplyMarkup(message.Chat.ID, message.MessageID, inlineButton_Reply))
        counter++

        msgReply := tgbotapi.NewMessage(update.Message.Chat.ID, "Your answers have been saved. Go to @system_logs again to see others' answers.")
  	    msgReply.ReplyToMessageID = update.Message.MessageID
  	    bot.Send(msgReply)
			default:
				msgReply := tgbotapi.NewMessage(update.Message.Chat.ID, "Belo")
				msgReply.ReplyToMessageID = update.Message.MessageID
				bot.Send(msgReply)
			}
		} 
    if counter > 9 {break}
  }
  messageText = messageText + "Discussion ended."
  msgEnd := tgbotapi.NewEditMessageText(message.Chat.ID, message.MessageID, messageText)
  msgEnd.ParseMode = tgbotapi.ModeHTML
  bot.Send(msgEnd)
  log.Printf("Program end.")
}
