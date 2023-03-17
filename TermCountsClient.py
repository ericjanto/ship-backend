import requests
import json
from TermCountsLoader import TermCountsLoader
from time import sleep


class TermCountsClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_tokens_before_processing(self, docIDs):
        data = {'docIDs': docIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getTokensBeforeProcessing', json=data)
        return response.json()
    
    def get_tokens_before_stemming(self, docIDs):
        data = {'docIDs': docIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getTokensBeforeStemming', json=data)
        return response.json()
    
    def get_unique_tokens_before_processing(self, docIDs):
        data = {'docIDs': docIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getUniqueTokensBeforeProcessing', json=data)
        return response.json()
    
    def get_unique_tokens_before_stemming(self, docIDs):
        data = {'docIDs': docIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getUniqueTokensBeforeStemming', json=data)
        return response.json()
    
    def get_tokens_after_stemming(self, docIDs):
        data = {'docIDs': docIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getTokensAfterStemming', json=data)
        return response.json()

    def get_all_term_counts_for(self, docIDs):
        data = {'docIDs': docIDs}
        response = requests.post(f'http://{self.ip}:{self.port}/getAllTermCountsForDocIds', json=data)
        return response.json()

    def get_all_term_counts(self):
        response = requests.get(f'http://{self.ip}:{self.port}/getAllTermCounts')
        return response.json()

    def append_into_term_counts(self, termCounts):
        data = {'termCounts': termCounts}
        response = requests.put(f'http://{self.ip}:{self.port}/appendIntoTermCounts', json=data)
        return response.json()
    
    def mergeWithOtherIndex(self, dateFileNames):
        data = {'dateFileNames': dateFileNames}
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndex', json=data)
        return response.json()

    def mergeWithOtherIndexAllDates(self):
        response = requests.put(f'http://{self.ip}:{self.port}/mergeWithOtherIndexAllDates')
        return response.json()

if __name__ == '__main__':
    tcClient = TermCountsClient('localhost', 5000)
    print("1.", tcClient.get_tokens_before_processing([51664000, 51233000]))
    print("2.", tcClient.get_tokens_before_stemming([51664000]))
    print("3.", tcClient.get_unique_tokens_before_processing([51664000]))
    print("4.", tcClient.get_unique_tokens_before_stemming([51664000]))
    print("5.", tcClient.get_tokens_after_stemming([51664000]))
    print("6.", tcClient.get_all_term_counts_for([51664000]))
    newTermCounts = TermCountsLoader.loadFromFile('./data/termCounts.bin')
    print(tcClient.append_into_term_counts([newTermCounts.get_all_term_counts()]))
    print("7.", tcClient.get_tokens_before_processing([51664000, 51233000]))