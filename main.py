from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from lookup import *

TOKEN='331304045:AAGVjGkL-11ysUPoSTk-EStFTNB93s00Gxw'

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Disease Ontology Mapping Bot is a tool for unification of terms in medical diagnoses. \nVisit https://github.com/elliekinz/Disease-ontology for details.')


def help(bot, update):
    update.message.reply_text('Please, insert your query in the following format: \n# Reason for admission: Cardiomyopathy \n# Acute infarction (localization): no \n# Former infarction (localization): no \n# Additional diagnoses: Hypertrophic obstructive cardiomyopathy \n or simply insert your diagnostic term such as \"aortic tenosis\"')


def process(bot, update):
    for m in lookup(update.message.text):
        bot.sendMessage(update.message.chat_id, m)
        if m.startswith("Best fuzzy match"):
            #bot.sendMessage(update.message.chat_id, m)
            bot.sendPhoto(update.message.chat_id, photo=open("test-output/round-table.gv.png", "rb"))
            

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, process))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
