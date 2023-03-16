import requests
import json


# test_queries = ["Who what who were AND (what OR (where AND are you))",
#                   "supernatural and doctor who superwholock",
#                   "superwholock",
#                   "bionicles",
#                   "Bob Fraser in a zombie apocalypse",
#                   "Doctor Who",
#                   "Doctor Mallard",
#                   "mix of words with \"Tails * bench\"",
#                   "\"Tails * bench\"",
#                 ]
# hard_queries = [ "Other terms with Mon*",
#                   "Mon*",
#                   "Mon*",
#                   "Mon*",
#                   "Mon*",
#                   "Mon*",
#                   "Mon*",
#                   "Mon*",
#                   "Mon*",
#                   "Mon*",]

# response = requests.get('http://storyhunter.live:80/test')
# print(response.text)

class SearchEngineAPIClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def query(self,query,tags=[],filter_params=None):
        data = {'query': query,
                'tags': tags,
                'filter_params': filter_params}
        response = requests.get(f'http://{self.ip}:{self.port}/query',json=data)
        return response.json()
    
if __name__ == '__main__':
    client = SearchEngineAPIClient('localhost', 5005)
    # Fix proximity queries:
    print(client.query('"harry potter"',[], {}))

    # Fix filtering:
    print(client.query("harry",[], {'singleChapter': True})[6])
    print(client.query("harry",[], {'singleChapter': False})[6])
