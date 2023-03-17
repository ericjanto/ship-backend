#!/usr/bin/python3.9
import json
from time import sleep
from matplotlib.font_manager import json_dump
import re
import requests
import datetime
import subprocess
import os
from time import sleep
from bs4 import BeautifulSoup

from TermCountsClient import TermCountsClient
from StoryMetadataClient import StoryMetadataClient
from PIIClientFastAPI import PIIClientFlask
from TagPIIClientFastAPI import TagPIIClientFastAPI
from WebScraperImporter import WebScraperImporter

NoneType = type(None)

class WebScraper():

    NoneType = type(None)

    def __init__(self):
        self.piiClientFlask = PIIClientFlask('localhost', 5001)
        self.tagPIIClient = TagPIIClientFastAPI('localhost', 5002)
        self.termCountsClient = TermCountsClient('localhost', 5003)
        self.storyMetadataClient = StoryMetadataClient('localhost', 5004)
        self.wsImporter = WebScraperImporter()
        self.outputPath =  'data/WebScraperImports/'
        self.pathCH = 'WebScraped-Chapters/'
        self.pathMD =' WebScraped-Metadata/'
        self.pathTg = 'WebScraped-Tags/'
        self.pathTC = 'WebScraped-TermCounts/'
        assert isinstance(self.wsImporter, WebScraperImporter)
        assert isinstance(self.tagPIIClient, TagPIIClientFastAPI)
        assert isinstance(self.piiClientFlask, PIIClientFlask)
        assert isinstance(self.termCountsClient, TermCountsClient)
        assert isinstance(self.storyMetadataClient, StoryMetadataClient)

        if not os.path.exists('scrapes'):
            os.makedirs('scrapes')

    def scrape(self):
        # get yesterday's date
        yesterday_fmt = datetime.date.today() - datetime.timedelta(days=1)

        # format the date as a string in the format YYYY-MM-DD
        self.yesterday = yesterday_fmt.strftime('%Y-%m-%d')

        self.fName1 = 'scrapes/chapters'+self.yesterday+'.json'
        self.fName2 = 'scrapes/metaData'+self.yesterday+'.json'  

        self.meta = 'metadata-{}.bin'.format(self.yesterday)
        self.tags = 'tags-{}.bin'.format(self.yesterday)
        self.chaps = 'chapters-{}.bin'.format(self.yesterday)
        self.terms = 'termCounts-{}.bin'.format(self.yesterday)

        # URL for the Harry Potter fandom on Archive of Our Own
        url = 'https://archiveofourown.org/works?work_search%5Bsort_column%5D=created_at&work_search%5Bother_tag_names%5D=&work_search%5Bexcluded_tag_names%5D=&work_search%5Bcrossover%5D=&work_search%5Bcomplete%5D=&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D=&work_search%5Bdate_from%5D='+self.yesterday+'&work_search%5Bdate_to%5D='+self.yesterday+'&work_search%5Bquery%5D=&work_search%5Blanguage_id%5D=&commit=Sort+and+Filter&tag_id=Harry+Potter+-+J*d*+K*d*+Rowling'

        # Retrieve the page HTML using requests
        page = requests.get(url).text

        # Parse the page HTML using BeautifulSoup
        soup = BeautifulSoup(page, 'html.parser')

        # Find the second-to-last item in the list of pages in the navigation bar
        num_pages = int(soup.find(class_='pagination actions').find_all('li')[-2].get_text())
        print(num_pages)
        # Dictionary to store the results for each unique story
        results = {}

        # Iterate over each page of stories
        for page_num in range(1, num_pages + 1):

            #url reset
            url2 = 'https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works?commit=Sort+and+Filter&page='+ str(page_num) +'&work_search%5Bcomplete%5D=&work_search%5Bcrossover%5D=&work_search%5Bdate_from%5D='+self.yesterday+'2&work_search%5Bdate_to%5D='+self.yesterday+'&work_search%5Bexcluded_tag_names%5D=&work_search%5Blanguage_id%5D=&work_search%5Bother_tag_names%5D=&work_search%5Bquery%5D=&work_search%5Bsort_column%5D=created_at&work_search%5Bwords_from%5D=&work_search%5Bwords_to%5D='

            # Construct the URL for the page of stories
            page_url = url2

            # Retrieve the page HTML using requests
            page = requests.get(page_url).text

            # Parse the page HTML using BeautifulSoup - can replace the original soup now we have page numbers
            soup = BeautifulSoup(page, 'html.parser')

            # Find the list of stories on the page
            story_list = soup.find(class_='work index group')
            
            # print(story_list.find_all('li'))
            preamble = soup.find('pre')
            if preamble:
                text = preamble.text.strip() == 'Retry later'
                print('AO3 Failed to load page listings | ',text, 'Retry last page after 5 mins')
                sleep(300)
                page_num -= 1
                break

            metaData = {}
            results = {}

            if page_num%5 == 0:
                print("sleeping for 5 mins to avoid IP restrictions")
                sleep(300)

            # Iterate over each story in the list
            for story in story_list.find_all('li', {'role': 'article'}):
                
                # Retrieve the story ID from the story link
                story_link = story.find(class_='heading').find('a')
                story_id = story_link['href'].split('/')[-1]

                fullView = '?view_full_work=true'
                adultTrue = '?view_adult=true'

                storyURL = 'https://archiveofourown.org/works/'+ story_id + fullView

                badreadURL = 'https://archiveofourown.org/works/'+ story_id + adultTrue + fullView

                #print(storyURL)
                print("story", story_id)
                print("on page" ,page_num)
                
                storypage = requests.get(storyURL).text

                # Parse the page HTML using BeautifulSoup
                worksoup = BeautifulSoup(storypage, 'html.parser')

                #heading group with tags etc
                heading_group = worksoup.find('dl', class_='work meta group')

                # preface with title/author and notes
                preface_group = worksoup.find('div', class_='preface group')

                # find the main content section of the page
                main_content = worksoup.find('div', {"id": "chapters"})

                pre = soup.find('pre')
                if pre:
                    text = pre.text.strip() == 'Retry later'
                    print('AO3 Failed to load page, skipping story | ',text)
                    break

                if main_content is []:
                    break

                try:
                    # extract the summary of the story (if any)

                    regex = re.compile('([a-zA-Z]\"[a-zA-Z])', re.S)
                    

                    summary = preface_group.find('blockquote', class_='userstuff')
                    if summary:
                        summary = regex.sub(lambda m: m.group().replace('<br>',"\\n",1), summary.text)
                        # print(summary.text.strip())
                        summary = summary.strip()
                        # print(summary)
                    else:
                        summary = ''
                    # print(summary)

                    # extract the title of the story
                    title = preface_group.find('h2', class_='title heading').text.strip()

                    # extract the author of the story
                    author = preface_group.find('a', rel='author')
                    if author:
                        author = author.text.strip()
                    else:
                        author = preface_group.find('h3', class_='byline heading').text.strip()

                except Exception as prefaceError:
                    print(prefaceError)
                    summary = ''
                    author = 'Anonymus'
                    title = 'Undefined'

                
                # extract the rating tags of the story (if any)
                ratingsec = heading_group.find('dd', class_='rating tags')
                if ratingsec:
                    ratingTags = [tag.text.strip() for tag in ratingsec.find_all('li')]
                else:
                    ratingTags = []

                # extract the warning tags of the story (if any)
                warningsec = heading_group.find('dd', class_='warning tags')
                if warningsec:
                    warningTags = [tag.text.strip() for tag in warningsec.find_all('li')]
                else:
                    warningTags = []

                # extract the category tags of the story (if any)
                catagorysec = heading_group.find('dd', class_='category tags')
                if catagorysec:
                    categoryTags = [tag.text.strip() for tag in catagorysec.find_all('li')]
                else:
                    categoryTags = []

                # extract the fandom of the story(if one)
                fandomsec = heading_group.find('dd', class_='fandom tags')
                if fandomsec:
                    fandomTags = [tag.text.strip() for tag in fandomsec.find_all('li')]
                else:
                    fandomTags = []

                # extract the relationships of the story (if any)
                relsec = heading_group.find('dd', class_='relationship tags')
                if relsec:
                    relationshipTags = [tag.text.strip() for tag in relsec.find_all('li')]
                else:
                    relationshipTags = []

                # extract the characters of the story (if any)
                charsec = heading_group.find('dd', class_='character tags')
                if charsec:
                    characterTags = [tag.text.strip() for tag in charsec.find_all('li')]
                else:
                    characterTags = []

                # extract the freeform tags of the story (if any)
                freesec = heading_group.find('dd', class_='freeform tags')
                if freesec:
                    freeformTags = [tag.text.strip() for tag in freesec.find_all('li')]
                else:
                    freeformTags = []


                # extract the language of the story (if one)
                language_section = heading_group.find('dd', class_='language')
                if language_section:
                    language = language_section.text.strip()
                else:
                    language = 'English?'

                # extract the stats of the story
                stats_section = heading_group.find('dl', class_='stats')
                stats = {}

                # published
                pubsec = stats_section.find('dt', class_='published')
                if pubsec:
                    pubData = stats_section.find('dd', class_="published").text.strip()
                else:
                    pubData = '-999'

                # status
                statsec = stats_section.find('dt', class_='status')
                if statsec:
                    statData = stats_section.find('dd', class_="status").text.strip()
                else:
                    statData = '-999'

                # words
                wordsec = stats_section.find('dt', class_='words')
                if wordsec:
                    wordData = stats_section.find('dd', class_="words").text.strip()
                else:
                    wordData = '0'

                # chapters
                chapsec = stats_section.find('dt', class_='chapters')
                if chapsec:
                    chapData = stats_section.find('dd', class_="chapters").text.strip()
                else:
                    chapData = '0'

                # comments
                commentsec = stats_section.find('dt', class_='comments')
                if commentsec:
                    commentData = stats_section.find('dd', class_="comments").text.strip()
                else:
                    commentData = '0'

                # kudos
                kudosec = stats_section.find('dt', class_='kudos')
                if kudosec:
                    kudoData = stats_section.find('dd', class_="kudos").text.strip()
                else:
                    kudoData = '0'

                # bookmarks
                bookmarksec = stats_section.find('dt', class_='bookmarks')
                if bookmarksec:
                    bookmarkData = stats_section.find('dd', class_="bookmarks").text.strip()
                else:
                    bookmarkData = '0'

                # hits
                hitsec = stats_section.find('dt', class_='hits')
                if hitsec:
                    hitData = stats_section.find('dd', class_="hits").text.strip()
                else:
                    hitData = '0'

                # stat_value = [stat.text.strip() for stat in stats_section.find_all('dd')]
                # stat_label = [statName.text.strip() for statName in stats_section.find_all('dt')]
                
                # stats = list(zip(stat_label, stat_value))
                
                stats.update({"published":pubData,
                            "status":statData,
                            "words":wordData,
                            "chapters":chapData,
                            "comments":commentData,
                            "kudos":kudoData,
                            "bookmarks":bookmarkData,
                            "hits":hitData
                            })
                
                # print(stats)

                #=============================================== skip notes
                # extract the notes section of the story (if any)
                # notes_section = main_content.find('div', class_='notes')
                # if notes_section:
                #     notes = notes_section.text.strip()
                # else:
                #     notes = ''
                #===========================================================


                metaDataKey = story_id
                meta = {'author':author,
                        'title':title,
                        'summary':summary,
                        'warnings':warningTags,
                        'ratings':ratingTags,
                        'categories':categoryTags,
                        'fandom': fandomTags,
                        'relationships':relationshipTags,
                        'characters':characterTags,
                        'freeform': freeformTags,
                        'language': language,
                        'stats':stats
                    }
                metaData.update({story_id:meta})
                # print(metaData[story_id])

                chNames = []
                chContents = []

                # look for chapters in the main body
                ch_list = main_content.find_all('div', class_='chapter')
                chapSingle = main_content.find('div', class_='userstuff')

                regex = re.compile('([a-zA-Z]\"[a-zA-Z])', re.S)

                if ch_list:
                    # print("ChGroup", ch_list)
                
                    print('chaptergroup', len(ch_list))
                    for i in range(0, len(ch_list), 2):
                        
                        try:
                            name_div = ch_list[i+1].find('div', {'role': 'complementary'}, class_='chapter preface group')
                        except:
                            name_div=ch_list[-1]

            
                        if not isinstance(name_div, NoneType):
                            chNames.append(name_div.text.strip())
                        else:
                            chNames.append('')
                        # print("got chapter name")

                        content = ch_list[i].find('div', class_='userstuff module')
                        # print("got chapter content")

                        # print("content: ",content.find_all('p'))

                        if isinstance(content, NoneType):
                            chContents = ''
            
                        elif content:
                            # print("list comp paras")
                            Contents = [regex.sub(lambda m: m.group().replace('<br>',"\\n",1), para.text).strip() for para in content.find_all('p')]
                            chContents = '\n'.join(Contents)
                        else:
                            chContents = ''

                        # print(chContents)
                        
                        # Store the results for the story in the dictionary
                        chapterID = round(round(int(story_id),12) * 1000 + round(i/2), 12)
                        # print("chapter vs chapter ID - {}|{}".format(i, chapterID))

                        results.update({chapterID: chContents})

                elif chapSingle:
                    # print("single Section Text")
                    chapterID = round(int(story_id) * 1000, 12)
                    content = regex.sub(lambda m: m.group().replace('<br>',"\\n",1), chapSingle.text).strip()
                    results.update({chapterID: content})

                else:
                    print('No Text')
                    chapterID = round(int(story_id) * 1000, 12)
                    results.update({chapterID: ''})

                print("sleep 1 sec -> next post")
                sleep(1)

        # print(results)

        with open(self.fName1, 'w', encoding='utf8') as f1:
            json.dump(results, f1, ensure_ascii=False, indent='\t')

        with open(self.fName2, 'w', encoding='utf8') as f2:
            json.dump(metaData, f2, ensure_ascii=False, indent='\t')

        self.convertAndMerge()

    def convertAndMerge(self):  
        self.wsImporter.convertWebScrapeDumpsToIndexChunks(self.fName1, self.fName2, self.outputPath, self.yesterday)
        self.piiClientFlask.mergeWithOtherIndex(self.outputPath+self.pathCH+self.chaps)
        self.tagPIIClient.mergeWithOtherIndex(self.outputPath+self.pathTg+self.tags)
        self.termCountsClient.mergeWithOtherIndex(self.outputPath+self.pathTC+self.terms)
        self.storyMetadataClient.mergeWithOtherIndex(self.outputPath+self.pathMD+self.meta)

        