from TermCountsClient import TermCountsClient
from StoryMetadataClient import StoryMetadataClient
from PIIClientFastAPI import PIIClientFlask
from TagPIIClientFastAPI import TagPIIClientFastAPI

if __name__=='__main__':
    piiClient = PIIClientFlask('localhost', 5001)
    tagClient = TagPIIClientFastAPI('localhost', 5002)
    tcClient = TermCountsClient('localhost', 5003)
    smClient = StoryMetadataClient('localhost', 5004)
    piiClient.mergeWithOtherIndexAllDates()
    tagClient.mergeWithOtherIndexAllDates()
    tcClient.mergeWithOtherIndexAllDates()
    smClient.mergeWithOtherIndexAllDates()