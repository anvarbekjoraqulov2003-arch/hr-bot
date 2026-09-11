import json
import aiosqlite
from typing import Dict, List, Optional, Any
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                direction TEXT NOT NULL,
                programs_skill TEXT,
                age_range TEXT,
                region TEXT,
                housing TEXT,
                education TEXT,
                experience TEXT,
                russian_level TEXT,
                english_level TEXT,
                device TEXT,
                driving TEXT,
                trip_ready TEXT,
                overtime_ready TEXT,
                expected_salary TEXT,
                portfolio TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()



async def add_applicant(data: Dict[str, Any]) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        programs_skill_str = ""
        if isinstance(data.get("programs"), dict):
            # Format as clean readable list
            programs_skill_str = ", ".join([f"{prog}: {pct}" for prog, pct in data["programs"].items()])
        elif data.get("programs"):
            programs_skill_str = str(data.get("programs"))

        portfolio_str = data.get("portfolio", "")
        if not portfolio_str:
            port_files = data.get("portfolio_files", [])
            port_links = data.get("portfolio_links", [])
            if port_files or port_links:
                parts = []
                if port_links:
                    parts.append("Havolalar: " + ", ".join(port_links))
                if port_files:
                    fnames = [f.get("file_name", "Fayl") for f in port_files]
                    parts.append(f"{len(port_files)} ta fayl (" + ", ".join(fnames) + ")")
                portfolio_str = "; ".join(parts)
            else:
                portfolio_str = "Kiritilmadi"

        cursor = await db.execute("""
            INSERT INTO applicants (
                user_id, username, full_name, phone, direction,
                programs_skill, age_range, region, housing, education,
                experience, russian_level, english_level, device,
                driving, trip_ready, overtime_ready, expected_salary,
                portfolio, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("user_id"),
            data.get("username", ""),
            data.get("full_name", ""),
            data.get("phone", ""),
            data.get("direction", ""),
            programs_skill_str,
            data.get("age_range", ""),
            data.get("region", ""),
            data.get("housing", ""),
            data.get("education", ""),
            data.get("experience", ""),
            data.get("russian_level", ""),
            data.get("english_level", ""),
            data.get("device", ""),
            data.get("driving", ""),
            data.get("trip_ready", ""),
            data.get("overtime_ready", ""),
            data.get("expected_salary", ""),
            portfolio_str,
            "new"
        ))
        await db.commit()
        return cursor.lastrowid

async def get_all_applicants() -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM applicants ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_applicant_by_id(applicant_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_applicant_status(applicant_id: int, status: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE applicants SET status = ? WHERE id = ?", (status, applicant_id))
        await db.commit()
        return True

async def get_stats() -> Dict[str, Any]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM applicants") as cur:
            total = (await cur.fetchone())[0]

        async with db.execute("SELECT direction, COUNT(*) FROM applicants GROUP BY direction") as cur:
            by_direction = await cur.fetchall()

        async with db.execute("SELECT status, COUNT(*) FROM applicants GROUP BY status") as cur:
            by_status = await cur.fetchall()

        return {
            "total": total,
            "by_direction": {row[0]: row[1] for row in by_direction},
            "by_status": {row[0]: row[1] for row in by_status}
        }

async def add_admin_db(user_id: int, username: str = "", full_name: str = "") -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO admins (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username, full_name))
        await db.commit()
        return True

async def remove_admin_db(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        await db.commit()
        return True

async def get_all_admins_db() -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM admins ORDER BY created_at ASC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def is_admin_db(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,)) as cursor:
            return (await cursor.fetchone()) is not None

