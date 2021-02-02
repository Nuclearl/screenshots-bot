from django.core.management import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.utils.request import Request
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
from screenshot.models import Profile


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_msg = f'Error: {e}'
            print(error_msg)
            raise e

    return inner


@log_errors
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text
    reply_text = f"ID: {chat_id}"

    p, _ = Profile.objects.get_or_create(
        user_id=chat_id,
    )

    update.message.reply_text(
        text=reply_text,
    )


class Command(BaseCommand):

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
            base_url=settings.PROXY_URL,
        )

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        message_handler = MessageHandler(Filters.text, do_echo)
        updater.dispatcher.add_handler(message_handler)

        #message_handler2 = CommandHandler('start', start)
        #updater.dispatcher.add_handler(message_handler2)
        updater.start_polling()
        updater.idle()
