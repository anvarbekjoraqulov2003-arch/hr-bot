import os
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from config import ADMIN_IDS
from database import (
    get_all_applicants, get_stats, get_applicant_by_id, update_applicant_status,
    add_admin_db, remove_admin_db, get_all_admins_db, is_admin_db
)
from utils.excel_exporter import export_applicants_to_excel
from keyboards.inline import (
    get_admin_keyboard, get_hr_decision_keyboard,
    get_admins_manage_keyboard, get_cancel_admin_keyboard
)
from states.applicant import AdminState
from handlers.anketa import format_progress_bar

def format_applicant_card(app: dict) -> str:
    """Ma'lumotlar bazasidagi nomzodni Telegramda minimalist va toza kartochka qilib ko'rsatish"""
    programs_raw = app.get("programs_skill", "")
    programs_lines = []
    if programs_raw:
        for item in programs_raw.split(","):
            item = item.strip()
            if ":" in item:
                prog_name, pct = item.split(":", 1)
                bar = format_progress_bar(pct.strip())
                programs_lines.append(f"  • {prog_name.strip()}:\n    <code>[{bar}]</code>")
            else:
                programs_lines.append(f"  • {item}")
        programs_text = "\n".join(programs_lines)
    else:
        programs_text = "  <i>Ko'rsatilmadi</i>"

    status_map = {
        "new": "Ko'rib chiqilmoqda",
        "accepted": "Suhbatga chaqirilgan",
        "rejected": "Rad etilgan"
    }
    status_title = status_map.get(app.get("status"), "Ko'rib chiqilmoqda")
    username_str = f"@{app.get('username')}" if app.get('username') else "Mavjud emas"

    card = (
        f"📄 <b>ARIZA #{app.get('id')} — {status_title}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Yo'nalish:</b> {app.get('direction')}\n"
        f"<b>Nomzod:</b> {username_str}\n"
        f"<b>Topshirilgan vaqt:</b> {app.get('created_at')}\n\n"
        f"<b>Shaxsiy ma'lumotlar:</b>\n"
        f"  • F.I.O: <b>{app.get('full_name')}</b>\n"
        f"  • Telefon: <code>{app.get('phone')}</code>\n"
        f"  • Yoshi: {app.get('age_range')}\n"
        f"  • Hudud: {app.get('region')}\n"
        f"  • Yashash joyi: {app.get('housing')}\n"
        f"  • Ma'lumoti: {app.get('education')}\n"
        f"  • Ish tajribasi: {app.get('experience')}\n\n"
        f"<b>Dasturlar va ko'nikmalar:</b>\n"
        f"{programs_text}\n\n"
        f"<b>Tillar:</b>\n"
        f"  • Rus tili: {app.get('russian_level')}\n"
        f"  • Ingliz tili: {app.get('english_level')}\n\n"
        f"<b>Qo'shimcha ma'lumotlar:</b>\n"
        f"  • Kompyuter: {app.get('device')}\n"
        f"  • Haydovchilik: {app.get('driving')}\n"
        f"  • Xizmat safari: {app.get('trip_ready')}\n"
        f"  • Qo'shimcha ishlash: {app.get('overtime_ready')}\n\n"
        f"<b>Kutilayotgan maosh:</b> {app.get('expected_salary')}\n"
        f"<b>Portfolio:</b> {app.get('portfolio')}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    return card

admin_router = Router()

async def check_is_admin(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    return await is_admin_db(user_id)

@admin_router.message(Command("admin"))
async def cmd_admin(message: types.Message, state: FSMContext):
    await state.clear()
    if not await check_is_admin(message.from_user.id):
        # Oddiy foydalanuvchiga javob bermaymiz (faqat haqiqiy adminlarga ko'rinadi)
        return

    stats = await get_stats()
    total = stats.get("total", 0)


    text = (
        "🔐 <b>HR ADMIN BOSHQARUV PANELI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Sizning Telegram ID: <code>{message.from_user.id}</code>\n"
        f"📊 Jami arizalar soni: <b>{total} ta</b>\n\n"
        "Quyidagi tugmalar orqali boshqarishingiz mumkin:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_keyboard())

@admin_router.callback_query(F.data == "admin:back")
async def process_admin_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    stats = await get_stats()
    total = stats.get("total", 0)

    text = (
        "🔐 <b>HR ADMIN BOSHQARUV PANELI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 Sizning Telegram ID: <code>{callback.from_user.id}</code>\n"
        f"📊 Jami arizalar soni: <b>{total} ta</b>\n\n"
        "Quyidagi tugmalar orqali boshqarishingiz mumkin:"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin:excel")
async def process_export_excel(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    await callback.answer("Excel fayl tayyorlanmoqda... ⏳")
    applicants = await get_all_applicants()
    if not applicants:
        await callback.message.answer("Hozircha hech qanday ariza kelib tushmagan.")
        return

    stats = await get_stats()
    total = stats.get("total", 0)
    by_status = stats.get("by_status", {})
    new_c = by_status.get("new", 0)
    acc_c = by_status.get("accepted", 0)
    rej_c = by_status.get("rejected", 0)

    filename = "nomzodlar_bazasi.xlsx"
    filepath = export_applicants_to_excel(applicants, filename)

    caption = (
        "📊 <b>NOMZODLAR BAZASI (EXCEL JADVAL)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Jami nomzodlar: <b>{total} ta</b>\n"
        f"🟡 Yangi ko'rilmagan: <b>{new_c} ta</b>\n"
        f"🟢 Suhbatga taklif qilingan: <b>{acc_c} ta</b>\n"
        f"🔴 Rad etilgan: <b>{rej_c} ta</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📁 <i>Jadvalda barcha ustunlar va qatorlar aniq chegaralar (granitsa), "
        "har xil ranglar va dasturlar bo'yicha chiroyli tartib bilan ajratilgan.</i>"
    )

    doc = FSInputFile(filepath, filename="Nomzodlar_HR_LUMARC.xlsx")
    await callback.message.answer_document(
        document=doc,
        caption=caption,
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data == "admin:recent")
async def process_recent_applicants(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    applicants = await get_all_applicants()
    if not applicants:
        await callback.answer("Hozircha hech qanday ariza yo'q.", show_alert=True)
        return

    await callback.answer("Oxirgi arizalar chiqarilmoqda... 📋")
    
    recent = applicants[:5]
    await callback.message.answer(
        f"📋 <b>Oxirgi {len(recent)} ta ariza:</b>\n"
        "<i>(Har bir arizani ko'rib chiqib, to'g'ridan-to'g'ri Telegramdan qaror qabul qilishingiz mumkin)</i>",
        parse_mode="HTML"
    )

    for app in recent:
        card = format_applicant_card(app)
        markup = get_hr_decision_keyboard(app["id"]) if app.get("status") == "new" else None
        await callback.message.answer(card, parse_mode="HTML", reply_markup=markup)

@admin_router.callback_query(F.data == "admin:stats")
async def process_show_stats(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    stats = await get_stats()
    total = stats.get("total", 0)
    by_dir = stats.get("by_direction", {})
    by_status = stats.get("by_status", {})

    dir_text = ""
    for d, count in by_dir.items():
        dir_text += f"  • {d}: <b>{count}</b>\n"
    if not dir_text:
        dir_text = "  Arizalar mavjud emas\n"

    status_map = {
        "new": "🟡 Yangi ko'rilmagan",
        "accepted": "🟢 Suhbatga taklif qilingan",
        "rejected": "🔴 Rad etilgan"
    }
    status_text = ""
    for s, count in by_status.items():
        s_title = status_map.get(s, s)
        status_text += f"  • {s_title}: <b>{count}</b>\n"
    if not status_text:
        status_text = "  Arizalar mavjud emas\n"

    text = (
        "📈 <b>BATAFSIL STATISTIKA</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Jami nomzodlar:</b> {total} ta\n\n"
        f"🎯 <b>Yo'nalishlar bo'yicha:</b>\n{dir_text}\n"
        f"📌 <b>Holat bo'yicha:</b>\n{status_text}"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_keyboard())
    await callback.answer()

# ----------------- ADMINLAR BOSHQARUVI -----------------

@admin_router.callback_query(F.data == "admin:manage_admins")
async def process_manage_admins(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    # Asosiy adminlarni DB da borligini ta'minlash
    for aid in ADMIN_IDS:
        await add_admin_db(aid, "", f"Admin {aid}")
    await add_admin_db(callback.from_user.id, callback.from_user.username or "", callback.from_user.full_name)

    admins = await get_all_admins_db()
    text = (
        "👥 <b>ADMINLAR VA HR XODIMLAR BOSHQARUVI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"Hozirda ro'yxatda <b>{len(admins)} ta</b> admin mavjud.\n\n"
        "Barcha qo'shilgan adminlar:\n"
        "• Yangi kelgan arizalarni Telegramda qabul qiladi\n"
        "• Excel faylni yuklab olishi mumkin\n"
        "• Nomzodni suhbatga chaqirish yoki rad etish huquqiga ega\n\n"
        "Adminni o'chirish uchun uning yonidagi 🗑 tugmasini bosing yoki yangi admin qo'shing:"
    )
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admins_manage_keyboard(admins, callback.from_user.id)
    )
    await callback.answer()

@admin_router.callback_query(F.data == "admin:add_admin")
async def process_add_admin_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    text = (
        "➕ <b>Yangi admin qo'shish:</b>\n\n"
        "Qo'shmoqchi bo'lgan xodimingizning <b>Telegram ID raqamini</b> yozib yuboring:\n"
        "<i>(yoki uning Telegramdagi biror xabarini shu yerga <b>Forward</b> qilib yuboring)</i>\n\n"
        "<i>Eslatma: ID raqamni bilish uchun u xodim @userinfobot ga kirib /start bosishi kifoya.</i>"
    )
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_cancel_admin_keyboard())
    await state.set_state(AdminState.waiting_for_admin_id)
    await callback.answer()

@admin_router.message(AdminState.waiting_for_admin_id)
async def process_new_admin_input(message: types.Message, state: FSMContext, bot: Bot):
    new_id = None
    new_username = ""
    new_name = ""

    if message.forward_from:
        new_id = message.forward_from.id
        new_username = message.forward_from.username or ""
        new_name = message.forward_from.full_name
    elif message.text and message.text.strip().isdigit():
        new_id = int(message.text.strip())
        new_name = f"Admin {new_id}"
    else:
        await message.answer(
            "Iltimos, to'g'ri Telegram ID raqamini (faqat sonlar) kiriting "
            "yoki xodim yozgan xabarni Forward qilib yuboring:",
            reply_markup=get_cancel_admin_keyboard()
        )
        return

    await add_admin_db(new_id, new_username, new_name)
    if new_id not in ADMIN_IDS:
        ADMIN_IDS.append(new_id)

    await state.clear()
    await message.answer(
        f"✅ <b>Yangi admin muvaffaqiyatli qo'shildi!</b>\n\n"
        f"• ID: <code>{new_id}</code>\n"
        f"• Ism: <b>{new_name}</b>\n\n"
        "Endi ushbu xodim ham yangi arizalarni qabul qilishi va /admin panelidan foydalanishi mumkin.",
        parse_mode="HTML"
    )

    # Yangi adminga bildirishnoma va maxsus menyu
    try:
        from aiogram.types import BotCommand, BotCommandScopeChat
        admin_commands = [
            BotCommand(command="start", description="Anketani boshlash"),
            BotCommand(command="anketa", description="Qayta to'ldirish"),
            BotCommand(command="admin", description="HR Admin paneli")
        ]
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=new_id))

        await bot.send_message(
            chat_id=new_id,
            text=(
                "Assalomu alaykum! Siz kompaniyamizning HR botiga admin sifatida qo'shildingiz.\n\n"
                "Endi siz yangi nomzodlar anketalarini qabul qilib, /admin paneli orqali ularni ko'rib chiqishingiz mumkin."
            )
        )
    except Exception:
        pass

@admin_router.callback_query(F.data.startswith("admin:del_admin:"))
async def process_del_admin(callback: types.CallbackQuery):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    del_id = int(callback.data.split(":")[2])
    await remove_admin_db(del_id)
    if del_id in ADMIN_IDS:
        ADMIN_IDS.remove(del_id)

    try:
        from aiogram.types import BotCommandScopeChat
        await callback.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=del_id))
    except Exception:
        pass

    await callback.answer("Admin muvaffaqiyatli o'chirildi.", show_alert=True)

    admins = await get_all_admins_db()
    text = (
        "👥 <b>ADMINLAR VA HR XODIMLAR BOSHQARUVI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"Hozirda ro'yxatda <b>{len(admins)} ta</b> admin mavjud.\n\n"
        "Adminni o'chirish uchun uning yonidagi 🗑 tugmasini bosing yoki yangi admin qo'shing:"
    )
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admins_manage_keyboard(admins, callback.from_user.id)
    )

# ----------------- HR QARORLARI -----------------

@admin_router.callback_query(F.data.startswith("hr_decision:"))
async def process_hr_decision(callback: types.CallbackQuery, bot: Bot):
    if not await check_is_admin(callback.from_user.id):
        await callback.answer("Faqat HR xodimlar ushbu tugmani bosa oladi!", show_alert=True)
        return

    parts = callback.data.split(":")
    decision = parts[1]
    applicant_id = int(parts[2])

    applicant = await get_applicant_by_id(applicant_id)
    if not applicant:
        await callback.answer("Nomzod topilmadi!", show_alert=True)
        return

    admin_username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name

    if decision == "accept":
        await update_applicant_status(applicant_id, "accepted")
        await callback.answer("Nomzod suhbatga chaqirildi!")

        try:
            user_msg = (
                "<b>Tabriklaymiz!</b>\n\n"
                f"Hurmatli <b>{applicant.get('full_name')}</b>, sizning kompaniyamizga topshirgan anketangiz "
                "HR mutaxassislarimiz tomonidan ma'qullandi.\n\n"
                "Siz <b>suhbat (intervyu)</b> bosqichiga taklif etilasiz! "
                "Tez orada mas'ul xodimimiz siz bilan bog'lanadi."
            )
            await bot.send_message(chat_id=applicant["user_id"], text=user_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Nomzodga xabar yuborib bo'lmadi: {e}")

        new_text = callback.message.text + f"\n\n<b>QAROR: Suhbatga chaqirildi ({admin_username})</b>"
        await callback.message.edit_text(new_text, parse_mode="HTML", reply_markup=None)

    elif decision == "reject":
        await update_applicant_status(applicant_id, "rejected")
        await callback.answer("Nomzod arizasi rad etildi.")

        try:
            user_msg = (
                f"Hurmatli <b>{applicant.get('full_name')}</b>,\n\n"
                "Kompaniyamizga qiziqish bildirganingiz uchun tashakkur bildiramiz. "
                "Afsuski, ayni vaqtdagi ochiq o'rin bo'yicha talablarimizga to'liq mos kelmadingiz.\n\n"
                "Kelgusi faoliyatingizda muvaffaqiyat tilaymiz!"
            )
            await bot.send_message(chat_id=applicant["user_id"], text=user_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Nomzodga xabar yuborib bo'lmadi: {e}")

        new_text = callback.message.text + f"\n\n<b>QAROR: Rad etildi ({admin_username})</b>"
        await callback.message.edit_text(new_text, parse_mode="HTML", reply_markup=None)
