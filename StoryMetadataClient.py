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
    
    def getStoryDescriptors(self, storyIDs):
        data = {'storyIDs': storyIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getStoryDescriptors', json=data)
        return response.json()
    
if __name__ == '__main__':
    smClient = StoryMetadataClient('localhost', 5004)    
    storyids = [5216000, 3625092, 1068302, 25168015, 14540055, 3448346, 5570332, 9432605, 7635109, 4466729, 20696240, 4894012, 24922558, 933314, 1188804, 3448004, 7554757, 8081095, 11327304, 14429139, 21277529, 5772508, 18489310, 13661664, 7305187, 19287664, 4163313, 15264369, 11895930]
    print("1.", smClient.getDescription([5216000, 5]))
    print("2.", smClient.getLastUpdated([3]))    
    print("3.", smClient.getStats([id//1000 for id in storyids]))
    print("4.", smClient.getLanguage([3]))
    print("5.", smClient.getStoryDescriptors(storyids))