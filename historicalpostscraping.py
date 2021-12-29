"""
A script to scrape all comments in the last 30 days from locked posts in
r/wallstreetbets for daily discussion and moves tomorrow and put the comments
into text files.

The webscraping is done primarily by the pushshift api for most old posts.
However, for posts created in the last 48 hours, the PRAW library is used, as
pushshift api needs time to scrape the data. The PRAW method is slower as Reddit
places an artificial cap of 1 operation/second. As a result, it takes 30-40 min
for the PRAW library to expand all the comments due to the large number of
comments that must be scraped.

Logan Kraver
Started: 11/5/2021
Last Edited: 11/8/2021
"""

import webscraping

if __name__ == "__main__":
    #variables
    url = 'https://www.reddit.com/r/wallstreetbets/?f=flair_name%3A%22Daily%20Discussion%22'
    PATH = r'file\path\to\input\comment\data'
    commentlist = webscraping.commentlist

    #dailydiscussionthread posts
    dailydiscussionlinks = webscraping.searchpostlinks(url,0)
    dailydiscussionlinks = webscraping.getpast30dayslinks(dailydiscussionlinks,PATH,0)
    webscraping.getallcommentslocked(PATH,dailydiscussionlinks,0)

    #movestomorrowthread posts
    movestomorrowlinks = webscraping.searchpostlinks(url,1)
    movestomorrowlinks = webscraping.getpast30dayslinks(movestomorrowlinks,PATH,1)
    webscraping.getallcommentslocked(PATH,movestomorrowlinks,1)
