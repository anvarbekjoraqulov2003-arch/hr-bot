import re
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from states.applicant import ApplicantForm
from keyboards.inline import (
    get_program_percentage_keyboard, get_age_keyboard, get_regions_keyboard,
    get_housing_keyboard, get_education_keyboard, get_experience_keyboard,
    get_language_keyboard, get_device_keyboard, get_driving_keyboard,
    get_trip_keyboard, get_overtime_keyboard, get_salary_keyboard,
    get_skip_keyboard, get_confirm_keyboard, get_hr_decision_keyboard,
    get_directions_keyboard, get_portfolio_keyboard
)
from keyboards.reply import get_phone_keyboard, get_name_suggestion_keyboard, remove_keyboard
from data.constants import (
    DIRECTIONS, DIRECTION_PROGRAMS, AGE_RANGES, REGIONS,
    HOUSING_TYPES, EDUCATION_LEVELS, EXPERIENCE_LEVELS,
    LANGUAGE_LEVELS, DEVICE_OPTIONS, DRIVING_OPTIONS,
    TRIP_OPTIONS, OVERTIME_OPTIONS, SALARY_OPTIONS
)
from database import add_applicant, get_all_admins_db
from config import ADMIN_IDS, HR_CHANNEL_ID


anketa_router = Router()

def validate_and_format_phone(raw: str) -> str | None:
    """Telefon raqamini tekshirish va xalqaro formatga keltirish.
    Agar matnda harflar (ism yoki boshqa so'zlar) bo'lsa, qat'iy rad etiladi.
    """
    if not raw:
        return None
    # Agar lotin yoki kirill harflari bo'lsa, bu ism yoki matn - telefon raqam emas
    if re.search(r'[a-zA-Zа-яА-ЯёЁўқғҳЎҚҒҲ]', raw):
        return None

    # Bo'sh joylar, qavslar va tirelarni tozalaymiz
    cleaned = re.sub(r'[\s\-\(\)]', '', raw)
    if not cleaned:
        return None

    # Raqamlar soni va formatini tekshirish
    if re.match(r'^\+?[0-9]{9,15}$', cleaned):
        digits = cleaned.lstrip('+')
        if len(digits) == 9:
            return f"+998{digits}"
        elif len(digits) == 12 and digits.startswith("998"):
            return f"+{digits}"
        elif len(digits) == 10 and digits.startswith("8"):
            return f"+998{digits[1:]}"
        else:
            return f"+{digits}"
    return None

def format_progress_bar(pct_str: str) -> str:
    """Foizni Telegramda chiroyli ko'rsatuvchi vizual indikator"""
    pct_map = {
        "0%": "░░░░░░░░░░ 0%",
        "25%": "███░░░░░░░ 25%",
        "50%": "█████░░░░░ 50%",
        "75%": "████████░░ 75%",
        "100%": "██████████ 100%"
    }
    return pct_map.get(pct_str.strip(), pct_str)

def format_summary(data: dict, applicant_id: int = None) -> str:
    """Anketa xulosasini minimalist va toza ko'rinishda shakllantirish"""
    programs_text = ""
    if data.get("programs"):
        lines = []
        for k, v in data["programs"].items():
            bar = format_progress_bar(str(v))
            lines.append(f"  • {k}:\n    <code>[{bar}]</code>")
        programs_text = "\n".join(lines)
    else:
        programs_text = "  <i>Ko'rsatilmadi</i>"

    id_line = f" #{applicant_id}" if applicant_id else ""
    username_str = f"@{data.get('username')}" if data.get("username") else "Mavjud emas"

    # Portfolio ko'rinishini shakllantirish
    port_files = data.get("portfolio_files", [])
    port_links = data.get("portfolio_links", [])
    if port_files or port_links:
        port_parts = []
        if port_links:
            port_parts.append("Havolalar:\n" + "\n".join([f"    • {l}" for l in port_links]))
        if port_files:
            file_names = [f.get("file_name", "Fayl") for f in port_files]
            port_parts.append(f"{len(port_files)} ta fayl:\n" + "\n".join([f"    • {fn}" for fn in file_names]))
        portfolio_display = "\n  " + "\n  ".join(port_parts)
    else:
        portfolio_display = data.get("portfolio", "Kiritilmadi")

    summary = (
        f"📄 <b>NOMZOD ANKETASI{id_line}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Yo'nalish:</b> {data.get('direction')}\n"
        f"<b>Nomzod:</b> {username_str}\n\n"
        f"<b>Shaxsiy ma'lumotlar:</b>\n"
        f"  • F.I.O: <b>{data.get('full_name')}</b>\n"
        f"  • Telefon: <code>{data.get('phone')}</code>\n"
        f"  • Yoshi: {data.get('age_range')}\n"
        f"  • Hudud: {data.get('region')}\n"
        f"  • Yashash joyi: {data.get('housing')}\n"
        f"  • Ma'lumoti: {data.get('education')}\n"
        f"  • Ish tajribasi: {data.get('experience')}\n\n"
        f"<b>Dasturlar va ko'nikmalar:</b>\n"
        f"{programs_text}\n\n"
        f"<b>Tillar:</b>\n"
        f"  • Rus tili: {data.get('russian_level')}\n"
        f"  • Ingliz tili: {data.get('english_level')}\n\n"
        f"<b>Qo'shimcha ma'lumotlar:</b>\n"
        f"  • Kompyuter: {data.get('device')}\n"
        f"  • Haydovchilik: {data.get('driving')}\n"
        f"  • Xizmat safari: {data.get('trip_ready')}\n"
        f"  • Qo'shimcha ishlash: {data.get('overtime_ready')}\n\n"
        f"<b>Kutilayotgan maosh:</b> {data.get('expected_salary')}\n"
        f"<b>Portfolio:</b> {portfolio_display}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    return summary

# 1. Yo'nalish tanlanganda -> BIRINCHI SHAXSIY MA'LUMOTLARNI OLISH
@anketa_router.callback_query(F.data.startswith("dir:"), ApplicantForm.direction)
async def process_direction(callback: types.CallbackQuery, state: FSMContext):
    dir_key = callback.data.split(":")[1]
    if dir_key not in DIRECTIONS:
        await callback.answer("Noto'g'ri yo'nalish tanlandi!", show_alert=True)
        return

    dir_name = DIRECTIONS[dir_key]
    programs = DIRECTION_PROGRAMS.get(dir_key, [])

    await state.update_data(
        direction_key=dir_key,
        direction=dir_name,
        programs_list=programs,
        programs={}
    )

    user_name = f"{callback.from_user.first_name or ''} {callback.from_user.last_name or ''}".strip()
    if not user_name:
        user_name = callback.from_user.username or "Nomzod"

    try:
        await callback.message.delete()
    except Exception:
        pass

    text = (
        f"Tanlangan yo'nalish: <b>{dir_name}</b>\n\n"
        "1. <b>Ism va familiyangizni</b> kiriting:\n\n"
        "<i>(Quyidagi tugmani bossangiz, Telegramdagi ismingiz avtomatik tanlanadi)</i>"
    )
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_name_suggestion_keyboard(user_name)
    )
    await state.set_state(ApplicantForm.full_name)
    await callback.answer()

# 2. F.I.O kiritilganda
@anketa_router.message(ApplicantForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    full_name = message.text.strip()
    if len(full_name) < 3:
        await message.answer("Iltimos, ism va familiyangizni to'liq kiriting:")
        return

    await state.update_data(
        full_name=full_name,
        user_id=message.from_user.id,
        username=message.from_user.username
    )

    text = (
        f"2. <b>Telefon raqamingizni</b> yuboring:\n\n"
        "<i>(Quyidagi tugmani bosing, raqamingiz avtomatik yuboriladi)</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_phone_keyboard())
    await state.set_state(ApplicantForm.phone)

# 3. Telefon raqam yuborilganda
@anketa_router.message(ApplicantForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_candidate = None
    if message.contact:
        phone_candidate = message.contact.phone_number
    elif message.text:
        phone_candidate = message.text.strip()

    valid_phone = validate_and_format_phone(phone_candidate) if phone_candidate else None

    if not valid_phone:
        text = (
            "⚠️ <b>Telefon raqami noto'g'ri kiritildi!</b>\n\n"
            "Telefon raqamni kiritish <b>majburiy</b>. Iltimos, pastdagi "
            "<b>«📱 Telefon raqamni yuborish»</b> tugmasini bosing yoki raqamingizni quyidagi ko'rinishda yozing:\n"
            "<code>+998901234567</code> yoki <code>901234567</code>"
        )
        await message.answer(text, parse_mode="HTML", reply_markup=get_phone_keyboard())
        return

    await state.update_data(phone=valid_phone)

    # Reply keyboardni olib tashlaymiz
    await message.answer("Telefon raqamingiz qabul qilindi.", reply_markup=remove_keyboard())

    # 4. Yosh toifasi
    text = "3. <b>Yoshingiz</b> qaysi toifaga to'g'ri keladi?"
    await message.answer(text, parse_mode="HTML", reply_markup=get_age_keyboard())
    await state.set_state(ApplicantForm.age_range)

# 4. Yosh tanlanganda
@anketa_router.callback_query(F.data.startswith("age:"), ApplicantForm.age_range)
async def process_age(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    age = AGE_RANGES[idx]
    await state.update_data(age_range=age)

    # 5. Hudud
    text = "4. Doimiy <b>yashash hududingiz</b> (viloyat/shahar):"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_regions_keyboard())
    await state.set_state(ApplicantForm.region)
    await callback.answer()

# 5. Hudud tanlanganda
@anketa_router.callback_query(F.data.startswith("reg:"), ApplicantForm.region)
async def process_region(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    region = REGIONS[idx]
    await state.update_data(region=region)

    # 6. Yashash sharoiti
    text = "5. <b>Yashash sharoitingiz</b>:"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_housing_keyboard())
    await state.set_state(ApplicantForm.housing)
    await callback.answer()

# 6. Yashash sharoiti tanlanganda
@anketa_router.callback_query(F.data.startswith("house:"), ApplicantForm.housing)
async def process_housing(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    housing = HOUSING_TYPES[idx]
    await state.update_data(housing=housing)

    # 7. Ma'lumoti
    text = "6. <b>Ma'lumotingiz</b> darajasini tanlang:"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_education_keyboard())
    await state.set_state(ApplicantForm.education)
    await callback.answer()

# 7. Ma'lumoti tanlanganda
@anketa_router.callback_query(F.data.startswith("edu:"), ApplicantForm.education)
async def process_education(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    education = EDUCATION_LEVELS[idx]
    await state.update_data(education=education)

    # 8. Ish tajribasi
    text = "7. Ushbu sohadagi <b>ish tajribangiz</b>:"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_experience_keyboard())
    await state.set_state(ApplicantForm.experience)
    await callback.answer()

# 8. Ish tajribasi tanlanganda
@anketa_router.callback_query(F.data.startswith("exp:"), ApplicantForm.experience)
async def process_experience(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    experience = EXPERIENCE_LEVELS[idx]
    await state.update_data(experience=experience)

    # 9. Rus tili
    text = "8. <b>Rus tilini</b> bilish darajangiz:"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_language_keyboard("ru"))
    await state.set_state(ApplicantForm.russian_level)
    await callback.answer()

# 9. Rus tili tanlanganda
@anketa_router.callback_query(F.data.startswith("lang:ru:"), ApplicantForm.russian_level)
async def process_russian(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[2])
    level = LANGUAGE_LEVELS[idx]
    await state.update_data(russian_level=level)

    # 10. Ingliz tili
    text = "9. <b>Ingliz tilini</b> bilish darajangiz:"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_language_keyboard("en"))
    await state.set_state(ApplicantForm.english_level)
    await callback.answer()

# 10. Ingliz tili tanlanganda
@anketa_router.callback_query(F.data.startswith("lang:en:"), ApplicantForm.english_level)
async def process_english(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[2])
    level = LANGUAGE_LEVELS[idx]
    await state.update_data(english_level=level)

    # 11. Kompyuter mavjudligi
    text = "10. Ishlash uchun <b>kompyuter/noutbukingiz</b> bormi?"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_device_keyboard())
    await state.set_state(ApplicantForm.device)
    await callback.answer()

# 11. Kompyuter tanlanganda
@anketa_router.callback_query(F.data.startswith("dev:"), ApplicantForm.device)
async def process_device(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    device = DEVICE_OPTIONS[idx]
    await state.update_data(device=device)

    # 12. Haydovchilik
    text = "11. <b>Haydovchilik guvohnomasi</b> yoki avtomobilingiz bormi?"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_driving_keyboard())
    await state.set_state(ApplicantForm.driving)
    await callback.answer()

# 12. Haydovchilik tanlanganda
@anketa_router.callback_query(F.data.startswith("drv:"), ApplicantForm.driving)
async def process_driving(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    drv = DRIVING_OPTIONS[idx]
    await state.update_data(driving=drv)

    # 13. Komandirovka
    text = "12. Xizmat safarlari (komandirovka)ga chiqishga rozimisiz?"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_trip_keyboard())
    await state.set_state(ApplicantForm.trip_ready)
    await callback.answer()

# 13. Komandirovka tanlanganda
@anketa_router.callback_query(F.data.startswith("trip:"), ApplicantForm.trip_ready)
async def process_trip(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    trip = TRIP_OPTIONS[idx]
    await state.update_data(trip_ready=trip)

    # 14. Ishdan keyin qolib ishlash
    text = "13. Zarurat bo'lganda ishdan keyin ham qolib ishlashga rozimisiz?"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_overtime_keyboard())
    await state.set_state(ApplicantForm.overtime_ready)
    await callback.answer()

# 14. Qolib ishlash tanlanganda -> ENDI DASTURLARNI ANQLASHTIRISH BOSHQICHI!
@anketa_router.callback_query(F.data.startswith("overtime:"), ApplicantForm.overtime_ready)
async def process_overtime(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    ot = OVERTIME_OPTIONS[idx]
    await state.update_data(overtime_ready=ot)

    data = await state.get_data()
    programs = data.get("programs_list", [])
    dir_name = data.get("direction", "")

    if programs:
        await state.update_data(prog_index=0, programs={})
        prog_name = programs[0]
        text = (
            f"Endi <b>{dir_name}</b> yo'nalishi bo'yicha qaysi dasturlarni bilishingizni aniqlashtiramiz:\n\n"
            f"<b>1/{len(programs)}. {prog_name}</b>\n"
            "Ushbu dasturni bilish darajangizni tanlang:"
        )
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_program_percentage_keyboard(0)
        )
        await state.set_state(ApplicantForm.programs)
    else:
        # Dasturlar bo'lmasa oylikka o'tish
        await prompt_salary(callback, state)
    await callback.answer()

# 15. Dasturlar bo'yicha foizlarni belgilash
@anketa_router.callback_query(F.data.startswith("prog_pct:"), ApplicantForm.programs)
async def process_program_percentage(callback: types.CallbackQuery, state: FSMContext):
    _, idx_str, pct = callback.data.split(":")
    idx = int(idx_str)
    data = await state.get_data()
    programs = data.get("programs_list", [])
    programs_dict = data.get("programs", {})

    if idx < len(programs):
        current_prog = programs[idx]
        programs_dict[current_prog] = pct
        await state.update_data(programs=programs_dict)

    next_idx = idx + 1
    if next_idx < len(programs):
        await state.update_data(prog_index=next_idx)
        next_prog = programs[next_idx]
        dir_name = data.get("direction", "")
        text = (
            f"<b>{dir_name}</b> dasturlari:\n\n"
            f"<b>{next_idx + 1}/{len(programs)}. {next_prog}</b>\n"
            "Bilish darajangizni tanlang:"
        )
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_program_percentage_keyboard(next_idx)
        )
        await callback.answer()
    else:
        # Barcha dasturlar belgilandi -> Kutilayotgan oylik maoshga o'tish
        await callback.answer("Dasturlar belgilandi.")
        await prompt_salary(callback, state)

async def prompt_salary(callback: types.CallbackQuery, state: FSMContext):
    """Kutilayotgan maoshni so'rash"""
    text = "Bizda qancha miqdordagi <b>oylik maoshga</b> ishlamoqchisiz?"
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_salary_keyboard())
    await state.set_state(ApplicantForm.expected_salary)

# 16. Maosh tanlanganda
@anketa_router.callback_query(F.data.startswith("sal:"), ApplicantForm.expected_salary)
async def process_salary(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split(":")[1])
    sal = SALARY_OPTIONS[idx]
    await state.update_data(
        expected_salary=sal,
        portfolio_files=[],
        portfolio_links=[]
    )

    # 17. Portfolio / Rezyume
    text = (
        "So'nggi bosqich: <b>Portfolio yoki Rezyume</b>\n\n"
        "Siz bir yoki bir nechta fayl (PDF, rasm, Word) yoki havola (link) yuborishingiz mumkin.\n\n"
        "Fayllarni birin-ketin yuboring. Barcha materiallarni yuborib bo'lgach yoki portfolio bo'lmasa, "
        "quyidagi tugmalardan foydalaning:"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_portfolio_keyboard(0))
    await state.set_state(ApplicantForm.portfolio)
    await callback.answer()

# 17. Portfolio o'tkazib yuborilganda
@anketa_router.callback_query(F.data == "port:skip", ApplicantForm.portfolio)
async def process_portfolio_skip(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("portfolio_files") and not data.get("portfolio_links"):
        await state.update_data(portfolio="Kiritilmadi")
    else:
        files = data.get("portfolio_files", [])
        links = data.get("portfolio_links", [])
        parts = []
        if links:
            parts.append("Havolalar: " + ", ".join(links))
        if files:
            parts.append(f"{len(files)} ta fayl")
        await state.update_data(portfolio="; ".join(parts))

    await show_confirmation(callback.message, state, is_edit=True)
    await callback.answer()

# 17. Portfolio yuklab bo'linganda ("Tayyor, davom etish")
@anketa_router.callback_query(F.data == "port:done", ApplicantForm.portfolio)
async def process_portfolio_done(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    files = data.get("portfolio_files", [])
    links = data.get("portfolio_links", [])
    if files or links:
        parts = []
        if links:
            parts.append("Havolalar: " + ", ".join(links))
        if files:
            parts.append(f"{len(files)} ta fayl biriktirilgan")
        await state.update_data(portfolio="; ".join(parts))
    else:
        await state.update_data(portfolio="Kiritilmadi")

    await show_confirmation(callback.message, state, is_edit=True)
    await callback.answer()

# 17. Portfolio fayl yoki matn ko'rinishida yuborilganda
@anketa_router.message(ApplicantForm.portfolio)
async def process_portfolio_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = list(data.get("portfolio_files", []))
    links = list(data.get("portfolio_links", []))
    item_desc = ""

    if message.document:
        doc = message.document
        fname = doc.file_name or "Hujjat.pdf"
        files.append({
            "type": "document",
            "file_id": doc.file_id,
            "file_name": fname
        })
        item_desc = f"📄 Hujjat ({fname})"
    elif message.photo:
        photo = message.photo[-1]
        files.append({
            "type": "photo",
            "file_id": photo.file_id,
            "file_name": "Rasm.jpg"
        })
        item_desc = "🖼 Rasm"
    elif message.text:
        text_val = message.text.strip()
        links.append(text_val)
        display_link = text_val[:35] + "..." if len(text_val) > 35 else text_val
        item_desc = f"🔗 Havola ({display_link})"
    else:
        await message.answer("Iltimos, fayl (PDF, rasm) yoki havola (link) yuboring:")
        return

    await state.update_data(portfolio_files=files, portfolio_links=links)
    total_count = len(files) + len(links)

    reply_text = (
        f"✅ <b>{item_desc} qabul qilindi!</b>\n\n"
        f"Hozirgacha yuklangan jami materiallar: <b>{total_count} ta</b>\n\n"
        "Yana fayl yoki havola yuborishingiz mumkin. "
        "Barcha fayllarni yuborib bo'lgach, <b>«✅ Tayyor, davom etish»</b> tugmasini bosing:"
    )
    await message.answer(
        reply_text,
        parse_mode="HTML",
        reply_markup=get_portfolio_keyboard(total_count)
    )

async def show_confirmation(message: types.Message, state: FSMContext, is_edit: bool = False):
    """Anketa to'ldirib bo'lingach, minimalist xulosa va tasdiqlash tugmasini ko'rsatish"""
    data = await state.get_data()
    summary = format_summary(data)
    confirm_text = (
        f"{summary}\n\n"
        "Barcha ma'lumotlar to'g'rimi? Ma'qul bo'lsa <b>Tasdiqlash va Yuborish</b> tugmasini bosing:"
    )

    if is_edit:
        await message.edit_text(confirm_text, parse_mode="HTML", reply_markup=get_confirm_keyboard())
    else:
        await message.answer(confirm_text, parse_mode="HTML", reply_markup=get_confirm_keyboard())
    await state.set_state(ApplicantForm.confirm)

# 18. Tasdiqlash yoki qayta boshlash
@anketa_router.callback_query(F.data.startswith("confirm:"), ApplicantForm.confirm)
async def process_confirm(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    action = callback.data.split(":")[1]

    if action == "restart":
        await state.clear()
        text = (
            "Anketa bekor qilindi.\n\n"
            "Qaytadan boshlash uchun yo'nalishni tanlang:"
        )
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_directions_keyboard())
        await state.set_state(ApplicantForm.direction)
        await callback.answer("Qaytadan boshlandi.")
        return

    # Tasdiqlash - DB ga saqlash
    data = await state.get_data()
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username

    # DB ga portfolio matnini chiroyli yozish
    files = data.get("portfolio_files", [])
    links = data.get("portfolio_links", [])
    if files or links:
        parts = []
        if links:
            parts.append("Havolalar: " + ", ".join(links))
        if files:
            fnames = [f.get("file_name", "Fayl") for f in files]
            parts.append(f"{len(files)} ta fayl (" + ", ".join(fnames) + ")")
        data["portfolio"] = "; ".join(parts)
    elif not data.get("portfolio"):
        data["portfolio"] = "Kiritilmadi"

    applicant_id = await add_applicant(data)
    portfolio_files = list(data.get("portfolio_files", []))
    applicant_name = data.get("full_name", "Nomzod")

    await state.clear()

    # Nomzodga xabar
    success_text = (
        "<b>Arizangiz muvaffaqiyatli qabul qilindi.</b>\n\n"
        f"Anketa raqami: <b>#{applicant_id}</b>\n\n"
        "Kompaniyamiz mutaxassislari arizangizni ko'rib chiqib, "
        "tez orada siz bilan bog'lanishadi."
    )
    await callback.message.edit_text(success_text, parse_mode="HTML")
    await callback.answer("Arizangiz qabul qilindi.")

    # HR admin yoki guruhga xabar yuborish
    summary = format_summary(data, applicant_id=applicant_id)
    user_mention = f"@{callback.from_user.username}" if callback.from_user.username else f"<a href='tg://user?id={callback.from_user.id}'>{applicant_name}</a>"
    hr_card = (
        f"<b>Yangi ariza kelib tushdi:</b>\n"
        f"Nomzod: {user_mention}\n\n"
        f"{summary}"
    )

    hr_markup = get_hr_decision_keyboard(applicant_id)

    # Shuningdek, barcha adminlar va HR kanal
    recipient_ids = set(ADMIN_IDS)
    try:
        db_admins = await get_all_admins_db()
        for a in db_admins:
            recipient_ids.add(a["user_id"])
    except Exception:
        pass

    target_chats = list(recipient_ids)
    if HR_CHANNEL_ID:
        target_chats.append(HR_CHANNEL_ID)

    # 1. Anketa kartasini yuborish
    for chat_id in target_chats:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=hr_card,
                parse_mode="HTML",
                reply_markup=hr_markup if chat_id in recipient_ids else None
            )
        except Exception as e:
            print(f"Anketa kartasini yuborishda xato ({chat_id}): {e}")

    # 2. Barcha yuklangan portfolio fayllarini (PDF, rasm) yuborish
    if portfolio_files:
        for chat_id in target_chats:
            for idx, file_info in enumerate(portfolio_files, start=1):
                caption = (
                    f"📎 <b>#{applicant_id} {applicant_name}</b>\n"
                    f"Portfolio fayli ({idx}/{len(portfolio_files)}): {file_info.get('file_name', 'Fayl')}"
                )
                try:
                    if file_info["type"] == "document":
                        await bot.send_document(
                            chat_id=chat_id,
                            document=file_info["file_id"],
                            caption=caption,
                            parse_mode="HTML"
                        )
                    elif file_info["type"] == "photo":
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=file_info["file_id"],
                            caption=caption,
                            parse_mode="HTML"
                        )
                except Exception as e:
                    print(f"Portfolio faylini {chat_id} ga yuborishda xatolik: {e}")

