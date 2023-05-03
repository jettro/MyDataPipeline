import openai
import os

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.getenv('OPEN_AI_API_KEY')


if __name__ == '__main__':
    response = openai.Image.create(
        prompt="a lake with smelly water, dead trees surrounding it and a monster coming half out of the water",
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']

    print(image_url)