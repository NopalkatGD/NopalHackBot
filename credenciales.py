import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('GELBOORU_API_KEY') 
user_id = os.environ.get('GELBOORU_USER_ID') 

bot_api = os.environ.get('BOT_API_TOKEN') 