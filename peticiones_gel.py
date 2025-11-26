import credenciales as cred
import asyncio
from python_gelbooru import AsyncGelbooru

api_key, user_id = cred.api_key, cred.user_id

async def main(tags:list):
    # si no hay tags => usar random puro
    async with AsyncGelbooru(api_key=api_key, user_id=user_id) as gel:
        post = await gel.search_posts(
            tags,
            limit=1,
            random=True
        )

        if not post:
            return ['', '', '']

        file_url = [i.file_url for i in post]
        post_url = [f'https://gelbooru.com/index.php?page=post&s=view&id={i.id}' for i in post]
        source = [i.source for i in post]

        return [file_url, post_url, source]



if __name__ == "__main__":
    tags_test = ['animated ']
    #for i in range(0,10):
    loop = asyncio.get_event_loop()
    arts= loop.run_until_complete(main(tags_test))
    if arts[2][0] == "":
        print("vacio")
    print(arts)
    