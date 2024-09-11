import telebot
from telebot import custom_filters, types
from telebot.states import State, StatesGroup
from telebot.states.sync.context import StateContext
from telebot.storage import StateMemoryStorage

TOKEN = "6860802226:AAG-XIz69_TxQjV1JDYrpeKiTbdvENWtEnI"
state_storage = StateMemoryStorage()  # don't use this in production; switch to redis
bot = telebot.TeleBot(TOKEN, state_storage=state_storage, use_class_middlewares=True)


class MyStates(StatesGroup):
    waiting_res1 = State()
    waiting_res2 = State()

res1 = 0
res2 = 0

# Start command handler
@bot.message_handler(commands=["start"])
def start_ex(message: types.Message, state: StateContext):
    state.set(MyStates.waiting_res1)
    bot.send_message(message.chat.id, "Привет! Введи значение первого сопротивления!",)


# Cancel command handler
@bot.message_handler(state="*", commands=["cancel"])
def any_state(message: types.Message, state: StateContext):
    state.delete()
    bot.send_message(
        message.chat.id,
        "Информация удалена, для повторения введите /start",
        reply_to_message_id=message.message_id,
    )


# Handler for name input
@bot.message_handler(state=MyStates.waiting_res1, is_digit=True)
def res1_get(message: types.Message, state: StateContext):
    bot.send_message(
        message.chat.id, "Отлично, теперь введи значение второго сопротивления", reply_to_message_id=message.message_id
    )
    state.add_data(res1=message.text)
    state.set(MyStates.waiting_res2)


# Handler for age input
@bot.message_handler(state=MyStates.waiting_res2, is_digit=True)
def res2_get(message: types.Message, state: StateContext):
    with state.data() as data:
        res1 = int(data.get("res1"))
    res2 = int(message.text)
    mes = f"Общий номинал сопротивления при последовательном подключении: {res1+res2} ОМ\n\nОбщий номинал сопротивления при паррарельном подключении: {1/((1/res1)+(1/res2))} ОМ"
    bot.send_message(message.chat.id, mes)
    state.delete()


# Handler for incorrect age input
@bot.message_handler(state=MyStates.waiting_res1, is_digit=False)
def age_incorrect(message: types.Message):
    bot.send_message(
        message.chat.id,
        "Пожалуйста введите правильное число для резистора!.",
        reply_to_message_id=message.message_id,
    )

@bot.message_handler(state=MyStates.waiting_res2, is_digit=False)
def age_incorrect(message: types.Message):
    bot.send_message(
        message.chat.id,
        "Пожалуйста введите правильное число для резистора!.",
        reply_to_message_id=message.message_id,
    )


# Add custom filters
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())

# necessary for state parameter in handlers.
from telebot.states.sync.middleware import StateMiddleware

bot.setup_middleware(StateMiddleware(bot))

# Start polling
bot.infinity_polling()