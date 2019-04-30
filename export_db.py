# This exports the db to an env var so we can use Telegram session on CI

import base64

with open("session_name.session", "rb") as file:
    encoded_db = base64.b64encode(file.read())
    print("SESSION_DB=" + encoded_db.decode("utf-8"))
