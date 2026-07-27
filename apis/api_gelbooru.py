import os
from dotenv import load_dotenv
import requests


class GelbooruConfig:
    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("GELBOORU_API_KEY")
        self.user_id = os.getenv("GELBOORU_USER_ID")

        self.base_url = "https://gelbooru.com/index.php"

    def get_json(self, tags_lst=None, limit: int = 1):

        if tags_lst is None:
            tags_lst = []
        tags = " ".join(tags_lst + ["sort:random"])

        tags = " ".join(tags_lst)
        params = {
            "page": "dapi",
            "q": "index",
            "json": "1",
            "api_key": self.api_key,
            "user_id": self.user_id,
            "tags": tags,
            "limit": f"{limit}",
            "s": "post",
        }
        respuesta = requests.get(self.base_url, params=params)


        #borrar luego de pruebas
        print("URL:", respuesta.url)
        print("STATUS:", respuesta.status_code)
        print("JSON:", respuesta.json())

        if "post" not in respuesta.json():
            return None, None, None, None

        data = respuesta.json()["post"][0]

        file_url =data["file_url"]

        gelbooru_id = data["id"]
        gelbooru_url = f"https://gelbooru.com/index.php?page=post&s=view&id={gelbooru_id}"

        source_url = data["source"]
        tags_post = data["tags"].split()

        return file_url, gelbooru_url, source_url, tags_post
    #def get_values():


