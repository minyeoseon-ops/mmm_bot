import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

# Configuration
BOT_TOKEN = "8994734061:AAHS1j6WT3GhichYUehYAuniWrNTAZ19_uI"
ADMIN_ID = 878726693  # Ваш Telegram ID

# Links
PLAYER_MINI_APP_URL = "https://t.me/Mint_mix_bot/ba_mixing"  # Ссылка на Mini App
CALCULATOR_URL = "https://b-a-sound.netlify.app/"
REVIEWS_POST_URL = "https://t.me/Mini_mint_mix/18"  # Ссылка на пост с отзывами

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# FSM States
class OrderForm(StatesGroup):
    channel_username = State()
    song_name = State()
    duration = State()
    group_type = State()
    extra_options = State()
    currency = State()


# Keyboards
def get_main_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎧 Примеры До/После", url=PLAYER_MINI_APP_URL
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧮 Калькулятор цены", url=CALCULATOR_URL
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Отзывы клиентов", url=REVIEWS_POST_URL
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Оформить заявку", callback_data="start_order"
                )
            ],
        ]
    )


def get_currency_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Рубли (RU)")],
            [KeyboardButton(text="Звёзды (⭐️)")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# Handlers
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        "Привет! Я бот для приёма заявок на сведение и мастеринг от <b>@Mini_mint_mix</b>.\n\n"
        "Здесь вы можете рассчитать стоимость, послушать примеры работ и оставить заявку на сведение."
    )
    await message.answer(
        welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML"
    )


@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    user = callback.from_user
    user_handle = (
        f"@{user.username}"
        if user.username
        else f"ID: {user.id} ({user.first_name})"
    )
    await state.update_data(user_handle=user_handle)

    await callback.message.answer(
        "Шаг 1/6: Укажите юзернейм вашего канала (или нажмите 'Пропустить'):",
        reply_markup=get_skip_keyboard(),
    )
    await state.set_state(OrderForm.channel_username)


@dp.message(OrderForm.channel_username)
async def process_channel(message: types.Message, state: FSMContext):
    channel = message.text if message.text != "Пропустить" else "Не указан"
    await state.update_data(channel_username=channel)

    await message.answer(
        "Шаг 2/6: Введите название песни:",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OrderForm.song_name)


@dp.message(OrderForm.song_name)
async def process_song_name(message: types.Message, state: FSMContext):
    await state.update_data(song_name=message.text)

    await message.answer(
        "Шаг 3/6: Укажите хронометраж/длительность песни или отрывка (например: 2:45 или Мини-кавер 1:20):"
    )
    await state.set_state(OrderForm.duration)


@dp.message(OrderForm.duration)
async def process_duration(message: types.Message, state: FSMContext):
    await state.update_data(duration=message.text)

    await message.answer(
        "Шаг 4/6: Укажите формат (Соло / Дуэт / Трио / Группа) и количество участников:"
    )
    await state.set_state(OrderForm.group_type)


@dp.message(OrderForm.group_type)
async def process_group_type(message: types.Message, state: FSMContext):
    await state.update_data(group_type=message.text)

    await message.answer(
        "Шаг 5/6: Нужны ли дополнительные опции? (Тюн, бэки/хармы, реставрация, срочный дедлайн). Если не нужны, нажмите 'Пропустить':",
        reply_markup=get_skip_keyboard(),
    )
    await state.set_state(OrderForm.extra_options)


@dp.message(OrderForm.extra_options)
async def process_extra_options(message: types.Message, state: FSMContext):
    options = message.text if message.text != "Пропустить" else "Нет"
    await state.update_data(extra_options=options)

    await message.answer(
        "Шаг 6/6: Выберите предпочтительную валюту для оплаты:",
        reply_markup=get_currency_keyboard(),
    )
    await state.set_state(OrderForm.currency)


@dp.message(OrderForm.currency)
async def process_currency(message: types.Message, state: FSMContext):
    await state.update_data(currency=message.text)
    data = await state.get_data()

    summary = (
        "📥 <b>НОВАЯ ЗАЯВКА НА СВЕДЕНИЕ</b>\n\n"
        f"1) <b>Заказчик:</b> {data['user_handle']}\n"
        f"2) <b>Канал:</b> {data['channel_username']}\n"
        f"3) <b>Песня:</b> {data['song_name']}\n"
        f"4) <b>Длительность:</b> {data['duration']}\n"
        f"5) <b>Формат/Состав:</b> {data['group_type']}\n"
        f"6) <b>Доп. опции:</b> {data['extra_options']}\n"
        f"7) <b>Оплата:</b> {data['currency']}"
    )

    await message.answer(
        "Спасибо! Ваша заявка сформирована и отправлена звукорежиссёру. Скоро с вами свяжутся!\n\n"
        + summary,
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )

    await bot.send_message(ADMIN_ID, summary, parse_mode="HTML")

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
