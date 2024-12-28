# ЗАДАНИЕ ПО ТЕМЕ "Клавиатура кнопок"

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

api = 'MY_TOKEN'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.add(button1)
kb.add(button2)


class UserState(StatesGroup):
    age = State()  # возраст
    growth = State()  # рост
    weight = State()  # вес


# Реагирует на Reply-кнопку "Рассчитать" / сообщение и запрашивает возраст
@dp.message_handler(text='Рассчитать')
async def set_age(message: types.Message):
    await message.answer('Введите свой возраст (полных лет):')
    await UserState.age.set()


# Реагирует на сообщение о возрасте и запрашивает рост
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age_ans=message.text)
    data = await state.get_data()
    await message.answer('Введите свой рост (см):')
    await UserState.growth.set()


# Реагирует на сообщение о росте и запрашивает вес
@dp.message_handler(state=UserState.growth)
async def set_weigth(message: types.Message, state: FSMContext):
    await state.update_data(growth_ans=message.text)
    data = await state.get_data()
    await message.answer('Введите свой вес (кг):')
    await UserState.weight.set()


# Реагирует на сообщение о весе, рассчитывает норму калорий и выдает полученный результат
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight_ans=message.text)
    data = await state.get_data()
    # Попробуем конвертировать переданные сообщения в целые числа
    # и рассчитаем для них норму калорий
    try:
        age = int(data['age_ans'])
        growth = int(data['growth_ans'])
        weight = int(data['weight_ans'])
        kcal_women = int(10 * weight + 6.25 * growth - 5 * age - 161)
        kcal_man = int(10 * weight + 6.25 * growth - 5 * age + 5)
        await message.answer(
            f'Вами указаны данные:\nвозраст - {age} полных лет\n'
            f'рост - {growth} см\nвес - {weight} кг\n'
            f'Норма калорий для женщин - {kcal_women} ккал в сутки\n'
            f'Норма калорий для мужчин - {kcal_man} ккал в сутки'
        )
    # Если какое-либо из значений не может быть представлено целым числом
    except Exception as er:
        await message.answer(
            f'Вами указаны данные:\nвозраст - {data["age_ans"]} полных лет\n'
            f'рост - {data["growth_ans"]} см\nвес - {data["weight_ans"]} кг\n'
            f'Нельзя преобразовать все значения в целые числа\n({er})\nи сделать расчет\n'
            f'Попробуйте еще раз'
        )
    await state.finish()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer(
        'Привет! Я бот помогающий твоему здоровью', reply_markup=kb)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer(
        'Информация о боте!\n'
        'Этот бот может рассчитать норму калорий для мужчин и женщин\n'
        'Нажмите кнопку "Рассчитать" и ответьте на ряд вопросов'
    )


@dp.message_handler()
async def urban_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
