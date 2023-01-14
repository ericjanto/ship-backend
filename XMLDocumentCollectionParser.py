from bs4 import BeautifulSoup as bs

class XMLDocumentCollectionParser():

    def __init__(self, filename):
        self.filename = filename

        self.documents = []
        with open(filename, 'r', encoding="utf-8") as f:
            fileContents = f.read()
            xmlContent = bs(fileContents, "lxml")
            self.documents = xmlContent.find_all('doc')

        self.documentCount = len(self.documents)
        self.currentDocument = 0

    # TODO: Update this so that it only reads chunks at a time
    def yieldNextDocument(self, tagsToInclude=['headline', 'text']):
        if self.currentDocument == self.documentCount:
            return None
        document = ""
        for tag in tagsToInclude:
            content = self.documents[self.currentDocument].find_all(tag)
            for string in content:
                document += string.text.strip().lstrip() + " "
        docID = self._extractDocIDFromDocument(self.documents[self.currentDocument])
        self.currentDocument += 1
        return (docID, document)

    def yieldAllRemainingDocuments(self):
        docs = []
        while (self.currentDocument != self.documentCount):
            docs.append(self.yieldNextDocument())
        return docs

    def yieldSpecificDocument(self, docID, tagsToInclude=['headline', 'text']):
        for document in self.documents:
            if self._extractDocIDFromDocument(document) == docID:
                text = ""
                for tag in tagsToInclude:
                    content = document.find_all(tag)
                    for string in content:
                        text += string.text.strip() + " "
                return text
        return ""


    def resetGeneratorPosition(self):
        self.currentDocument = 0

    def _extractDocIDFromDocument(self, document):
        return int(document.find("docno").text)

if __name__ == "__main__":
    parser = XMLDocumentCollectionParser("data/lab2data/trec.sample.xml")
    print(parser.yieldNextDocument())