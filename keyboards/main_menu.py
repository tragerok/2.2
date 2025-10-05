from aiogram import types
from utils.db import get_user
from utils.locale import L

def get_main_menu(user_id):
    lang = "ru"
    info = get_user(user_id)
    if info and 'lang' in info and info['lang'] in ['ru', 'en']:
        lang = info['lang']
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(L("main_menu_profile", lang))
    kb.add(L("main_menu_buy_license", lang), L("main_menu_renew", lang))
    kb.add(L("main_menu_topup", lang))
    kb.add(L("main_menu_support", lang), L("main_menu_language", lang))
    return kb
