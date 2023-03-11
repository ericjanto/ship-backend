import requests
import json

class StoryMetadataClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
    
    def getDescription(self, storyIDs):
        data = {'storyIDs': storyIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getDescription', json=data)
        return response.json()
    
    def getLastUpdated(self, storyIDs):
        data = {'storyIDs': storyIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getLastUpdated', json=data)
        return response.json()
    
    def getStats(self, storyIDs):
        data = {'storyIDs': storyIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getStats', json=data)
        return response.json()
    
    def getLanguage(self, storyIDs):
        data = {'storyIDs': storyIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getLanguage', json=data)
        return response.json()
    

if __name__ == '__main__':
    smClient = StoryMetadataClient('localhost', 5000)
    print("1.", smClient.getDescription([3, 5]))
    print("2.", smClient.getLastUpdated([3]))
    print("3.", smClient.getStats([3]))
    print("4.", smClient.getLanguage([3]))