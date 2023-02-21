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
        
        self.termCounter.saveToBin(os.path.join("./data/", "termCounts.bin"))



class DatabaseToIndex:
    def __init__(self, dbPathName, query):
        self.conn = sqlite3.connect(dbPathName)
        self.cursor = self.conn.cursor()
        self.cursor.execute(query)
        self.rows = self.cursor.fetchall()
        self.docIDs = [row[0] for row in self.rows]
        self.documents = [row[1] for row in self.rows]
        self.stopWords = loadStopWordsIntoSet('englishStopWords.txt')

    def convertChaptersToXML(self):
        """
        Converts the chapters in the database to XML
        """
        root = BeautifulSoup("<root></root>", "xml")
        # Iterate over the rows and create child elements for each row
        for row in self.rows:
            child = root.new_tag("DOC")
            id = root.new_tag("DOCNO")
            id.string = str(row[0])
            text = root.new_tag("TEXT")
            text.string = row[1].encode('ascii', 'ignore').decode('ascii')
            child.append(id)
            child.append(text)
            root.document.append(child)

        # Write the XML to a file
        with open("output.xml", "w") as file:
            file.write(root.prettify())
    
    def closeConn(self):
        self.cursor.close()

    def __indexChapters(self):
        """
        Indexes the chapters in the database
        """
        pidxFactory = PositionalInvertedIndexFactory()
        docTerms = PositionalInvertedIndexFactory.preprocessDocs(self.documents, stem=True, stopwords=self.stopWords)
        return pidxFactory.generateIndexFromPreprocessedDocs(docTerms, self.docIDs)

    def __storeAllUniqueTermCounts(self):
        tc = TermCounts(self.stopWords)
        tc.countTerms(self.docIDs, self.documents)
        tc.saveToBin('./data/term-counts.bin')
    
    def __storeAllUniqueTermsBeforeProcessing(self):
        """
        Stores the unique terms in the database before processing
        """
        docTerms = set()
        for document in self.documents:
            pidxFactory = PositionalInvertedIndexFactory()
            docTerms.update(set(PositionalInvertedIndexFactory.preprocessDocs([document], stem=False, stopwords=self.stopWords)[0]))
            # store doc terms in pickle file 
        with open('./data/doc-terms.pickle', 'wb') as f:
            pickle.dump(docTerms, f)
        

    
    def storeUniqueTermsAndIndex(self):
        """
        Stores the unique terms in the database and indexes the chapters
        """
        self.__storeAllUniqueTermsBeforeProcessing()
        print("Unique terms stored")
        self.__storeAllUniqueTermCounts()
        print("Term counts stored")
        pii =  self.__indexChapters()
        print("Indexing completed")
        PositionalInvertedExporter.saveToCompressedIndex(pii, "./data/chapters-index-vbytes.bin")
        print("Saved index as vbytes")
        
            
        
        
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

    CREATE_TABLE_QUERY_2 = """
    CREATE TABLE ChaptersWithStoryInfo AS
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
    QUERY = "SELECT docID, text FROM ChaptersWithStoryInfo;"
    ### Create a table for the query above
    
    # dbIdx = DatabaseToIndex("smallerDB.sqlite3", QUERY)
    # dbIdx.storeUniqueTermsAndIndex()
    # dbIdx.closeConn()

    # dbIdx = ChapterDBImporter("smallerDB.sqlite3", QUERY)
    # dbIdx.importChaptersToIndex("./data/compressed-chapter-indexes/", 2000)

    reloadedIndex = PositionalInvertedIndexLoader.loadFromMultipleCompressedFiles("./data/compressed-chapter-indexes/", verbose=True)
    pii_single = PositionalInvertedIndexLoader.loadFromCompressedFile("chapters-index-vbytes.bin")
    print(pii_single == reloadedIndex)
