import requests
import json

# Perform a GET request
#response = requests.get('http://localhost:5002/test')
#print(response.text)

class TagPIIClientFastAPI:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_ranked_autocomplete(self, pairs):
        data = {'pairs': pairs}
        response = requests.post(f'http://{self.ip}:{self.port}/autocomplete', json=data)
        return response.json()

    def getStoryIDsWithTag(self, tags):
        data = {'tags': tags}
        response = requests.post(f'http://{self.ip}:{self.port}/getStoryIDsWithTag', json=data)
        return response.json()

    def getTagFrequency(self, tags):
        data = {'tags': tags}
        response = requests.post(f'http://{self.ip}:{self.port}/getTagFrequency', json=data)
        return response.json()

    def mergeWithOtherIndex(self, dateFileNames):
        data = {'dateFileNames': dateFileNames}
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndex', json=data)
        return response.json()
    
    def mergeWithOtherIndexAllDates(self):
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndexAllDates')
        return response.json()

if __name__ == '__main__':
    client = TagPIIClientFastAPI('localhost', 5002)
    tag_results = client.getStoryIDsWithTag(['anime', 'manga'])
    print(set(tag_results['anime']).intersection(set(tag_results['manga'])))
    print(client.getTagFrequency(['marvel', 'magic']))
    print(client.mergeWithOtherIndex(['compressedTagIndexFull.bin']))