# 🤖 HR Bot - Kompaniya Xodimlarini Saralash Telegram Boti

Mazkur bot kompaniyaga yangi xodimlarni jalb qilish va rekruting (HR) jarayonini to'liq avtomatlashtirish uchun maxsus ishlab chiqilgan. 

### ⚡️ Asosiy afzalligi:
Hozirgi nomzodlar va yoshlarning erinchoqligini inobatga olgan holda, bot **qo'lda deyarli hech narsa yozdirmaydi**. Barcha jarayon — yo'nalish tanlash, dasturlarni bilish foizlari (0% dan 100% gacha), yosh, hudud, tajriba va boshqa ma'lumotlar **bitta tugmani bosish (1-click)** orqali 1-2 daqiqada to'ldiriladi!

---

## 🎯 Bot Imkoniyatlari

1. **Yo'nalishlar (Vakansiyalar):**
   - 🎨 **Dizayner** (Photoshop, Illustrator / Corel, Figma, Canva, 3D...)
   - 🏛 **Arxitektor** (AutoCAD, 3D MAX, Revit, Lumion, SketchUp, D5...)
   - 💻 **IT mutaxassis** (Linux/Windows, Tarmoq/Sysadmin, Dasturlash, Ma'lumotlar bazasi, AI...)
   - 💼 **Menejer** (Excel, Word, PowerPoint, CRM tizimlar, AI...)
   - 🎬 **Video montajchi** (Premiere Pro, After Effects, DaVinci, Photoshop, CapCut...)

2. **Dasturlar bo'yicha dinamik foizlar:**
   - Har bir yo'nalish tanlanganda faqat o'sha kasbga xos dasturlar chiqadi.
   - Har bir dastur uchun: `[0%] [25%] [50%] [75%] [100%]` tugmalari mavjud.
   - Bosilishi bilan bir zumda keyingi dasturga o'tadi.

3. **Tezkor shaxsiy ma'lumotlar:**
   - **F.I.O:** Telegram profil nomini 1 tugma bilan tanlash yoki o'zi yozish.
   - **Telefon raqam:** `[📱 Raqamni yuborish]` tugmasi (kontakt ulashish).
   - **Yosh toifasi:** `[18-21]` `[22-25]` `[26-30]` `[31-38]` `[38+]`.
   - **Hudud:** Toshkent shahri va barcha 13 ta viloyat tugmalari.
   - **Yashash sharoiti:** Hovli / Kvartira (Dom).
   - **Ma'lumoti:** Oliy, O'rta maxsus, O'rta, Talaba.
   - **Ish tajribasi:** Yangi boshlovchi, 1 yilgacha, 1-3 yil, 3-5 yil, 5+ yil.
   - **Tillar:** Rus tili va Ingliz tili darajalari.
   - **Qo'shimcha:** Shaxsiy noutbuk/PC, Haydovchilik/Avtomobil, Komandirovka va qo'shimcha ishlashga rozilik.
   - **Kutilayotgan oylik:** 3-5 mln, 5-8 mln, 8-12 mln, 12-20 mln, 20+ mln, Kelishilgan holda.
   - **Portfolio:** Havola, rasm, PDF fayl yoki `[⏭ O'tkazib yuborish]`.

4. **HR & Admin paneli (`/admin`):**
   - 📊 **Excelga eksport:** Barcha arizalarni chiroyli dizayndagi `.xlsx` jadvali ko'rinishida 1 ta tugma bilan yuklab olish.
   - 📈 **Statistika:** Jami nomzodlar soni, yo'nalishlar va holatlar bo'yicha filtrlash.
   - ⚡️ **Tezkor qaror qabul qilish:** HR xodimi har bir kelgan arizaning ostidagi `[✅ Suhbatga chaqirish]` yoki `[❌ Rad etish]` tugmasini bossa, nomzodga avtomatik tarzda Telegram orqali xushxabar yoki rad javobi boradi.

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Bot tokenini olish:
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring va botingiz nomini belgilang.
3. BotFather bergan **Token**ni nusxalab oling.

### 2. O'zingizning Telegram ID raqamingizni aniqlash:
1. [@userinfobot](https://t.me/userinfobot) botiga `/start` yuborib, o'z ID raqamingizni bilib oling (masalan: `123456789`).

### 3. `.env` faylini to'ldirish:
Loyihadagi `.env` faylini oching va ma'lumotlaringizni kiriting:

```env
BOT_TOKEN=1234567890:AAHxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_IDS=123456789
HR_CHANNEL_ID=
DB_PATH=database.db
```
*(Agar bir nechta admin bo'lsa, ID larni vergul bilan yozing: `123456789,987654321`)*

### 4. Kutubxonalarni o'rnatish:
Terminal yoki buyruqlar satrida:
```bash
pip install -r requirements.txt
```

### 5. Botni ishga tushirish:
```bash
python main.py
```

---

## 📁 Loyiha Tuzilmasi

```text
HR-bot/
├── config.py                 # Bot konfiguratsiyasi va sozlamalar
├── database.py               # SQLite ma'lumotlar bazasi (aiosqlite)
├── main.py                   # Botni yurgizuvchi asosiy fayl
├── requirements.txt          # Kerakli Python kutubxonalari
├── .env                      # Muhit o'zgaruvchilari (Token va ID lar)
├── data/
│   └── constants.py          # Kasblar, dasturlar va variantlar
├── keyboards/
│   ├── inline.py             # Barcha inline tugmalar (kasblar, foizlar...)
│   └── reply.py              # Kontakt va ism tugmalari
├── states/
│   └── applicant.py          # FSM holatlari
├── handlers/
│   ├── start.py              # /start buyrug'i
│   ├── anketa.py             # Anketa savollari va bosqichlari
│   └── admin.py              # Admin paneli, Excel yuklash, qarorlar
└── utils/
    └── excel_exporter.py     # Ma'lumotlarni Excelga (.xlsx) chiroyli eksport qilish
```
