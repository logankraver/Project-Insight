"""
A script to find the most recent unlocked post in r/wallstreetbets and get the
comments in real-time. After the post is locked, the comments are put into a
text file.

The webscraping is done by first loading through selenium the search for all
recent daily discussion posts to get all links of recent posts. Afterwards, the
first unlocked post is selected and is loaded separately through selenium and
all comments are scraped to a commentlist. The post is than closed and the
script sleeps for 10 seconds and repeats the process, while the post remains
unlocked. Once the post locks, the commentlist is added to a text file.

Logan Kraver
Started: 11/5/2021
Last Edited: 11/8/2021
"""

import webscraping

if __name__ == "__main__":
    #variables
    url = 'https://www.reddit.com/r/wallstreetbets/?f=flair_name%3A%22Daily%20Discussion%22'
    PATH = r'file\path\to\input\comment\data'

    #dailydiscussionthread posts
    dailydiscussionlinks = webscraping.searchpostlinks(url,0)
    webscraping.getallcommentsunlocked(dailydiscussionlinks,0)

    #movestomorrowthread posts
    movestomorrowlinks = webscraping.searchpostlinks(url,1)
    webscraping.getallcommentsunlocked(movestomorrowlinks,1)
