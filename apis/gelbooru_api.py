import requests
import os
import dotenv

class GelbooruAPI:
    def __init__(self):
        dotenv.load_dotenv()
        self.api_key = os.getenv("GELBOORU_API_KEY")
        self.user_id = os.getenv("GELBOORU_USER_ID")
        self.base_url = "https://gelbooru.com/index.php"

    def get_json(self, tags_lst= None, limit:int=1):
        if not tags_lst:
            tags_lst = []
        tags = " ".join(tags_lst)+" sort:random"
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
        response = requests.get(self.base_url, params=params)
        #print de debugging
        #print(response.url)
        #print(response.status_code)
        #print(response.text)


        if response.status_code == 200 and 'post' in response.json():
            post = response.json()['post'][0]

            data = [
                #url file
                post.get('file_url'),
                #gelbooru post
                f"https://gelbooru.com/index.php?page=post&s=view&id={post.get('id')}",
                #gelbooru post source
                post.get('source'),
                #gelbooru post tags
                post.get('tags')
            ]
            #print(post.get('sample_url'))

            return data
        return None