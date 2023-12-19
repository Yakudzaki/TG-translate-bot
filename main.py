import io
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import BOT_TOKEN
from utils_db import add_count_translate, create_tables, create_user, get_user, get_translate_text, add_translate
from translate_utils import translate_text

storage = MemoryStorage()
dp = Dispatcher(
    Bot(
        BOT_TOKEN,
        parse_mode='html'
    ),
    storage=storage
)


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    user = get_user(msg.from_user.id)
    new_user = False

    if user is None:
        create_user(msg.from_user.id)
        new_user = True
    
    msg_text = (
        '<b>Вы уже зарегистрированы!</b>\n\n' if not new_user else '<b>Добро пожаловать в бота!</b>\n\n'
    )

    await msg.answer(
        msg_text,
        reply_markup=types.ReplyKeyboardMarkup(
            [
                [
                    types.KeyboardButton('📗 Профиль')
                ]
            ],
            resize_keyboard=True
        ))

@dp.message_handler(text='📗 Профиль')
async def profile(msg: types.Message):
    user = get_user(msg.from_user.id)

    msg_text = (
        '<b>📗 Профиль</b>\n\n'
        f'<b>Айди:</b> <code>{msg.from_user.id}</code>\n'
        f'<b>Кол-во переводов:</b> <code>{user.translate_count}</code>\n'
    )

    await msg.answer(
        msg_text
    )


@dp.message_handler(content_types=['text'])
async def translate(msg: types.Message, state: FSMContext):
    await state.set_state('choice_language')
    await state.update_data(
        text=msg.text
    )

    await msg.answer(
        '<b>Выберите язык на который нужно перевести!</b>',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton('🇬🇧 Английский', callback_data='translate_en'),
                    types.InlineKeyboardButton('🇪🇸 Испанский', callback_data='translate_es')
                ],
                [
                    types.InlineKeyboardButton('🇩🇪 Немецкий', callback_data='translate_de'),
                    types.InlineKeyboardButton('🇵🇱 Польский', callback_data='translate_pl')
                ]
            ]
        ))


@dp.callback_query_handler(state='choice_language', text_startswith='translate_')
async def translate_choice_language(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = call.data.replace('translate_', '')
    await state.finish()

    add_count_translate(call.from_user.id)

    message = await call.message.edit_text('<b>Идет перевод...</b>')

    text = translate_text(
        data.get('text'),
        language
    )
    translate = add_translate(text)

    await message.edit_text(
        '<b>⚡️ Перевод завершен!</b>\n\n'
        f'<b>💬 Перевод: {text}</b>',
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton('📥 Скачать перевод', callback_data=f'download_{translate.translate_id}')
                ]
            ]
        )
    )
    

@dp.callback_query_handler(text_startswith='download_')
async def translate_download(call: types.CallbackQuery):
    translate_id = int(call.data.replace('download_', ''))
    text = get_translate_text(translate_id)

    await call.message.delete()

    with io.StringIO(text) as file:
        input_file = types.InputFile(file, filename="translate.txt")

        await call.message.answer_document(
            input_file
        )


if __name__ == '__main__':
    print('Бот был запущен!')
    create_tables()
    executor.start_polling(
        dp,
        skip_updates=True
    )