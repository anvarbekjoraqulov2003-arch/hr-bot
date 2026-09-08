from aiogram.fsm.state import State, StatesGroup

class ApplicantForm(StatesGroup):
    direction = State()          # Yo'nalish tanlash (Dizayner, Arxitektor, IT, ...)
    programs = State()           # Dasturlar bo'yicha foizlarni belgilash
    full_name = State()          # F.I.O (Telegram ismini olish yoki yozish)
    phone = State()              # Telefon raqam (kontakt ulashish yoki yozish)
    age_range = State()          # Yosh toifasi
    region = State()             # Yashash hududi
    housing = State()            # Yashash sharoiti (Hovli / Dom)
    education = State()          # Ma'lumoti (Oliy, O'rta maxsus...)
    experience = State()         # Ish tajribasi
    russian_level = State()      # Rus tili darajasi
    english_level = State()      # Ingliz tili darajasi
    device = State()             # Kompyuter mavjudligi
    driving = State()            # Haydovchilik guvohnomasi / Mashina
    trip_ready = State()         # Xizmat safari (komandirovka)
    overtime_ready = State()     # Ishdan keyin qolib ishlash
    expected_salary = State()    # Kutilayotgan oylik maosh
    portfolio = State()          # Portfolio yoki Rezyume (fayl / link / o'tkazish)
    confirm = State()            # Anketani tasdiqlash

class AdminState(StatesGroup):
    waiting_for_admin_id = State()

