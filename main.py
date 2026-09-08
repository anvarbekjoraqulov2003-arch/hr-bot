import asyncio
import logging
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from aiogram import Bot, Dispatcher

from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, get_all_admins_db
from handlers.start import start_router
from handlers.anketa import anketa_router
from handlers.admin import admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def setup_bot_commands(bot: Bot):
    # 1. Oddiy foydalanuvchilar uchun komandalar (faqat start va anketa, admin yo'q!)
    user_commands = [
        BotCommand(command="start", description="Anketani boshlash"),
        BotCommand(command="anketa", description="Qayta to'ldirish")
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    # 2. Adminlar uchun maxsus komandalar (faqat adminlarning shaxsiy menyusida ko'rinadi)
    admin_commands = [
        BotCommand(command="start", description="Anketani boshlash"),
        BotCommand(command="anketa", description="Qayta to'ldirish"),
        BotCommand(command="admin", description="HR Admin paneli")
    ]

    all_admin_ids = set(ADMIN_IDS)
    try:
        db_admins = await get_all_admins_db()
        for a in db_admins:
            all_admin_ids.add(a["user_id"])
    except Exception:
        pass

    for aid in all_admin_ids:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=aid))
        except Exception:
            pass


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error(
            "\n"
            "==========================================================\n"
            "XATOLIK: BOT_TOKEN ko'rsatilmagan!\n"
            "Iltimos, .env faylini oching va @BotFather dan olgan\n"
            "Telegram bot tokeningizni BOT_TOKEN=... qatoriga yozing.\n"
            "==========================================================\n"
        )
        return

    # Ma'lumotlar bazasini ishga tushirish
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyorlandi.")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ro'yxatga olish
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(anketa_router)

    # Bot buyruqlarini sozlash
    await setup_bot_commands(bot)

    # Render.com bulutli serveri uchun web-server (PORT berilgan bo'lsa)
    port_str = os.getenv("PORT")
    web_runner = None
    if port_str:
        try:
            from aiohttp import web
            async def handle_ping(request):
                return web.Response(text="LUMARC HR Bot is active and running 24/7!")

            web_app = web.Application()
            web_app.router.add_get("/", handle_ping)
            web_app.router.add_get("/health", handle_ping)
            web_runner = web.AppRunner(web_app)
            await web_runner.setup()
            site = web.TCPSite(web_runner, "0.0.0.0", int(port_str))
            await site.start()
            logger.info(f"Render.com web serveri {port_str}-portda ishga tushdi.")
        except Exception as e:
            logger.warning(f"Web serverni ishga tushirishda xato: {e}")

    logger.info("HR Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        if web_runner:
            await web_runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
