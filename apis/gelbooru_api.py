import requests
import os
import time
import random
import logging

logger = logging.getLogger(__name__)

class GelbooruAPI:
    def __init__(self):
        self.api_key = os.getenv("GELBOORU_API_KEY")
        self.user_id = os.getenv("GELBOORU_USER_ID")
        self.base_url = "https://gelbooru.com/index.php"

    def get_json(self, tags_lst=None, limit: int = 1):
        if not tags_lst:
            tags_lst = []
        tags = " ".join(tags_lst) + " sort:random"
        params = {
            'page': 'dapi',
            'q': 'index',
            'json': '1',
            'api_key': self.api_key,
            'user_id': self.user_id,
            'tags': tags,
            'limit': f"{limit}",
            's': 'post',
        }

        last_error = None
        for attempt in range(1):
            try:
                response = requests.get(self.base_url, params=params, timeout=15)

                if response.status_code == 429:
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.warning(f"[!] Rate limited por Gelbooru. Esperando {wait_time:.1f}s... (intento {attempt + 1}/5)")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()

                try:
                    data = response.json()
                except ValueError:
                    logger.error(f"[!] Respuesta no es JSON: {response.text[:200]}")
                    last_error = "Respuesta inválida de Gelbooru"
                    time.sleep(1)
                    continue

                posts = data.get("post")
                if not posts:
                    logger.warning(f"[!] Sin resultados para tags: {tags}")
                    return None

                post = posts[0]
                file_url = post.get("file_url")
                post_id = post.get("id")
                post_gel_url = f"https://gelbooru.com/index.php?page=post&s=view&id={post_id}"
                source_url = post.get("source", "")
                tags_post = post.get("tags", "")

                if not file_url:
                    logger.warning(f"[!] Post sin file_url: id={post_id}")
                    last_error = "Sin URL de archivo"
                    time.sleep(1)
                    continue

                return [file_url, post_gel_url, source_url, tags_post]

            except requests.exceptions.RequestException as e:
                logger.error(f"[!] Error de conexión con Gelbooru (intento {attempt + 1}/5): {e}")
                last_error = str(e)
                wait_time = 2 ** attempt
                time.sleep(wait_time)

        logger.error(f"[!] No se pudo obtener respuesta de Gelbooru después de 5 intentos. Último error: {last_error}")
        return None
