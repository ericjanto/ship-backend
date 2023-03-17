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

    def mergeWithOtherIndex(self, dateFileNames):
        data = {'dateFileNames': dateFileNames}
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndex', json=data)
        return response.json()

    def mergeWithOtherIndexAllDates(self):
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndexAllDates')
        return response.json()
    
if __name__ == '__main__':
    smClient = StoryMetadataClient('localhost', 5004)    
    storyids = ['100579000', '100579005', '10102000', '102597000', '103525000', '105404000', '10628000', '106984000',
                '107158000', '107158001', '108311000', '11059000', '11116000', '112836000', '113198000', '113198001',
                '113198002', '113198004', '113658000', '113801000', '114452000', '117366000', '117458000', '117458004',
                '117512004', '117512005', '117512006', '117512007', '117512009', '117512010', '117512011', '119638000',
                '121733000', '122255000', '124158000', '126041000', '127256000', '127451000', '127769000', '128628000', 
                '128728000', '129718000', '130023000', '131619000', '132224000', '133051000', '133494000', '133596000', 
                '136798000', '137418000', '137900000', '137932000', '138100000', '139587000', '139608000', '14323000', 
                '14323001', '144130000', '150546000', '151433024', '152647000', '154811000', '155168004', '155168011', 
                '155761000', '157028000', '157417004', '158743000', '158830003', '159934004', '160850000', '160968000', 
                '161013000', '161211000', '166050042', '169494000', '172115000', '172292000', '173513000', '173924000', 
                '175621000', '176929000', '180806000', '180806001', '180806004', '181095000', '181095001', '181095002', 
                '181095003', '181095004', '181522000', '19003000', '19457000', '19570000', '21754000', '22879000', 
                '24884000', '28189000', '39320000', '41071000', '41563000', '41627000', '43152000', '43174000', '43619000', 
                '43619001', '43885000', '45485000', '45485001', '46387000', '46528000', '46890000', '48389000', '50502000', 
                '50941000', '51028000', '51436000', '51484000', '55254000', '55390001', '55390004', '55390008', '55390010', 
                '56551000', '58758000', '5904003', '59200000', '59242000', '59242001', '60155000', '60668000', '61463000', 
                '6282000', '68692000', '68692001', '68692002', '69622000', '71447000', '73689000', '74208000', '74779000', 
                '74779001', '75263011', '78579000', '78803000', '81769000', '84080000', '88027000', '89149000', '89450000', 
                '90397000', '91561000', '91731000', '93074000', '94758000', '95671000', '98159000', '98734000']
    print("1.", smClient.getDescription([5216000, 5]))
    print("2.", smClient.getLastUpdated([3]))    
    print("3.", smClient.getStats([79104,103637,51028,110078,78803,20392,44456]))
    print("4.", smClient.getLanguage([79104,103637,51028,110078,78803,20392,44456]))
    print("5.", smClient.getStoryDescriptors([79104,103637,51028,110078,78803,20392,44456]))