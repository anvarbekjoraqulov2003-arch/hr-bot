from typing import Dict, List

# Vakansiya yo'nalishlari (Minimalist)
DIRECTIONS = {
    "designer": "Dizayner",
    "architect": "Arxitektor",
    "it_specialist": "IT mutaxassis",
    "manager": "Menejer",
    "video_editor": "Video montajchi"
}

# Har bir yo'nalish uchun dasturlar ro'yxati
DIRECTION_PROGRAMS: Dict[str, List[str]] = {
    "designer": [
        "Adobe Photoshop",
        "Adobe Illustrator / Corel Draw",
        "Figma",
        "Canva",
        "3D dizayn / Qo'shimcha dasturlar"
    ],
    "architect": [
        "Auto CAD",
        "3D MAX",
        "Revit",
        "Lumion",
        "SketchUp",
        "D5 Render / Twinmotion"
    ],
    "it_specialist": [
        "Operatsion tizimlar (Linux / Windows)",
        "Tarmoq va tizim administratorligi",
        "Dasturlash (Python / JS / boshqa)",
        "Ma'lumotlar bazasi (SQL / boshqa)",
        "ChatGPT va AI vositalari"
    ],
    "manager": [
        "MS Excel / Google Sheets",
        "MS Word (Hujjatlar)",
        "PowerPoint (Taqdimotlar)",
        "CRM tizimlari (Bitrix/Amo/Trello)",
        "ChatGPT va AI vositalari"
    ],
    "video_editor": [
        "Adobe Premiere PRO",
        "Adobe After Effects",
        "DaVinci Resolve",
        "Adobe Photoshop",
        "CapCut / Adobe Audition"
    ]
}

# Dasturlarni bilish foizlari
PERCENTAGES = ["0%", "25%", "50%", "75%", "100%"]

# Yosh toifalari
AGE_RANGES = [
    "18 - 21 yosh",
    "22 - 25 yosh",
    "26 - 30 yosh",
    "31 - 38 yosh",
    "38+ yosh"
]

# Hududlar (Viloyatlar va Toshkent shahri)
REGIONS = [
    "Toshkent shahri",
    "Toshkent viloyati",
    "Samarqand viloyati",
    "Farg'ona viloyati",
    "Andijon viloyati",
    "Namangan viloyati",
    "Buxoro viloyati",
    "Qashqadaryo viloyati",
    "Surxondaryo viloyati",
    "Xorazm viloyati",
    "Navoiy viloyati",
    "Jizzax viloyati",
    "Sirdaryo viloyati",
    "Qoraqalpog'iston Resp."
]

# Yashash sharoiti
HOUSING_TYPES = [
    "Hovli",
    "Kvartira (Dom)"
]

# Ma'lumoti
EDUCATION_LEVELS = [
    "Oliy ma'lumot",
    "O'rta maxsus (Kollej/Texnikum)",
    "O'rta (Maktab)",
    "Hozir talabaman"
]

# Ish tajribasi
EXPERIENCE_LEVELS = [
    "Tajribasiz (Boshlovchi)",
    "1 yilgacha",
    "1 - 3 yil",
    "3 - 5 yil",
    "5 yildan ortiq"
]

# Til bilish darajalari
LANGUAGE_LEVELS = [
    "Bilmayman",
    "Boshlang'ich",
    "Yaxshi",
    "Erkin / A'lo"
]

# Kompyuter mavjudligi
DEVICE_OPTIONS = [
    "Noutbukim bor",
    "Stol kompyuteri (PC) bor",
    "Kompyuterim yo'q"
]

# Haydovchilik / Avtomobil
DRIVING_OPTIONS = [
    "Avtomobil va guvohnoma bor",
    "Faqat haydovchilik guvohnomam bor",
    "Guvohnomam yo'q"
]

# Komandirovka
TRIP_OPTIONS = [
    "Ha, safarlarga tayyorman",
    "Safarlarga chiqa olmayman"
]

# Ishdan keyin qolib ishlash
OVERTIME_OPTIONS = [
    "Ha, zarurat bo'lsa roziman",
    "Faqat favqulodda hollarda",
    "Qat'iy ish vaqti bo'yicha"
]

# Kutilayotgan maosh
SALARY_OPTIONS = [
    "3 - 5 mln so'm",
    "5 - 8 mln so'm",
    "8 - 12 mln so'm",
    "12 - 20 mln so'm",
    "20+ mln so'm",
    "Suhbatda kelishiladi"
]
