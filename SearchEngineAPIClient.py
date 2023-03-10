import requests
import json

response = requests.get('http://localhost:5000/test')
print(response.text)

class SearchEngineAPIClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def query(self,query,tags,filter_params=None):
        data = {'query': query,
                'tags': tags,
                'filter_params': filter_params}
        response = requests.get(f'http://{self.ip}:{self.port}/query',json=data)
        return response.json()
    
if __name__ == '__main__':
    client = SearchEngineAPIClient('localhost',4999)
    print(client.query("",['anime','manga']))