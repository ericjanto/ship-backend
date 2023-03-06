from typing import List

import bisect


class TagPositionalInvertedIndex:
    """
    Structure:
    HashMap<String Tag, List<StoryIDs>>
    """

    def __init__(self):
        self.tags = dict()

        # TODO: Don't believe there is any reason
        #  for these fields to exist
        self.storyIDs = set()
        self.storyCount = 0

    def insertTagInstance(self, tag: str, storyID: int) -> None:
        if storyID not in self.storyIDs:
            self.storyIDs.add(storyID)
            self.storyCount += 1

        if tag not in self.tags:
            self.tags[tag] = [storyID]
            return

        bisect.insort(self.tags[tag], storyID)
        return

    def insertStoryIDs(self, tag: str, storyIDs: List[int]) -> None:
        """Insert a list of storyIDs that feature the specified tag"""
        if tag not in self.tags:
            self.tags[tag] = storyIDs
        else:
            for storyId in storyIDs:
                self.insertTagInstance(tag, storyId)

    def getStoryIDsWithTag(self, tag: str) -> List[int]:
        if tag not in self.tags:
            return []
        return self.tags[tag]

    def getTagFrequency(self, tag: str) -> int:
        if tag not in self.tags:
            return 0
        return len(self.tags[tag])

    def mergeWithOtherIndex(self, otherTagPositionalInvertedIndex) -> None:
        """Merges the contents of another index into this one"""
        for tag in otherTagPositionalInvertedIndex.tags:
            for docID in otherTagPositionalInvertedIndex.tags[tag]:
                self.insertTagInstance(tag, docID)


    def __eq__(self, other) -> bool:
        if not isinstance(other, TagPositionalInvertedIndex):
            return False

        return (self.tags == other.tags 
                and self.storyIDs == other.storyIDs 
                and self.storyCount == other.storyCount)


if __name__ == "__main__":
    index = TagPositionalInvertedIndex()
    index.insertTagInstance("Testing", 123)
    index.insertTagInstance("Testing2", 50)
    index.insertTagInstance("Testing", 10)
    index.insertTagInstance("Testing2", 500)

    for tag in index.tags:
        print(index.tags[tag])