import requests
import json

# Perform a GET request
response = requests.get('http://localhost:5000/test')
print(response.text)

class TagPIIClientFastAPI:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def getStoryIDsWithTag(self, tags):
        data = {'tags': tags}
        response = requests.post(f'http://{self.ip}:{self.port}/getStoryIDsWithTag', json=data)
        return response.json()

    def getTagFrequency(self, tags):
        data = {'tags': tags}
        response = requests.post(f'http://{self.ip}:{self.port}/getTagFrequency', json=data)
        return response.json()

if __name__ == '__main__':
    client = TagPIIClientFastAPI('localhost', 5000)
    print(client.getStoryIDsWithTag(['anime', 'manga']))
    print(client.getTagFrequency(['marvel', 'magic']))