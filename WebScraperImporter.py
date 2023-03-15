import json
import os
from datetime import datetime

import PositionalInvertedIndexExporter
from PositionalInvertedIndex import PositionalInvertedIndex
from PositionalInvertedIndexExporter import PositionalInvertedExporter
from StoryMetadataExporter import StoryMetadataExporter
from StoryMetadataRecord import StoryMetadataRecord
from TagPositionalInvertedIndex import TagPositionalInvertedIndex
from TagPositionalInvertedIndexExporter import TagPositionalInvertedIndexExporter
from TermCounts import TermCounts
from TermCountsExporter import TermCountsExporter
from preprocessing import loadStopWordsIntoSet
from Preprocessor import Preprocessor

class WebScraperImporter:

    def __init__(self, pathToStopwords: str = "englishStopWords.txt"):

        self.stopwords = loadStopWordsIntoSet(pathToStopwords)

        self.preprocessor = Preprocessor(None, self.stopwords)

    def convertWebScrapeDumpsToIndexChunks(self, pathToChaptersJSON: str, pathToMetadataJSON: str, outputPath: str, dateStr: str) -> None:

        chaptersJSON = self.loadJSONFile(pathToChaptersJSON)
        metadataJSON = self.loadJSONFile(pathToMetadataJSON)


        chaptersIndex = PositionalInvertedIndex()
        tagsIndex = TagPositionalInvertedIndex()
        termCounts = TermCounts(self.stopwords)
        metadataIndex = dict()

        for chapterIDStr in chaptersJSON:
            chapterID = int(chapterIDStr)
            chapterNo = chapterID % 1000
            storyNo = chapterID // 1000

            # print(storyNo)
            # print(chapterNo)
            # print()

            if chapterNo == 999:
                continue

            text = chaptersJSON[chapterIDStr]

            if text is None or len(text) == 0:
                continue

            if chapterNo == 000:
                text += " " + metadataJSON[str(storyNo)]["title"]

                text += " " + " ".join(metadataJSON[str(storyNo)]["author"])

                text += " " + metadataJSON[str(storyNo)]["summary"]

            termCounts.countTermsRowWise(text, chapterID)

            preprocessedText = self.preprocessor.preprocessDocument(text)

            for pos, term in enumerate(preprocessedText):
                chaptersIndex.insertTermInstance(term, chapterID, pos)

        for storyNoStr in metadataJSON:
            storyNoInt = int(storyNoStr)

            TAG_TYPES = ["ratings", "warnings", "categories", "fandom", "relationships", "characters", "freeform"]
            for tagType in TAG_TYPES:
                for tag in metadataJSON[storyNoStr][tagType]:
                    tagsIndex.insertTagInstance(tag, storyNoInt)


            metadata = StoryMetadataRecord()
            metadata.storyID = storyNoInt
            metadata.title = metadataJSON[storyNoStr]["title"]
            # TODO: This forcibly joins every author into a single string,
            # Is that ok, or should it be fixed
            metadata.setAuthor(metadataJSON[storyNoStr]["author"])
            metadata.setDescription(metadataJSON[storyNoStr]["summary"])


            currentChapters, maxChapters = [x for x in metadataJSON[storyNoStr]["stats"]["chapters"].split("/")]
            metadata.currentChapterCount = int(currentChapters)

            if maxChapters == "?":
                maxChapters = -1
            else:
                maxChapters = int(maxChapters)
            metadata.setFinalChapterCount(maxChapters)

            if metadata.currentChapterCount == metadata.finalChapterCount:
                metadata.finished = True

            # This is very hacky, but works given we don't intend
            # to support non english stories
            language = metadataJSON[storyNoStr]["language"]
            language = 1 if language.lower() == "english" else 2
            metadata.language = language

            metadata.wordCount = int(metadataJSON[storyNoStr]["stats"]["words"][1])
            metadata.commentCount = int(metadataJSON[storyNoStr]["stats"]["comments"])
            metadata.bookmarkCount = int(metadataJSON[storyNoStr]["stats"]["bookmarks"])
            metadata.kudosCount = int(metadataJSON[storyNoStr]["stats"]["kudos"])
            metadata.hitCount = int(metadataJSON[storyNoStr]["stats"]["hits"])
            lastUpdated = metadataJSON[storyNoStr]["stats"]["published"]
            if lastUpdated == "-999":
                lastUpdatedUnix = 0
            else:
                dt = datetime.strptime(lastUpdated, "%Y-%m-%d")
                if dt <= datetime(1970, 1, 1):
                    lastUpdatedUnix = 0
                else:
                    lastUpdatedUnix = int(dt.timestamp())

            metadata.lastUpdated = lastUpdatedUnix
            metadataIndex[storyNoInt] = metadata

        # Save indexes to file

        PositionalInvertedExporter.saveToCompressedIndex(chaptersIndex,
                                                              os.path.join(
                                                                  outputPath,
                                                                  f"chapters-{dateStr}.bin"
                                                              ))

        TagPositionalInvertedIndexExporter.saveToCompressedIndex(tagsIndex,
                                                                 os.path.join(
                                                                     outputPath,
                                                                     f"tags-{dateStr}.bin"
                                                                 ))

        StoryMetadataExporter.saveToCompressedIndex(metadataIndex,
                                                    os.path.join(
                                                        outputPath,
                                                        f"metadata-{dateStr}.bin"
                                                    ))

        TermCountsExporter.saveToFile(
            os.path.join(
                outputPath,
                f"termCounts-{dateStr}.bin"
            ),
            termCounts.termCounts
        )



    def loadJSONFile(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

if __name__ == "__main__":
    importer = WebScraperImporter()

    importer.convertWebScrapeDumpsToIndexChunks("data/chapters2023-03-13.json",
                                                "data/metaData2023-03-13.json",
                                                "data/",
                                                "2023-03-14")
