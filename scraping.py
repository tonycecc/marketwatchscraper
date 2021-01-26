# Author  : Anthony Cecc
# Version : 0.2

from bs4 import BeautifulSoup, ResultSet
import requests
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd


analyzer = SentimentIntensityAnalyzer()
print('Getting news')
mw_html_text = requests.get('https://www.marketwatch.com/latest-news?mod=top_nav').text  # gets website
mw_website = BeautifulSoup(mw_html_text, 'lxml')  # uses BeautifulSoup to read the html
news_container = mw_website.find('div', class_='collection__elements j-scrollElement')  # searches the html that BS read into py
stories_link = news_container.find_all('a', class_='link')
head_lines = news_container.find_all('h3', class_='article__headline')
# Make arrays with links and respective headlines
head_line_hrefs = []
for story in stories_link:
    head_line_hrefs.append(story.get('href'))
# get content from story using hrefs gathered prev and puts it into a list for later
article_content = []
a = ''
vs_compound = ''
all_content = []
senitment_of_article = []
ticker_list = []
container = []
print('Analyzing...')
print('This can take a while.')
for i in head_line_hrefs:
    article_html = requests.get(i).text
    article = BeautifulSoup(article_html, 'lxml')
    try:
        article_wrapper = article.find('div', class_='column column--full article__content')
        article_content = article_wrapper.find_all('p')
        article_title = article.find('h1', class_ = 'article__headline').text
        article_title = article_title.encode('ascii', 'ignore').decode()
        article_title = re.sub("https*\S+", " ", article_title)
        article_title = re.sub('\s{2,}', " ", article_title)
    except:
        None

    try:
        find_tick = article.find('div', class_='element element--list referenced-tickers')
        list_tick = find_tick.find('ul', class_='list list--tickers')
        tickers = list_tick.find('span', class_='symbol').text
        assert isinstance(tickers, object)
        ticker_list.append(tickers)
    except:
        tickers = "None"
        # print('No ticker symbol(s) mentioned')
        ticker_list.append('None')
    for element in article_content :  # takes the text <p> and puts them into a string
        assert isinstance(element.text, object)
        a += element.text
        # clean text
        a = re.sub("https*\S+", " ", a)  # remove links
        a = re.sub('\s{2,}', " ", a)  # fix overspace
        senitment_of_article.append(analyzer.polarity_scores(a)) # use vader for each one and print the whole shabang
        vs_compound = analyzer.polarity_scores(a)['compound']
        # append
        all_content.append(a)
    if tickers == 'None':
        None
    else:
        if vs_compound >= 0.5:
            container.append(['$' + tickers, 'Positive', vs_compound, article_title])
        else:
            container.append(['$' + tickers, 'Negative',vs_compound, article_title])

    a = '' # Needs to be reset to an empty string or else ever index of the list will contain the previous article
    holder = ''
print('Done')

#print(ticker_list)
#print(container)
#print(senitment_of_article)

# write data
df = pd.DataFrame(container, columns= ['Ticker', 'Sentiment', 'Score', 'Headline'])
print(df)



