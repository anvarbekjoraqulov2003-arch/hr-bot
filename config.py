import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8876471739:AAFQ5AVxLNogkEfk3NtMFShWQdTYsEUq9A4").strip()

_admin_ids_raw = os.getenv("ADMIN_IDS", "1649296,6651310885").strip()
ADMIN_IDS: List[int] = []
if _admin_ids_raw:
    for aid in _admin_ids_raw.split(","):
        aid = aid.strip()
        if aid.isdigit() or (aid.startswith("-") and aid[1:].isdigit()):
            ADMIN_IDS.append(int(aid))


_hr_channel_raw = os.getenv("HR_CHANNEL_ID", "").strip()
HR_CHANNEL_ID: Optional[int] = None
if _hr_channel_raw:
    try:
        HR_CHANNEL_ID = int(_hr_channel_raw)
    except ValueError:
        pass

DB_PATH: str = os.getenv("DB_PATH", "database.db").strip()
