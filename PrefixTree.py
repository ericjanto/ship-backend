from typing import List, Tuple


class TrieNode:
    """
    Each node holds a text bit which is either
    a tag (is_tag) or a prefix of a tag (!is_tag).

    freq keeps track of how often a tag occurs in the index,
    for ranking purposes.

    freq > 0 implies is_tag, but we keep it explicit for clarity.
    """

    def __init__(self, text: str = "", freq: int = 0):
        self.text = text
        self.children = {}
        self.is_tag = False
        self.freq = freq


class PrefixTree:
    """
    Tree data structure which we use for locating tags which have
    a given prefix ("autocomplete").

    For more information:
        - https://en.wikipedia.org/wiki/Trie
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, tag: str, freq: int) -> None:
        """
        Inserts a new tag into the tree, along with its frequency
        of occuring in the index.
        """
        current = self.root
        for i, char in enumerate(tag):
            if char not in current.children:
                prefix = tag[0 : i + 1]
                current.children[char] = TrieNode(prefix)
            current = current.children[char]
        current.is_tag = True
        current.freq = freq

    def find(self, tag: str) -> TrieNode | None:
        """
        Finds the TrieNode representing the given tag if it exists.
        Returns None if not found.
        """
        current = self.root
        for char in tag:
            if char not in current.children:
                return None
            current = current.children[char]

        if current.is_word:
            return current

    def autocomplete(self, prefix: str) -> List[str]:
        """
        Returns a list of all words beginning with the given prefix, or
        an empty list if no words begin with that prefix.

        NOTE: you might want to preprocess the prefix according to the
        preprocessing the tree leaves received before insertion.
        """
        tags = []
        current = self.root
        for char in prefix:
            if char not in current.children:
                return []
            current = current.children[char]

        self.__child_words_for(current, tags)
        return tags

    def __child_words_for(self, node: TrieNode, tags: List[Tuple[str, int]]):
        """
        Cycles through all children
        of node recursively, adding them to words if they
        constitute whole words (as opposed to merely prefixes).
        """
        if node.is_tag:
            tags.append((node.text, node.freq))
        for letter in node.children:
            self.__child_words_for(node.children[letter], tags)
