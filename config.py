import os

# Токен бота. Вставь сюда токен из https://discord.com/developers/applications
BOT_TOKEN = os.environ.get("AWARD_BOT_TOKEN", "MTU1ODM2ODQ1MTA3MDkxODY5Ng.GFAIF4.ZRZY-VDSdJeF0mNsCKjelntPUSwyAQMX2h4gfk")

# Guild id вашего сервера (нужен для синхронизации slash-команд).
# Если оставить None - команды регистрируются глобально (обновление занимает до часа).
GUILD_ID = 1553829485646839982  # например: 987654321098765432

# Роль администратора, которая может выдавать медали.
# Если не указывать - доступ есть у пользователей с правом Administrator.
ADMIN_ROLE_NAME = "Админ"

# Канал, куда бот отправляет логи о выдаче наград (если None - логи не шлются).
LOG_CHANNEL_ID = None

# Пути к файлам БД
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "awards.db")

PREFIX = "!"
