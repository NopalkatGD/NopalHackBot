import requests
import time
import random
from urllib.parse import urlencode
from apis.api_gelbooru import GelbooruConfig

BASE_URL = "https://gelbooru.com/index.php"


class PeticionesGelbooru:
    def __init__(self):
        config = GelbooruConfig()
        self.gel_api_key = config.api_key
        self.gel_user_id = config.user_id

    def search_posts(self, tags_lst: list[str], limit: int = 1, random: bool = False):
        params = {
            "page": "dapi",
            "q": "index",
            "json": "1",
            "api_key": self.gel_api_key,
            "user_id": self.gel_user_id,
            "tags": self._format_tags(tags_lst, random),
            "limit": limit,
            "s": "post",
        }

        url = f"{BASE_URL}?{urlencode(params)}"

        for attempt in range(5):
            try:
                response = requests.get(url, timeout=15)

                if response.status_code == 429:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    print(f"[!] Rate limited por Gelbooru. Esperando {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()

                data = response.json()

                posts = data.get("post")
                if not posts:
                    raise Exception("No se encontraron imagenes para los tags proporcionados")

                post = posts[0]
                file_url = post.get("file_url")
                post_id = post.get("id")
                post_gel_url = f"https://gelbooru.com/index.php?page=post&s=view&id={post_id}"
                source_url = post.get("source", "")
                tags = post.get("tags", "")

                if file_url:
                    return file_url, post_gel_url, source_url, tags

                raise Exception("No se encontro URL de archivo en la respuesta")

            except requests.exceptions.RequestException as e:
                if attempt < 4:
                    wait_time = 2 ** attempt
                    print(f"[!] Error de conexion, reintento {attempt + 1}/5 en {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Error al conectar con Gelbooru: {e}")
            except ValueError:
                raise Exception("Respuesta invalida de Gelbooru (no es JSON)")

        raise Exception("No se encontraron imagenes despues de varios intentos")

    def _format_tags(self, tags_lst: list[str], random: bool) -> str:
        include = "+".join(tag.strip().lower().replace(" ", "_") for tag in tags_lst)
        if random:
            include += "+sort:random+"
        return include

    def _is_url_accessible(self, url: str) -> bool:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False