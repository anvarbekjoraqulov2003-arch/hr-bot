import asyncio
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from database import init_db, add_applicant, get_all_applicants, get_stats, update_applicant_status

from utils.excel_exporter import export_applicants_to_excel
from keyboards.inline import (
    get_directions_keyboard, get_program_percentage_keyboard,
    get_age_keyboard, get_regions_keyboard, get_housing_keyboard,
    get_education_keyboard, get_experience_keyboard, get_language_keyboard,
    get_device_keyboard, get_driving_keyboard, get_trip_keyboard,
    get_overtime_keyboard, get_salary_keyboard, get_skip_keyboard,
    get_confirm_keyboard, get_admin_keyboard, get_hr_decision_keyboard
)
from keyboards.reply import get_phone_keyboard, get_name_suggestion_keyboard
from data.constants import DIRECTIONS, DIRECTION_PROGRAMS

async def run_tests():
    print("1. Testing database initialization...")
    await init_db()
    print("Database initialized successfully!")

    print("\n2. Testing adding an applicant...")
    sample_candidate = {
        "user_id": 998901234567,
        "username": "dizayner_pro",
        "full_name": "Azizbek Rahimov",
        "phone": "+998901234567",
        "direction": "🎨 Dizayner",
        "programs": {
            "Adobe Photoshop": "100%",
            "Adobe Illustrator / Corel Draw": "75%",
            "Figma": "100%",
            "Canva": "100%",
            "3D dizayn / Qo'shimcha dasturlar": "50%"
        },
        "age_range": "22 - 25 yosh",
        "region": "Toshkent shahri",
        "housing": "🏢 Kvartira (Dom)",
        "education": "🎓 Oliy ma'lumot",
        "experience": "💼 1 - 3 yil",
        "russian_level": "🟢 Yaxshi",
        "english_level": "🔵 Erkin / A'lo",
        "device": "💻 Noutbukim bor",
        "driving": "🚗 Avtomobil + Guvohnoma bor",
        "trip_ready": "✅ Ha, safarlarga tayyorman",
        "overtime_ready": "✅ Ha, zarurat bo'lsa roziman",
        "expected_salary": "💰 8 - 12 mln so'm",
        "portfolio": "https://behance.net/sample_portfolio"
    }
    
    app_id = await add_applicant(sample_candidate)
    print(f"Candidate added with ID: {app_id}")

    print("\n3. Testing fetching applicants...")
    all_applicants = await get_all_applicants()
    print(f"Total applicants in DB: {len(all_applicants)}")
    assert len(all_applicants) >= 1
    first = all_applicants[0]
    print(f"First applicant: {first['full_name']} | {first['direction']} | {first['phone']}")

    print("\n4. Testing statistics...")
    stats = await get_stats()
    print(f"Stats: {stats}")

    print("\n5. Testing status update...")
    await update_applicant_status(app_id, "accepted")
    stats_updated = await get_stats()
    print(f"Updated status stats: {stats_updated['by_status']}")

    print("\n6. Testing Excel export...")
    test_excel = "test_export.xlsx"
    filepath = export_applicants_to_excel(all_applicants, test_excel)
    print(f"Excel created at: {filepath}")
    assert os.path.exists(filepath)
    print(f"Excel file size: {os.path.getsize(filepath)} bytes")

    print("\n7. Testing all keyboards creation...")
    assert get_directions_keyboard() is not None
    assert get_program_percentage_keyboard(0) is not None
    assert get_age_keyboard() is not None
    assert get_regions_keyboard() is not None
    assert get_housing_keyboard() is not None
    assert get_education_keyboard() is not None
    assert get_experience_keyboard() is not None
    assert get_language_keyboard('ru') is not None
    assert get_device_keyboard() is not None
    assert get_driving_keyboard() is not None
    assert get_trip_keyboard() is not None
    assert get_overtime_keyboard() is not None
    assert get_salary_keyboard() is not None
    assert get_skip_keyboard() is not None
    assert get_confirm_keyboard() is not None
    assert get_admin_keyboard() is not None
    assert get_hr_decision_keyboard(1) is not None
    assert get_phone_keyboard() is not None
    assert get_name_suggestion_keyboard("Ali Valiyev") is not None
    print("All keyboards rendered successfully!")

    # Clean up test excel
    if os.path.exists(test_excel):
        os.remove(test_excel)
    print("\n>>> ALL TESTS PASSED! <<<")

if __name__ == "__main__":
    asyncio.run(run_tests())
