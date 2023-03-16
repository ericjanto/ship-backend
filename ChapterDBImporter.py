import os
import sqlite3
from bs4 import BeautifulSoup as bs
import PositionalInvertedIndexExporter
from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory
from PositionalInvertedIndexExporter import PositionalInvertedExporter
from PositionalInvertedIndexLoader import PositionalInvertedIndexLoader
from PositionalInvertedIndex import PositionalInvertedIndex
from preprocessing import loadStopWordsIntoSet
from TermCounts import TermCounts
from TermCountsExporter import TermCountsExporter
from Preprocessor import Preprocessor
import pickle

class ChapterDBImporter:

    def __init__(self, pathToDB: str, query: str) -> None:
        self.query = query

        self.conn = sqlite3.connect(pathToDB)

        self.cursor = self.conn.cursor()

        #TODO: Make this configurable
        self.stopWords = loadStopWordsIntoSet('englishStopWords.txt')
        self.preprocessor = Preprocessor(None, self.stopWords)
        self.termCounter = TermCounts(self.stopWords)

    def importChaptersToIndex(self, outputPath: str, chaptersPerChunk: int = 50000, limit=None, verbose=False) -> None:
        """Will flush the index to multiple vbyte compressed index chunks"""

        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        chunkNo = 0
        chaptersInCurrentChunk = 0

        index = PositionalInvertedIndex()

        self.cursor.execute(self.query) # Assuming this doesn't cause RAM issues, ie, doesn't load everything

        for i, row in enumerate(self.cursor):

            if limit and i >= limit:
                break

            if verbose and i % 100000 == 0:
                print(f"Preprocessed and indexed {i/ 1000000} million chapters")

            docID = row[0]
            chapter = row[1]
            self.termCounter.countTermsRowWise(chapter, docID)
            preprocessedChapter = self.preprocessor.preprocessDocument(chapter)

            for pos, term in enumerate(preprocessedChapter):
                index.insertTermInstance(term, docID, pos)
            chaptersInCurrentChunk += 1

            if chaptersInCurrentChunk == chaptersPerChunk:
                # Flush index to file
                if os.path.exists(outputPath) == False:
                    os.makedirs(outputPath)
                outputTo = os.path.join(outputPath, f"chapterIndex-part-{chunkNo}.bin")
                PositionalInvertedExporter.saveToCompressedIndex(index, outputTo)

                chunkNo += 1
                chaptersInCurrentChunk = 0

                index = PositionalInvertedIndex()

        if chaptersInCurrentChunk != 0:
            if os.path.exists(outputPath) == False:
                os.makedirs(outputPath)
            outputTo = os.path.join(outputPath, f"chapterIndex-part-{chunkNo}.bin")
            PositionalInvertedExporter.saveToCompressedIndex(index, outputTo)
        
        TermCountsExporter.saveToFile(os.path.join("./data/", "termCounts.bin"), self.termCounter.termCounts)

    def importTermCounts(self, outputPath: str, chaptersPerChunk: int = 50000, chunkLimit: int = None, verbose=False) -> None:

        print(f"Importing term counts for {chunkLimit} chunks")

        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        chunkNo = 0
        chaptersInCurrentChunk = 0

        #uniquePreStemmedTerms = set()

        self.cursor.execute(self.query)  # Assuming this doesn't cause RAM issues, ie, doesn't load everything

        for i, row in enumerate(self.cursor):

            if chunkLimit and chunkNo >= chunkLimit:
                break

            if verbose and i % 1000 == 0:
                print(f"Preprocessed and indexed {i} chapters")

            docID = row[0]
            chapter = row[1]
            # This is a hacky solution to save time preprocessing each document twice
            self.termCounter.countTermsRowWise(chapter, docID)
            #preprocessedChapter = self.preprocessor.preprocessDocument(chapter, removeStopWords=True, stem=False)

            # for term in preprocessedChapter:
            #     uniquePreStemmedTerms.add(term)
            chaptersInCurrentChunk += 1

            if chaptersInCurrentChunk >= chaptersPerChunk:

                chunkNo += 1
                chaptersInCurrentChunk = 0

                print(f"Processed {chunkNo} chunks")

        print("Exporting term counts")

        TermCountsExporter.saveToFile(os.path.join("./data/", "termCountsFull.bin"), self.termCounter.termCounts)

        # print("Exporting doc-terms")
        #
        # docTermsOutputPath = os.path.join("./data/", "doc-terms-full.pickle")
        # with open(docTermsOutputPath, "wb") as f:
        #     pickle.dump(uniquePreStemmedTerms, f)

    def importDocTerms(self, outputPath: str, chaptersPerChunk: int = 50000, chunkLimit: int = None, verbose=False) -> None:
        print(f"importing pre stemmed terms for {chunkLimit} chunks")


        if not os.path.exists(outputPath):
            os.makedirs(outputPath)

        chunkNo = 0
        chaptersInCurrentChunk = 0

        uniquePreStemmedTerms = set()

        self.cursor.execute(self.query)  # Assuming this doesn't cause RAM issues, ie, doesn't load everything

        for i, row in enumerate(self.cursor):

            if chunkLimit and chunkNo >= chunkLimit:
                break

            if verbose and i % 1000 == 0:
                print(f"Preprocessed and indexed {i} chapters")

            docID = row[0]
            chapter = row[1]
            preprocessedChapter = self.preprocessor.preprocessDocument(chapter, removeStopWords=True, stem=False)

            for term in preprocessedChapter:
                uniquePreStemmedTerms.add(term)
            chaptersInCurrentChunk += 1

            if chaptersInCurrentChunk >= chaptersPerChunk:
                chunkNo += 1
                chaptersInCurrentChunk = 0

                print(f"Processed {chunkNo} chunks")

            # Safety feature: rely on heap's law to ensure we at least
            # have something for our wildcard tree
            if i > 0 and i % 10000 == 0:
                docTermsOutputPath = os.path.join("./data/", "doc-terms-full.pickle")
                with open(docTermsOutputPath, "wb") as f:
                    pickle.dump(uniquePreStemmedTerms, f)

        # print("Exporting term counts")
        #
        # TermCountsExporter.saveToFile(os.path.join("./data/", "termCountsFull.bin"), self.termCounter.termCounts)
        #
        print("Exporting doc-terms")

        docTermsOutputPath = os.path.join("./data/", "doc-terms-full.pickle")
        with open(docTermsOutputPath, "wb") as f:
            pickle.dump(uniquePreStemmedTerms, f)


if __name__ == "__main__":
    """
    conn = sqlite3.connect("smallerDB.sqlite3")
    cursor = conn.cursor()
    
    GET_ALL_TABLENAMES = "SELECT name FROM sqlite_master WHERE type='table';"

    result = conn.execute(GET_ALL_TABLENAMES).fetchall()
    table_names = sorted(list(zip(*result))[0])
    print("\ntables are:"+'\n'+'\n'.join(table_names))
    for table_name in table_names:
        result = conn.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        print("\nTable: %s" % table_name)
        print(result)
        print()
   
    GET_LANGUAGE_ID_FOR_ENGLISH_QUERY = "SELECT * FROM Languages WHERE name = 'English';"

    cursor.execute(GET_LANGUAGE_ID_FOR_ENGLISH_QUERY)
    print(cursor.fetchall())

    # Count number of english fics

    QUERY = "SELECT COUNT(*) FROM StoryHeaders where language =1;"
    cursor.execute(QUERY)
    print(cursor.fetchall())

    # Count number of english chapters

    QUERY = "SELECT SUM(curChapters) FROM StoryHeaders where language=1;"
    cursor.execute(QUERY)
    print(cursor.fetchall())

    # Confirm this many exist in the data
    QUERY = "SELECT COUNT(Chapters.idx) FROM StoryHeaders INNER JOIN Chapters on StoryHeaders.id = Chapters.storyId WHERE StoryHeaders.language=1;"
    cursor.execute(QUERY)
    for row in cursor:
        print(row)

    # Count the number of terms in english fanfictions

    QUERY = "SELECT SUM(words) FROM StoryHeaders where language=1;"
    cursor.execute(QUERY)
    for row in cursor:
        print(row)
     

    QUERY = "SELECT storyId, idx, text FROM Chapters;"
    cursor.execute(QUERY)

    # Close the database connection
    conn.close()
    """
    
    CREATE_TABLE_QUERY = """
                CREATE TABLE ChaptersWithStoryInfo AS
                SELECT (chp.storyID*1000+chp.idx) AS docID,
                CASE   
                    WHEN chp.idx = 0 THEN chp.text || "." || sh.description || "." || sh.title || "." || group_concat(auth.name,',')
                    ELSE chp.text
                END AS text
                FROM StoryHeaders sh
                JOIN Chapters chp ON chp.storyId = sh.id
                JOIN AuthorLinks al ON sh.id = al.storyId
                JOIN Authors auth ON al.authorId = auth.id
                GROUP BY docId;
    """

    QUERY = """
    SELECT (chp.storyID*1000+chp.idx) AS docID,
        CASE   
            WHEN chp.idx = 0 THEN COALESCE(chp.text, '') || "." || COALESCE(sh.description, '') || "." || COALESCE(sh.title, '') || "." || COALESCE(group_concat(auth.name, ', '), '')
            ELSE chp.text
        END AS text
    FROM Chapters chp
    LEFT JOIN StoryHeaders sh ON chp.storyId = sh.id
    LEFT JOIN AuthorLinks al ON sh.id = al.storyId
    LEFT JOIN Authors auth ON al.authorId = auth.id
    GROUP BY docID;
    """

    EMERGENCY_QUERY = """
    SELECT (chp.storyID*1000+chp.idx) AS docID, chp.text
    FROM Chapters chp;
    """

    QUERY_FOR_WHEN_CHAPTERSWITHSTORYINFO_EXISTS = "SELECT docID, text FROM ChaptersWithStoryInfo;"

    # Update the paths in the following two lines: the first is where you read the db from
    # the second where to write the chunks to.
    dbIdx = ChapterDBImporter(r"../ao3_dump/organizedData.sqlite3", EMERGENCY_QUERY)
    # dbIdx.importChaptersToIndex("./data/compressed-chapter-indexes/", 25000, limit=10000000, verbose=True)
    dbIdx.importTermCounts("./data/compressed-chapter-indexes", 25000, chunkLimit=35, verbose=True)
    dbIdx.importDocTerms(".data/compressed-chapter-indexes", 25000, chunkLimit=35, verbose=True)

    #index = PositionalInvertedIndexLoader.loadFromMultipleCompressedFiles("./data/compressed-chapter-indexes/", chunk_limit=50, verbose=True)

    # reloadedIndex = PositionalInvertedIndexLoader.loadFromMultipleCompressedFiles("./data/compressed-chapter-indexes/", verbose=True)

    # pii_single = PositionalInvertedIndexLoader.loadFromCompressedFile("./data/chapters-index-vbytes.bin")
    # print(pii_single == reloadedIndex)
