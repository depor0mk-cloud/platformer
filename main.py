# Telegram Clan Bot

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class ClanBot:
    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start(self, update, context):
        update.message.reply_text('Hello! I am your clan bot.')

    def handle_message(self, update, context):
        text = update.message.text
        update.message.reply_text(f'You said: {text}')

    def run(self):
        start_handler = CommandHandler('start', self.start)
        message_handler = MessageHandler(Filters.text & ~Filters.command, self.handle_message)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(message_handler)

        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
    bot = ClanBot(TOKEN)
    bot.run()