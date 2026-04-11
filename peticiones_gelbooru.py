from python_gelbooru import AsyncGelbooru
import credenciales
from dotenv import load_dotenv
import requests

class PeticionesGelbooru:
    def __init__(self):
        load_dotenv()
        self.gel_api_key = credenciales.gel_api_key
        self.gel_user_id = credenciales.gel_user_id

    async def main(self, tags_lst: list[str]):
        try:
            async with AsyncGelbooru(api_key=self.gel_api_key, user_id=self.gel_user_id) as gel:
                peticion = await gel.search_posts(tags_lst, limit=1, random=True)
                if not peticion:
                    raise Exception("No se encontraron imágenes para los tags proporcionados")
                
                post = peticion[0]
                file_url = post.file_url
                post_gel_url = f"https://gelbooru.com/index.php?page=post&s=view&id={post.id}"
                source_url = post.source
                tags_lst = post.tags
                
                urls_a_probar = [file_url]
                
                if hasattr(post, 'sample_url') and post.sample_url:
                    urls_a_probar.append(post.sample_url)
                
                url_valida = None
                for url in urls_a_probar:
                    if url and self._is_url_accessible(url):
                        url_valida = url
                        break
                
                if url_valida:
                    file_url = url_valida
                else:
                    print(f"Warning: Ninguna URL accesible para post {post.id}, usando original: {file_url}")
                
                return file_url, post_gel_url, source_url, tags_lst
        
        except Exception as e:
            print(f"Error al obtener las imágenes: {str(e)}")
            raise e
    
    def _is_url_accessible(self, url: str) -> bool:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False