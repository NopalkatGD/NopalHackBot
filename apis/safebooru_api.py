import requests

class SafebooruAPI:
    def __init__(self):
        self.base_url = "https://safebooru.org/index.php"

    def get_json(self, tags_lst=None, limit: int = 1):
        if not tags_lst:
            tags_lst = []
        tags = " ".join(tags_lst) + " sort:random"
        params = {
            'page': 'dapi',
            'q': 'index',
            'json': '1',
            'tags': tags,
            'limit': f"{limit}",
            's': 'post',
        }
        response = requests.get(self.base_url, params=params)
        return response.json()
    def get_data(self, tags_lst=None, limit: int = 1):
        data = self.get_json(tags_lst, limit)[0]
        data_list = [
            f'{self.base_url}?page=post&s=view&id={data.get("id")}',
            data.get("file_url"),
            data.get("source"),
        ]
        return data_list