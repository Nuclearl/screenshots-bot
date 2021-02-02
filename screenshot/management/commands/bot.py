import logging, os
from django.core.management import BaseCommand
from django.conf import settings
from screenshot.models import Profile
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from asgiref.sync import sync_to_async
from site_function import screenshots

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

KEY_BTN1 = "Скриншот сайта"


# state
class UrlState(StatesGroup):
    url = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton(KEY_BTN1))
    user_id = message.from_user.id
    await sync_to_async(Profile.objects.get_or_create, thread_sensitive=True)(user_id=user_id)
    await bot.send_message(user_id, "Бот для скриншотов сайта", reply_markup=keyboard)


@dp.message_handler(
    lambda message: message.text == KEY_BTN1 and message.from_user.id == message.chat.id)
async def take_massage(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await bot.send_message(user_id, "Отправьте ссылку на сайт")
    await UrlState.url.set()


@dp.message_handler(state=UrlState.url)
async def get_url(message: types.Message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    if text == '/start':
        await state.finish()
        await start(message)
    else:
        waiting_msg = await bot.send_message(user_id, "Обработка запроса...")
        path = f'site_function/storage/{user_id}.png'
        photo = await screenshots.generate_photo(text, path)
        try:
            await bot.delete_message(user_id, waiting_msg.message_id)
        except:
            pass
        if photo:
            await bot.send_document(user_id, document=open(path, 'rb'))
            try:
                os.remove(path)
            except:
                pass
        else:
            await bot.send_message(user_id, "Ошибка!")
        await state.finish()


class Command(BaseCommand):
    def handle(self, *args, **options):
        executor.start_polling(dp)
