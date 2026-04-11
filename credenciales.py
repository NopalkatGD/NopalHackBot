import os
from dotenv import load_dotenv

load_dotenv()

gel_api_key = os.getenv("GELBOORU_API_KEY")
gel_user_id = os.getenv("GELBOORU_USER_ID")
bot_token = os.getenv("BOT_API_TOKEN")