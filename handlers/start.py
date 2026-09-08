from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_directions_keyboard
from states.applicant import ApplicantForm

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    welcome_text = (


        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        "Kompaniyamizning xodimlarni saralash (HR) botiga xush kelibsiz.\n"
        "Ushbu bot orqali anketani 1-2 daqiqa ichida hech narsa yozmasdan, "
        "faqat kerakli tugmalarni tanlash orqali tez va qulay to'ldirishingiz mumkin.\n\n"
        "Boshlash uchun o'zingiz topshirmoqchi bo'lgan <b>yo'nalishni tanlang</b>:"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_directions_keyboard())
    await state.set_state(ApplicantForm.direction)

@start_router.message(Command("anketa"))
async def cmd_anketa(message: types.Message, state: FSMContext):
    await cmd_start(message, state)
