import smolandshop
from models import initialize_db, db

initialize_db()
smolandshop.parse_url(smolandshop.base_url)
db.close()
