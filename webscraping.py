"""
A module to scrape r/wallstreetbets to get all comments from the general daily
discussion reddit posts + what are your moves tomorrow posts

This module uses selenium to load the website and find all the links for each
post and uses those links to find the comments for the respective posts in the
last 30 days. To scrape the posts, the module uses the pushshift api to get a
json, the PRAW library, or selenium depending on whether the post is locked or
unlocked or whether the pushshift api is up to date. These comments are stored
in text files for each respective date.

Logan Kraver
Started: 10/25/2021
Last Edited: 11/8/2021
"""


from selenium import webdriver
import requests
from datetime import date,timedelta
import os
from time import sleep
import praw


#PRAW instance does not contain actual information for reddit script to protect privacy
r = praw.Reddit(
    client_id='client_id',
    client_secret='client_secret',
    user_agent='windows:getcomments:1.0 (by u/username)',
    username='username',
    password='password'
)


#date functions
def getdate(s):
    """
    Function to get the date that is s days from today

    Parameter s is an int representing the number of days since today's date

    Returns a datetime object based on the date that is s days from today
    """
    return date.today() - timedelta(days=s)


def convertdatetime(d):
    """
    Function to convert a datetime object into a string

    Parameter d is a datetime object
    Parameter s is an int representing the number of days since today's date

    Returns a string of a date in form (month/day/year)
    """
    return d.strftime("%m/%d/%Y")


def convertstringdate(s):
    """
    Function to convert a date with words into numbers

    Parameter s is a string, with form Month Day, Year

    Returns a string with numerical date with similar form (month/day/year)
    """
    firstpos = s.find(' ')
    secondpos = s.find(' ', firstpos + 1)
    month = s[0: firstpos]
    months = ['January','February','March','April','May','June','July','August'
    ,'September','October','November','December']
    for m in range(len(months)):
        if month == months[m]:
            month = str(m + 1)

    day = s[firstpos + 1: secondpos - 1]
    year = s[secondpos +1:]
    date = month + '/' + day + '/' + year
    return date


def convertlinkdate(s):
    """
    Function to convert a string date to date form found in link

    Parameter s is a string, with form Month Day, Year

    Returns a string with the date form found in link (month-day-year)
    """
    firstpos = s.find(' ')
    secondpos = s.find(' ', firstpos + 1)
    month = s[0: firstpos].lower()
    day = s[firstpos + 1: secondpos - 1]
    year = s[secondpos +1:]
    date = month + '_' + day + '_' + year
    return date

def convertintmonth(s):
    """
    Function to convert an integer into its corresponding string month

    Parameter s is an int less than or equal to 12, representing a month

    Returns a string that is the name of the month
    """
    months = ['January','February','March','April','May','June','July','August'
    ,'September','October','November','December']
    for x in range(12):
        if s == x+1:
            return months[x]

def convertfilefriendlydate(s):
    """
    Function to convert a numerical date (month/day/year) to a file friendly
    form (month-day-year)

    Parameter s is a string with form (month/day/year; all of which are ints)

    Returns a string of a date with form (month-day-year; all of which are ints)
    """
    return s.replace('/','-')

def isweekend(d):
    """
    Function to determine if the date is in the weekend

    Parameter d is a datetime object

    Returns true, if the date is in the weekend, returns false, if the date is a
    weekday
    """
    if d.weekday() < 5:
        return False
    else:
        return True

#web functions
def launchchrome(url):
    """
    Function to load chrome with a specific url.

    Parameter url is a string that is a valid url

    Returns a Chrome webdriver object
    """
    driver = webdriver.Chrome(executable_path=r'c:\chromedriver.exe')
    driver.get(url)
    return driver


def findelements(driver,classname):
    """
    Function to find all elements of a specific class from the chrome webdriver

    Parameter driver is a Chrome webdriver object
    Parameter classname is a string that has a valid class name

    Returns list of web objects of the elements found
    """
    return driver.find_elements_by_xpath('//*[@class="' + classname + '"]')


def identifyposttype(id):
    """
    Function to the post type with an integer id

    Parameter is an int representing an id number
    id 0 = Daily Discussion thread
    id 1 = What are your moves tomorrow post

    Returns a list that includes post information for each respective id
    """
    posttypes = [
    ['Daily Discussion Thread for ','daily_discussion_thread','Daily_Discussion_Thread_Comments_'],
    ['What Are Your Moves Tomorrow, ','what_are_your_moves','What_Are_Your_Moves_Tomorrow_Comments_']
    ]
    return posttypes[id]


def searchpostlinks(url,posttype):
    """
    Function to find a dictionary of links based on most recent posts to r/WSB
    using the flair Daily Discussion and the desired posttype

    Parameter url is a string representing a valid url
    Parameter posttype is an integer representing the post id type

    Returns a dictionary with dates for keys that match to the corresponding
    post link for that day
    """
    driver = launchchrome(url)

    postlist = findelements(driver,'_eYtD2XCVieq6emjKBH3m')
    urllist = findelements(driver,'SQnoC3ObvgnGjWt90zD9Z _2INHSNB8V5eaWp4P0rY_mE')

    posttitle = identifyposttype(posttype)[0]
    urltitle = identifyposttype(posttype)[1]

    links = {}
    for post in postlist:
        if post.text.startswith(posttitle):
            postdate = post.text[len(posttitle):]
            linkdate = convertlinkdate(postdate)
            numericaldate = convertstringdate(postdate)
            for url in urllist:
                posturl = url.get_attribute('href')
                if posturl.find(linkdate) != -1:
                    if posturl.find(urltitle) != -1:
                        links[numericaldate] = posturl
                        break
    closedriver(driver)
    return links


def findpostgivendate(date):
    """
    Function to find the url of a post given the date

    Parameter date is a datetime object corresponding to the desired date

    Returns a string that is a valid url
    """
    month = convertintmonth(date.month)

    if date.day < 10:
        day = '0' + str(date.day)
    else:
        day = str(date.day)

    year = str(date.year)

    url = ("https://www.reddit.com/r/wallstreetbets/search/?q=flair%3A%22Daily%20Discussion%22%20AND%20title%3A%22"
    + month + "%20" + day + "%2C%20" + year + "%22&restrict_sr=1&sr_nsfw=")
    return url


def closedriver(driver):
    """
    Function to close chrome webdriver

    Parameter driver is a Chrome webdriver object
    """
    driver.close()


#Comment Functions
def findthreadid(s):
    """
    Function to find thread id for reddit post given the link

    Parameter s is a string, which is a link to a reddit post

    Returns as string that is the thread id of the post
    """
    pos1 = s.rfind('/',0,-1)
    pos2 = s.rfind('/', 0, pos1 - 1)
    threadid = s[pos2+1:pos1]
    return threadid

def isthreadlocked(url):
    """
    Function to determine if a reddit post is locked

    Parameter url is the string that represents the url for a post

    Returns True if the post is locked, returns False if the post is unlocked
    """
    threadid = findthreadid(url)
    submission = r.submission(id=threadid)
    return submission.locked


def getcommentspushshift(date, links):
    """
    Function to return a list with all comments as strings from a r/WSB post
    given a dictionary of dates and links using the pushshift API

    Parameter date is a string reflecting the date desired
    Parameter links is a dictionary with links corresponding to the date

    Returns a list of strings with each comment
    """
    threadid = findthreadid(links[date])
    html = requests.get(f'https://api.pushshift.io/reddit/comment/search/?link_id={threadid}&limit=20000&fields=body')
    raw_comment_json = html.json()
    raw_comment_list = raw_comment_json['data']
    comments = []
    for body in raw_comment_list:
        comments.append(body['body'])
    return comments


def getcommentslockedpraw(url):
    """
    Function to return a list with all comments as string from a locked r/WSB
    post given the url for a post using the PRAW library

    Parameter url is a string that represents a valid url for a reddit post

    Returns a list of strings that represent comments
    """
    commentlist = []
    id = findthreadid(url)
    submission = r.submission(id=id)
    comments = submission.comments
    getmorecomments(comments)
    return commentlist


def getmorecomments(comments):
    """
    Function to get all comments from a commentforest object by expanding all
    morecomments objects.

    This function uses recursion to get all objects from a list of comment and
    morecomments objects and adds the comments to the list, while expanding the
    morecomments objects into separate commentlists to be added to the original
    commentlist.

    Parameter comments is a list of comment and morecomments objects from a
    commentforest

    Returns a list with exclusively comment objects
    """
    for comment in comments:
        if type(comment) != praw.models.MoreComments:
            commentlist.append(comment.body)
        else:
            print(commentlist)
            morecomments = comment.comments()
            getmorecomments(morecomments)


def deleteremovedcomments(comments):
    """
    Function to remove all '[removed]' comments from a list of reddit comments

    Parameter comments is a list of strings of reddit comments

    Returns a new list without the '[removed]' comments
    """
    itemstoremove = []
    for x in range(len(comments)):
        if comments[x] == '[removed]':
            itemstoremove.append(x)
    itemstoremove.reverse()
    for y in itemstoremove:
        comments.pop(y)
    return comments


def getpast30dayslinks(postdict,PATH,posttype):
    """
    Function to add links of posts in the last 30 days that haven't been scraped

    Parameter postdict is a dictionary with date keys that correspond to post
    links
    Parameter PATH is a string represeting a valid file PATH
    Parameter posttype is an int represeting a valid id for types of posts

    Returns a dictionary with date keys and corresponding link values (strings)
    for all dates in the last 30 days that have not been scraped
    """
    for d in range(30):
        date = getdate(29-d)
        if not convertdatetime(date) in postdict.keys():
            if not isweekend(date):
                file_name = identifyposttype(posttype)[2] + convertfilefriendlydate(convertdatetime(date))
                if not checkfilelocation(PATH,file_name):
                    searchurl = findpostgivendate(date)
                    datelink = searchpostlinks(searchurl,posttype)
                    postdict.update(datelink)
    return postdict


def getallcommentslocked(PATH,linklist,posttype):
    """
    Function to get all comments of all locked posts in a dict of urls and puts
    the comments into a txt file

    Parameter PATH is a string represeting a valid file PATH
    Parameter linklist is a dict with date keys and valid corresponding post
    links
    Parameter posttype is an int that represents a valid post type id
    """
    for date in linklist:
        comments = []
        if not checkfilelocation(PATH,identifyposttype(posttype)[2] + convertfilefriendlydate(date)):
            #check if file already exists for posttype + date
            if isthreadlocked(linklist[date]):
                #check if thread is locked
                comments = getcommentspushshift(date,linklist)
                #use pushshift API to get comments
                if comments == []:
                    #if pushshift API fails to get comments use PRAW library
                    getcommentslockedpraw(linklist[date])
                    comments = deleteremovedcomments(commentlist)
                    createcommentfile(posttype,date,comments)
                else:
                    #if pushshift API succeeds put comments into file
                    comments = deleteremovedcomments(comments)
                    createcommentfile(posttype,date,comments)


def getallcommentsunlocked(linklist,posttype):
    """
    Function to get all comments of an unlocked post in a dict of urls and puts
    the comments into a txt file using Selenium to continually reload the post

    Parameter linklist is a dict with date keys and valid corresponding post
    links
    Parameter posttype is an int that represents a valid post type id
    """
    commentlist = []
    postdate = ''

    for date in linklist:
        #check if any posts are unlocked
        if not isthreadlocked(linklist[date]):
            postdate = date
            break

    #if no posts are unlocked end the function
    if postdate == '':
        return 0

    #while the loop is unlocked run the scraping algorithm
    while not isthreadlocked(linklist[postdate]):
        #launch the post url
        driver = launchchrome(linklist[date])

        #use Selenium to find all comment webelements
        commentelements = driver.find_elements_by_xpath('//*[@class="_1qeIAgB0cPwnLhDF9XSiJM"]')

        for comment in commentelements:
            if comment.text not in commentlist:
                #if comment text is not in commentlist add it to the list
                commentlist.append(comment.text)

        closedriver(driver)

        #print contents of the list
        print("# of comments: " + str(len(commentlist)))
        print(commentlist)
        sleep(10)

    #create a file with all of the comments when the post locks
    createcommentfile(posttype,postdate,commentlist)


#File Functions
def checkfilelocation(PATH, string):
    """
    Function to determine if a file is in the folder PATH

    Parameter PATH is a string that is a valid directory path
    Parameter string is a string that represents the name of the file

    Returns True if the file is present, false if the file is not present
    """
    files = os.listdir(PATH)
    for file in files:
        if file.find(string) != -1:
            return True
    return False


def createcommentfile(posttype,date,comments):
    """
    Function to create a txt file given comment data and posttype + date

    Parameter posttype is an int representing a valid post id
    Parameter date is a string with the date (format: M/D/Y)
    Parameter comments is a list of strings that represent a comment
    """
    filename = identifyposttype(posttype)[2] + convertfilefriendlydate(date) + '.txt'
    with open(filename,'w',encoding='utf-8') as f:
        for comment in comments:
            f.write(comment)
            f.write('\n')


if __name__ == "__main__":
    #variables
    url = 'https://www.reddit.com/r/wallstreetbets/?f=flair_name%3A%22Daily%20Discussion%22'
    PATH = r'file\path\to\input\comment\data'
    commentlist = []

    #dailydiscussionthread posts
    dailydiscussionlinks = searchpostlinks(url,0)
    dailydiscussionlinks = getpast30dayslinks(dailydiscussionlinks,PATH,0)
    getallcommentslocked(PATH,dailydiscussionlinks,0)

    #movestomorrowthread posts
    movestomorrowlinks = searchpostlinks(url,1)
    movestomorrowlinks = getpast30dayslinks(movestomorrowlinks,PATH,1)
    getallcommentslocked(PATH,movestomorrowlinks,1)
