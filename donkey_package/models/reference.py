from os import getenv
import json
import requests

API_KEY = getenv('API_KEY', None)
assert API_KEY

default_url = ('https://newsapi.org/v2/top-headlines?'
               'language=en&'
               'sources=the-new-york-times,the-wall-street-journal,bbc-news,reuters&'
               'pageSize=100&'
               f'apiKey={API_KEY}')


def get_api_response(url=default_url):

    response = requests.get(url)

    return response


def write_json(content):
    with open('current.json', 'w') as file:
        json.dump(content, file)


if __name__ == '__main__':

    response = get_api_response()

    write_json(response)
