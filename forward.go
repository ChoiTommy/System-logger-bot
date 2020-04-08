package main
import (
	"github.com/go-telegram-bot-api/telegram-bot-api"
	"log"
  "math/rand"
  "time"
  "os"
  "strconv"
)
func forward(){
  token := os.Getenv("TOKEN")
	bot, err := tgbotapi.NewBotAPI(token)
	if err != nil {
		log.Fatal(err)
	}
  rand.Seed(time.Now().UnixNano())
	bot.Debug = true

	log.Printf("Authorized on account %s", bot.Self.UserName)

  k := 434;
  /*u := tgbotapi.NewUpdate(0)
	u.Timeout = 60
  updates, err := bot.GetUpdatesChan(u)*/

  channelid, err := strconv.ParseInt(os.Getenv("CHANNEL_ID"), 10, 64)
  chatid, err := strconv.ParseInt(os.Getenv("CHAT_TIMCHUNW_ID"), 10, 64)

  for {
    msg := tgbotapi.NewForward(chatid, channelid, getRand(k))
    m, err := bot.Send(msg)
    _ = m
    for err != nil {
  		log.Printf("error: ", err)
      m, err = bot.Send(tgbotapi.NewForward(chatid, channelid, getRand(k)))
      _ = m
  	}
    //bot.Send(tgbotapi.NewMessage(chatid, ""))
    time.Sleep(2*time.Hour)
  }

  /*for update := range updates {
		if update.Message.Chat.IsChannel() == true {
			k++
      log.Printf("k value: ", k)
		}
  }*/
}

func getRand(k int) int{
  return rand.Intn(k - 297 + 1) + 297
}
