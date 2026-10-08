import re
filepath = ".env"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

target = "SECRET_KEY=CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32"
replacement = "SECRET_KEY=29262506e8c3bb0fdc8daf709778761a99145dc69af1bb6544198eeae6c20b3e"
content = content.replace(target, replacement)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
