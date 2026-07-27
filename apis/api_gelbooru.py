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

        tags = "+".join(tags_lst) + "+sort:random+"
        url = (
            f"{self.base_url}?page=dapi&q=index&json=1"
            f"&api_key={self.api_key}&user_id={self.user_id}"
            f"&tags={tags}&limit={limit}&s=post"
        )

        respuesta = requests.get(url, timeout=15)

        if respuesta.status_code == 429:
            raise Exception(f"Rate limit de Gelbooru (429)")

        if respuesta.status_code != 200:
            raise Exception(f"Gelbooru respondió con status {respuesta.status_code}: {respuesta.text[:200]}")

        try:
            data = respuesta.json()
        except Exception:
            raise Exception(f"Respuesta no es JSON: {respuesta.text[:200]}")

        if "post" not in data:
            attrs = data.get("@attributes", {})
            count = attrs.get("count", 0)
            raise Exception(f"Gelbooru sin resultados. count={count}, attributes={attrs}")

        data = data["post"][0]

        file_url = data["file_url"]

        gelbooru_id = data["id"]
        gelbooru_url = f"https://gelbooru.com/index.php?page=post&s=view&id={gelbooru_id}"

        source_url = data["source"]
        tags_post = data["tags"].split()

        return file_url, gelbooru_url, source_url, tags_post
