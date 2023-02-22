def loadStopWordsIntoSet(fileLocation):
    stopWords = set()
    with open(fileLocation, "r") as f:
        data = f.readlines()
        for word in data:
            stopWords.add(word.strip())
    return stopWords
