import re
import Stemmer
import matplotlib.pyplot as plt

import os

from Preprocessor import Preprocessor
from TextLawsAnalyser import TextLawsAnalyser

def loadStopWordsIntoSet(fileLocation):
    stopWords = set()
    with open(fileLocation, "r") as f:
        data = f.readlines()
        for word in data:
            stopWords.add(word.strip())
    return stopWords

def splitIntoTerms(collection):
    return re.split(r'\W+', collection)

def normaliseCase(terms):
    for i in range(len(terms)):
        terms[i] = terms[i].lower()
    return terms

def removeStopWords(terms, stopWords):
    # stopWords should be a set to improve run time
    return [term for term in terms if term not in stopWords]

def stemTerms(terms):
    return stemmer.stemWords(terms)
    # stemmed = [None for _ in range(len(terms))]
    # for i, term in enumerate(terms):
    #     terms[i] = porter2.stem(term)
    #     if (i % 100000 == 0):
    #         print(f"Stemmed  {i/len(terms) * 100}% of the document")
    # return stemmed

def preprocessDocument(filename, stopWords):

    with open(filename, 'r', encoding="utf-8") as f:
        data = f.read()
    tokenisedDocument = splitIntoTerms(data)
    print("tokenised " + filename)
    lowerCasedDocumentTokens = normaliseCase(tokenisedDocument)
    print("Normalised " + filename)
    stopWordFreeTerms = removeStopWords(lowerCasedDocumentTokens, stopWords)
    print("Removed stop words from " + filename)
    regularisedTerms = stemTerms(stopWordFreeTerms)
    print("Regularised " + filename)

    return TextLawsAnalyser(regularisedTerms)



if __name__ == "__main__":

    global stemmer
    #stemmer = nltk.stem.SnowballStemmer('english')
    stemmer = Stemmer.Stemmer('english')

    SRC = ['bible.txt', 'quran.txt', 'abstracts.wiki.txt']

    rankedFreqs = []
    benfordDists = []
    benfordDistsIgnoringOnes = []
    benfordDistsIgnoringLessThanTen = []
    heapsLawDataPoints = []

    stopWords = loadStopWordsIntoSet("englishStopWords.txt")
    
    for src in SRC:
        analyser = None
        if os.path.isdir('preprocessed/') and os.path.isfile('preprocessed/' + src):
            with open('preprocessed/' + src, "r", encoding="utf-8") as f:
                terms = f.readlines()
                analyser = TextLawsAnalyser(terms)
        else:
            document = []
            with open('data/' + src, "r", encoding="utf-8") as f:
                document = f.read()
            preprocessor = Preprocessor(document, stopWords, filename=src)
            analyser = TextLawsAnalyser(preprocessor.preprocess(verbose=True))
            preprocessor.exportProcessedDocumentToFile('preprocessed/' + src)
        
        rankedFreqs.append(analyser.getTermsRankedByFrequency())
        benfordDists.append(analyser.produceBenfordsLawData())
        benfordDistsIgnoringOnes.append(analyser.produceBenfordsLawData(True))
        benfordDistsIgnoringLessThanTen.append(analyser.produceBenfordsLawData(True, 10))
        heapsLawDataPoints.append(analyser.heapsLawDataPoints)

        print(f"Processed {src}")


    for i in range(len(SRC)):
        plt.loglog([c + 1 for c in range(len(rankedFreqs[i]))],
                   [x[1] for x in rankedFreqs[i]], label=SRC[i])
    plt.xlabel("Log Term rank")
    plt.ylabel("Log Frequency")
    plt.legend()
    plt.title("Zipf's Law (Log Log Graph)")
    plt.savefig("zipf.pdf")
    plt.clf()

    for i in range(len(SRC)):
        normalised = [x / sum(benfordDists[i]) for x in benfordDists[i]]
        labels = [x for x in range(1, 10)]
        plt.plot(labels, normalised, label=SRC[i])
    plt.xlabel("First Digit")
    plt.ylabel("Frequency (Normalised)")
    plt.title("Benford's Law")
    plt.legend()
    plt.savefig("Benfords.pdf")
    plt.clf()

    for i in range(len(SRC)):
        normalised = [x / sum(benfordDistsIgnoringOnes[i]) for x in benfordDistsIgnoringOnes[i]]
        labels = [x for x in range(1, 10)]
        plt.plot(labels, normalised, label=SRC[i])
    plt.xlabel("First Digit")
    plt.ylabel("Frequency (Normalised)")
    plt.title("\nBenford's Law \n(Excluding terms which \nonly appear once)")
    plt.legend()
    plt.savefig("BenfordsExcludingSingletons.pdf")
    plt.clf()

    for i in range(len(SRC)):
        normalised = [x / sum(benfordDistsIgnoringLessThanTen[i]) for x in benfordDistsIgnoringLessThanTen[i]]
        labels = [x for x in range(1, 10)]
        plt.plot(labels, normalised, label=SRC[i])
    plt.xlabel("First Digit")
    plt.ylabel("Frequency (Normalised)")
    plt.title("\nBenford's Law \n(Excluding terms which \noccur less than ten times)")
    plt.legend()
    plt.savefig("BenfordsExcludingSingleDigitFrequencies.pdf")
    plt.clf()

    for i in range(len(SRC)):
        terms_read = [x[0] for x in heapsLawDataPoints[i]]
        unique_terms_encountered = [x[1] for x in heapsLawDataPoints[i]]
        plt.plot(terms_read, unique_terms_encountered, label=SRC[i])
        plt.xlabel("Terms Read")
        plt.ylabel("Unique Terms Encountered")
        plt.title("Heaps.pdf")
        plt.legend()
        filenameAddition = SRC[i].split(".")[0]
        plt.savefig(f"heaps-{filenameAddition}.pdf")
        plt.clf()