import telebot


# جایگزین کن با توکن رباتت
TOKEN = "8390278484:AAEZYoEIn76BkAuXUlo2pGql8ieniWA8Mko"
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! ربات وصل شد ✅")
print( "start" )
bot.infinity_polling()