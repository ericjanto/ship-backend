import re
import Stemmer
import matplotlib.pyplot as plt

import os

class TextLawsAnalyser():

    def __init__(self, terms):
        self.terms = terms
        self.termFreqs = dict()
        self.termsRead = 0
        self.uniqueTermsEncountered = 0

        self.heapsLawDataPoints = []
        self._countTermFreqs()

    def getUniqueTermCount(self, ignoreTermsWithFreqOfOne=False):
        if not ignoreTermsWithFreqOfOne:
            return len(self.termFreqs)
        else:
            count = 0
            for term in self.termFreqs:
                if self.termFreqs[term] != 1:
                    count += 1
            return count

    def produceBenfordsLawData(self, ignoreTermsLessThanThreshold=False, threshold=1):
        data = [0 for _ in range(1, 10)]
        for term in self.termFreqs:
            if ignoreTermsLessThanThreshold and self.termFreqs[term] <= threshold:
                continue
            firstDigit = int(str(self.termFreqs[term])[:1]) - 1
            data[firstDigit] += 1

        return data

    def getTermsRankedByFrequency(self):
        return [(k, v) for k, v in sorted(self.termFreqs.items(), key=lambda x: x[1], reverse=True)]

    def _countTermFreqs(self):
        for term in self.terms:
            if term in self.termFreqs:
                self.termFreqs[term] += 1
            else:
                self.termFreqs[term] = 1
                self.uniqueTermsEncountered += 1
            self.termsRead += 1
            if self.termsRead % 100 == 0:
                self.heapsLawDataPoints.append((self.termsRead, self.uniqueTermsEncountered))
