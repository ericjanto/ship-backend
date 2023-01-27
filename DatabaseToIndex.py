import sqlite3
from bs4 import BeautifulSoup as bs
from PositionalInvertedIndexFactory import PositionalInvertedIndexFactory

class DatabaseToIndex:
    def __init__(self, dbPathName, tableName):
        print("HI")
        self.conn = sqlite3.connect(dbPathName)
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT (storyId || '-' || idx) AS docID, text FROM "+tableName)
        self.rows = self.cursor.fetchall()
        self.docIDs = [row[0] for row in self.rows]
        self.documents = [row[1] for row in self.rows]

    def conbvertChaptersToXML(self):
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

    """
    function that continously writes to a binary file
    """

    def indexChapters(self):
        pidxFactory = PositionalInvertedIndexFactory()
        docTerms = PositionalInvertedIndexFactory.preprocessDocs(self.documents)
        return pidxFactory.generateIndexFromPreprocessedDocs(docTerms, self.docIDs)
        
        
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
    dbIdx = DatabaseToIndex("smallerDB.sqlite3", "Chapters")
    dbIdx.indexChapters().writeToBinary("index.bin")
    dbIdx.closeConn()