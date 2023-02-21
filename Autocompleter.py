from rich.progress import Progress

from PrefixTree import PrefixTree
from TagPositionalInvertedIndexLoader import TagPositionalInvertedIndexLoader


class Autocompleter:
    """
    Provides prefix autocomplete for the keys of a PI-index.

    We use it for tag autocompletion.

    In theory, we could autocomplete other index keys as well,
    but they are likely to be preprocessed and would offer less value
    to an end-user.
    """
    def __init__(self, path_to_compressed_tag_index: str) -> None:
        self.pt = None
        self.tag_index = None

        # Update index and pt
        self.build_prefix_tree(path_to_compressed_tag_index)

    def get_ranked_autocomplete(self, prefix: str, n: int):
        """
        Rank by freq and then lexical string order

        NOTE: sorting for every request might be too expensive for cases
        where there are many leaves which share the same prefix?
        """

        completed_tags = self.pt.autocomplete(prefix.lower())

        # k[0] = frequency of tag, k[1] is tag itself
        key_sort = lambda k: (k[1], Reversor(k[0]))
        sorted_results_n = sorted(completed_tags, key=key_sort, reverse=True)[:n]

        return sorted_results_n

    def build_prefix_tree(self, path_to_compressed_tag_index: str) -> None:
        """
        - Decompress tag index
        - Obtain tags by looking at keys
        - Build tree with tags
        - Update self.tag_index and self.pt

        NOTE: re:performance, this takes ~15s on an M2 machine, with an index
            containing 1491127 tags. This might not be efficient enough / we
            might want to only do this once.
        """
        print("Decompressing index")
        self.tag_index = TagPositionalInvertedIndexLoader.loadFromCompressedFile(
            path_to_compressed_tag_index
        )
        tags = list(self.tag_index.tags.keys())
        self.pt = PrefixTree()

        with Progress() as p:
            task = p.add_task("Building tree...", total=len(tags))
            for t in tags:
                f = self.tag_index.getTagFrequency(t)
                self.pt.insert(t, f)
                p.advance(task)


class Reversor:
    """
    Used for being able to sort by two keys, one of them reversed.

    See https://stackoverflow.com/a/56842689/.
    """

    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj


if __name__ == '__main__':
    PATH_TAG_INDEX = 'data/compressedTagIndex.bin'
    autocompleter = Autocompleter(PATH_TAG_INDEX)

    n = 5
    print(autocompleter.get_ranked_autocomplete('angst', n))
    print(autocompleter.get_ranked_autocomplete('Angst', n))