from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni 1 bosishda ulashish tugmasi"""
    kb = [
        [KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_name_suggestion_keyboard(full_name: str) -> ReplyKeyboardMarkup:
    """Telegramdagi ism-familiyani 1 bosishda tanlash tugmasi"""
    kb = [
        [KeyboardButton(text=full_name)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
