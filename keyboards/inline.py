from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.constants import (
    DIRECTIONS, PERCENTAGES, AGE_RANGES, REGIONS,
    HOUSING_TYPES, EDUCATION_LEVELS, EXPERIENCE_LEVELS,
    LANGUAGE_LEVELS, DEVICE_OPTIONS, DRIVING_OPTIONS,
    TRIP_OPTIONS, OVERTIME_OPTIONS, SALARY_OPTIONS
)

def get_directions_keyboard() -> InlineKeyboardMarkup:
    """Yo'nalishlar (Vakansiyalar) ro'yxati"""
    buttons = []
    for key, name in DIRECTIONS.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"dir:{key}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_program_percentage_keyboard(program_index: int) -> InlineKeyboardMarkup:
    """Dasturlarni bilish foizlari (0%, 25%, 50%, 75%, 100%)"""
    row = []
    for pct in PERCENTAGES:
        row.append(InlineKeyboardButton(text=pct, callback_data=f"prog_pct:{program_index}:{pct}"))
    return InlineKeyboardMarkup(inline_keyboard=[row])

def get_age_keyboard() -> InlineKeyboardMarkup:
    """Yosh toifalari tugmalari"""
    buttons = []
    row = []
    for idx, age in enumerate(AGE_RANGES):
        row.append(InlineKeyboardButton(text=age, callback_data=f"age:{idx}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_regions_keyboard() -> InlineKeyboardMarkup:
    """Viloyatlar va Toshkent shahri (2 tadan qatorda)"""
    buttons = []
    row = []
    for idx, region in enumerate(REGIONS):
        # Qisqaroq nom berish tugmaga sig'ishi uchun
        short_name = region.replace(" viloyati", " vil.").replace(" Resp.", "")
        row.append(InlineKeyboardButton(text=short_name, callback_data=f"reg:{idx}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_housing_keyboard() -> InlineKeyboardMarkup:
    """Yashash sharoiti (Hovli / Dom)"""
    buttons = [
        [InlineKeyboardButton(text=h, callback_data=f"house:{idx}") for idx, h in enumerate(HOUSING_TYPES)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_education_keyboard() -> InlineKeyboardMarkup:
    """Ma'lumoti darajalari"""
    buttons = []
    for idx, edu in enumerate(EDUCATION_LEVELS):
        buttons.append([InlineKeyboardButton(text=edu, callback_data=f"edu:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_experience_keyboard() -> InlineKeyboardMarkup:
    """Ish tajribasi"""
    buttons = []
    for idx, exp in enumerate(EXPERIENCE_LEVELS):
        buttons.append([InlineKeyboardButton(text=exp, callback_data=f"exp:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_language_keyboard(lang_code: str) -> InlineKeyboardMarkup:
    """Til bilish darajalari: ru yoki en"""
    buttons = []
    row = []
    for idx, level in enumerate(LANGUAGE_LEVELS):
        row.append(InlineKeyboardButton(text=level, callback_data=f"lang:{lang_code}:{idx}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_device_keyboard() -> InlineKeyboardMarkup:
    """Kompyuter mavjudligi"""
    buttons = []
    for idx, dev in enumerate(DEVICE_OPTIONS):
        buttons.append([InlineKeyboardButton(text=dev, callback_data=f"dev:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_driving_keyboard() -> InlineKeyboardMarkup:
    """Haydovchilik / Mashina"""
    buttons = []
    for idx, drv in enumerate(DRIVING_OPTIONS):
        buttons.append([InlineKeyboardButton(text=drv, callback_data=f"drv:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_trip_keyboard() -> InlineKeyboardMarkup:
    """Komandirovka"""
    buttons = [
        [InlineKeyboardButton(text=trip, callback_data=f"trip:{idx}") for idx, trip in enumerate(TRIP_OPTIONS)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_overtime_keyboard() -> InlineKeyboardMarkup:
    """Qo'shimcha vaqt ishlash"""
    buttons = []
    for idx, ot in enumerate(OVERTIME_OPTIONS):
        buttons.append([InlineKeyboardButton(text=ot, callback_data=f"overtime:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_salary_keyboard() -> InlineKeyboardMarkup:
    """Kutilayotgan maosh"""
    buttons = []
    row = []
    for idx, sal in enumerate(SALARY_OPTIONS):
        row.append(InlineKeyboardButton(text=sal, callback_data=f"sal:{idx}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_skip_keyboard() -> InlineKeyboardMarkup:
    """O'tkazib yuborish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data="port:skip")]
    ])

def get_portfolio_keyboard(count: int = 0) -> InlineKeyboardMarkup:
    """Portfolio yuklash bosqichi uchun tugmalar"""
    buttons = []
    if count > 0:
        buttons.append([InlineKeyboardButton(text=f"✅ Tayyor, davom etish ({count} ta)", callback_data="port:done")])
    else:
        buttons.append([InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data="port:skip")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Tasdiqlash yoki qayta boshlash"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash va Yuborish", callback_data="confirm:yes")],
        [InlineKeyboardButton(text="🔄 Qayta to'ldirish", callback_data="confirm:restart")]
    ])

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Excel (.xlsx) yuklab olish", callback_data="admin:excel")],
        [InlineKeyboardButton(text="📋 So'nggi arizalarni ko'rish", callback_data="admin:recent")],
        [InlineKeyboardButton(text="📈 Statistika", callback_data="admin:stats")],
        [InlineKeyboardButton(text="👥 Adminlar boshqaruvi", callback_data="admin:manage_admins")]
    ])

def get_admins_manage_keyboard(admins: list, current_user_id: int) -> InlineKeyboardMarkup:
    """Adminlar ro'yxati va boshqaruv tugmalari"""
    buttons = []
    for adm in admins:
        uid = adm["user_id"]
        name = adm.get("full_name") or adm.get("username") or f"ID: {uid}"
        if uid != current_user_id:
            buttons.append([InlineKeyboardButton(text=f"🗑 O'chirish: {name}", callback_data=f"admin:del_admin:{uid}")])
        else:
            buttons.append([InlineKeyboardButton(text=f"👤 {name} (Siz)", callback_data="noop")])
            
    buttons.append([InlineKeyboardButton(text="➕ Yangi admin qo'shish", callback_data="admin:add_admin")])
    buttons.append([InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_cancel_admin_keyboard() -> InlineKeyboardMarkup:
    """Bekor qilish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Bekor qilish", callback_data="admin:manage_admins")]
    ])

def get_hr_decision_keyboard(applicant_id: int) -> InlineKeyboardMarkup:
    """HR qaror tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Suhbatga chaqirish", callback_data=f"hr_decision:accept:{applicant_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"hr_decision:reject:{applicant_id}")
        ]
    ])

