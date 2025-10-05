from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN
from handlers import start, profile, subscription, balance, support, hwid, license_renewal, admin  # обязательно импорт admin!

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

start.register(dp)
profile.register(dp)
subscription.register(dp)
balance.register(dp)
support.register(dp)
hwid.register(dp)
license_renewal.register(dp)
admin.register(dp)  # подключаем админку!

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
