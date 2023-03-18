from BooleanSearchEngine import BooleanSearchEngine
from preprocessing import loadStopWordsIntoSet
from bm25 import BM25_Model
from indexDecompressor import IndexDecompressor
from WildcardSearch import create_permuterm_index_trie
from TagPositionalInvertedIndexLoader import TagPositionalInvertedIndexLoader
from StoryMetadataLoader import StoryMetadataLoader
from QueryCache import QueryCache
import pickle
import numpy as np
import re
import copy

query_examples = ["Who what who were AND (what OR (where AND are you))",
                  "supernatural and doctor who superwholock",
                  "superwholock",
                  "bionicles",
                  "Bob Fraser in a zombie apocalypse",
                  "Doctor Who",
                  "Doctor Mallard",
                  "mix of words with \"Tails * bench\"",
                  "\"Tails * bench\"",
                  "Other terms with Mon*",
                  '"harry potter"',
                  "harry potter"]
                 
harder_queries = ["Mon*",
                  "Mon*",
                  "Mon*",
                  "Mon*",
                  "Mon*",
                  "Mon*",
                  "Mon*",
                  "Mon*",
                  "Mon*",
                  "TAG{anime} OR TAG{manga} deku vs todoroki",
                  "TAG{anime} TAG{manga}"]

CONNECTIVES = ['AND','OR','and','or']

filter_dict = {'singleChapter':False, 'completionStatus':'all', 'language':1, 
                'wordCountFrom':-1, 'wordCountTo':-1, 
                'hitCountFrom':-1, 'hitCountTo':-1, 
                'kudosCountFrom':-1, 'kudosCountTo':-1, 
                'commentCountFrom':-1, 'commentCountTo':-1, 
                'bookmarkCountFrom':-1, 'bookmarkCountTo':-1, 
                'lastUpdatedFrom':-1, 'lastUpdatedTo':-1}

class Search_Engine():
    def __init__(self,positionalInvertedIndex,permutermIndexTrie,tagIndex,metadataDict,stopwords,termcounts,cache_size=1000):
        self.index = positionalInvertedIndex
        self.stopwords = stopwords
        self.termcounts = termcounts
        self.permutermIndexTrie = permutermIndexTrie
        self.tagIndex = tagIndex
        self.metadataDict = metadataDict
        self.fullqueryCache = QueryCache(cache_size)
        self.queryCache = QueryCache(cache_size)
        self.boolean_engine = BooleanSearchEngine(self.index,self.permutermIndexTrie,self.metadataDict,self.stopwords)
        self.ranker = BM25_Model(self.index,self.stopwords,self.termcounts)
        all_docIDs = self.index.getDocIDs()
        total_term_counts = sum(self.termcounts.get_tokens_before_stemming(all_docIDs).values())
        self.avg_doc_len = total_term_counts/len(all_docIDs)
        self.tag_regex = re.compile(r'TAG{ *\w+ *}')
        self.proximity_regex = re.compile(r'#\d+\s*\(\s*\w+(\s*,\s*\w+\s*)*\)')
    
    def search(self,query,**kwargs):
        assert self.check_args(kwargs)
        query_filters = {'singleChapter':False, 'completionStatus':'all', 'language':1, 
                'wordCountFrom':-1, 'wordCountTo':-1, 
                'hitCountFrom':-1, 'hitCountTo':-1, 
                'kudosCountFrom':-1, 'kudosCountTo':-1, 
                'commentCountFrom':-1, 'commentCountTo':-1, 
                'bookmarkCountFrom':-1, 'bookmarkCountTo':-1, 
                'lastUpdatedFrom':-1, 'lastUpdatedTo':-1}
        
        query_key = query
        for key in kwargs:
            query_filters[key] = kwargs[key]
            query_key += f' {key}:{kwargs[key]}'
        
        if self.fullqueryCache.exists(query_key):
            return self.fullqueryCache.get(query_key)
        else:
            original_query = query
            query = query.replace('"',' " ')
            query = query.replace('TAG{','TAG{ ')
            query = query.replace('}',' }')
            tokens = query.split()
            new_tokens = []
            for token in tokens:
                if not self.proximity_regex.search(token):
                    token = token.replace('(', ' ( ')
                    token = token.replace(')', ' ) ')
                    new_tokens += token.split()
                else:
                    new_tokens.append(token)
            tokens = new_tokens

            if self.queryCache.exists(original_query):
                all_doc_IDs = self.queryCache.get(original_query)
            else:
                all_doc_IDs = self.recur_connectives(tokens)
                self.queryCache.push(original_query,all_doc_IDs)
                
            tokens = self.tag_regex.sub('',query).split()
            tokens = [token for token in tokens if '*' not in token]
            query = ' '.join(tokens)
            terms = self.ranker.preprocess_query(query)    
            all_doc_IDs = self.apply_filters(all_doc_IDs,query_filters)
            doc_score_pairs = dict.fromkeys(all_doc_IDs,0)
            query_scores = self.ranker.score_documents(terms,all_doc_IDs)
            for docID,score in query_scores:
                doc_score_pairs[docID] += score

            final_results = sorted(doc_score_pairs.items(),key=lambda x: x[1], reverse=True)
            self.fullqueryCache.push(query_key,final_results)
        return final_results

    def recur_connectives(self,subquery):
        split_query = self.bracketed_split(subquery,CONNECTIVES,strip_brackets=True)
        if 'AND' in split_query or 'and' in split_query:
            token_1 = self.recur_connectives(split_query[0])
            token_2 = self.recur_connectives(split_query[-1])
            return token_1.intersection(token_2)
        elif 'OR' in split_query or 'or' in split_query:
            token_1 = self.recur_connectives(split_query[0])
            token_2 = self.recur_connectives(split_query[-1])
            return token_1.union(token_2)
        else:
            tags = []
            tag_latch = False
            tag = []
            for token in split_query[0]:
                if '}' == token:
                    tag_latch = False
                    tags.append(' '.join(tag))
                    tag = []
                if tag_latch:
                    tag.append(token)
                if 'TAG{' == token:
                    tag_latch = True
            tag_results = None
            results = set()
            if tags:
                tag_results = self.tag_search(tags)
            else:
                quotes,or_str = self.quote_split(split_query[0])
                if quotes:
                    query_str = ' OR '.join([f"\"{' '.join(quote)}\"" for quote in quotes])
                else:
                    query_str = ' OR '.join(or_str)
                results = set(self.boolean_engine.makeQuery(query_str,debugVerbose=False))
            return tag_results if tags else results
    
    def apply_filters(self, docIDs, filter_params):
        range_fields = ['wordCount','hitCount','kudosCount',
                        'commentCount','bookmarkCount','lastUpdated']
        filtered_storyIDs = []
        storyIDs = [int(docID)//1000 for docID in list(docIDs)]
        story_descs = self.metadataDict.getStoryDescriptors(storyIDs)
        story_stats = self.metadataDict.getStats(storyIDs)
        story_language = self.metadataDict.getLanguage(storyIDs)
        storyIDs = [str(docID) for docID in storyIDs]

        for docID,storyID in zip(docIDs,storyIDs):
            if (not story_descs.get(storyID)) or (not story_stats.get(storyID)) or (not story_language.get(storyID)):
                continue
            isSingle = filter_params['singleChapter']
            status = filter_params['completionStatus']
            language = filter_params['language']

            if isSingle:
                chapterCountMatch = (
                                    isSingle and story_descs[storyID]['finalChapterCountKnown'] and story_descs[storyID]['finalChapterCount'] == 1
                                    ) or (
                                    isSingle and (not story_descs[storyID]['finalChapterCountKnown']) and story_descs[storyID]['currentChapterCount'] == 1
                                    )
                if not chapterCountMatch:
                    continue
            completionStatusMatch = (
                                    status == "all"
                                    ) or (
                                    status == "completed" and story_descs[storyID]['finished']
                                    ) or (
                                    status == "in-progress" and not story_descs[storyID]['finished']
                                    )
            if not completionStatusMatch:
                continue
            languageMatch = story_language[storyID] == language
            if not languageMatch:
                continue

            for field in range_fields:
                param = story_stats[storyID].get(field,-1)
                lowerBound = filter_params[field+'From']
                upperBound = filter_params[field+'To']
                flag = False
                if param>=0:
                    flag = self.parameterWithinBoundary(param,lowerBound,upperBound)
                if not flag:
                    break

            if not flag:
                continue

            filtered_storyIDs.append(docID)
            
        return filtered_storyIDs

    def parameterWithinBoundary(self, parameter, lowerBound, upperBound):
        return (lowerBound == -1 or parameter >= lowerBound) and (upperBound == -1 or parameter <= upperBound)

    def bracketed_split(self,string, delimiter, strip_brackets=False):
        openers = ['(']
        closers = [')']
        split_query = []
        current_string = []
        depth = 0
        for c in string:
            if c in openers:
                depth += 1
                if strip_brackets and depth == 1:
                    continue
            elif c in closers:
                depth -= 1
                if strip_brackets and depth == 0:
                    continue
            if depth == 0 and (c in delimiter):
                split_query += [current_string]
                split_query += [c]
                current_string = []
            else:
                current_string += [c]
        split_query += [current_string]
        return split_query

    def quote_split(self,string):
        or_str = []
        quotes = []
        curr_quote = []
        depth = 0
        for token in string:
            if token == '"' and depth == 0:
                depth += 1
                continue
            elif token == '"' and depth > 0:
                quotes += [curr_quote]
                curr_quote = []
                depth -= 1
                continue
            if depth > 0:
                curr_quote += [token]
            else:
                or_str += [token]
        return quotes,or_str

    def tag_search(self, tags):
        temp_tags = copy.deepcopy(tags)
        tag_search_results = self.tagIndex.getStoryIDsWithTag(temp_tags)
        docIDs = set([storyID*1000 for storyID in tag_search_results[temp_tags.pop()]])
        for tag in temp_tags:
            docIDs = docIDs.intersection(set([storyID*1000 for storyID in tag_search_results[tag]]))
        return docIDs
    
    def check_args(self,args):
        return all([key in filter_dict.keys() for key in args]) 
        

if __name__ == "__main__":
    with open('data/chapters-index-vbytes.bin','rb') as f:
        data = f.read()
        decompressor = IndexDecompressor(data)
        index = decompressor.toIndex()
    print("Index Loaded")

    tag_index = TagPositionalInvertedIndexLoader().loadFromCompressedFile('data/compressedTagIndex.bin')
    print("Tag Index Loaded")

    with open('data/termCounts.bin','rb') as f:
        data = f.read()
        term_counts = pickle.loads(data)
    print("Term counts Loaded")

    with open('data/doc-terms.pickle','rb') as f:
        data = f.read()
        doc_terms = pickle.loads(data)
    permuterm_index_trie = create_permuterm_index_trie(doc_terms)
    print("permuterm index tree constructed")

    metadata_dict = StoryMetadataLoader().loadFromCompressedFile('data/compressedMetadata.bin')
    print("Metadata Dict Loaded")

    stopwords = loadStopWordsIntoSet('englishStopWords.txt')
    print("Stopwords loaded")
    api = Search_Engine(index,permuterm_index_trie,tag_index,metadata_dict,stopwords,term_counts)

    print(api.search(query_examples[10])[:5])
    print(api.search(query_examples[11])[:6])
