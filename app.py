from dotenv import load_dotenv

import smolandshop
from models import initialize_db, db

load_dotenv()
initialize_db()
smolandshop.parse_url(smolandshop.base_url)
db.close()
