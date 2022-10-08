# ニュースサイトをクローリングして、時系列順にAIのキーワードを抽出する。
# 抽出したキーワードからWordCloudを作成する。
# 作成したWordCloudをTwitterに投稿する。

import os
import sys
import time
import datetime
import requests
import json
import re
import MeCab
import numpy as np
from PIL import Image
from wordcloud import WordCloud
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1Session

# Twitter APIのキーを設定
#CK = os.environ['CK']
#CS = os.environ['CS']
#AT = os.environ['AT']
#AS = os.environ['AS']

#Twitter APIを使用するためのConsumerキー、アクセストークン設定
CK = ''
CS = ''
AT = ''
AS = ''


# ニュースサイトのURLを設定
#URL = 'https://www3.nhk.or.jp/news/easy/k10011852901000/k10011852901000.html'
#URL = 'https://www.nikkei.com/technology/ai/' # 日経新聞社
#URL = 'https://ledge.ai/theme/news/' # ledge.ai
URL = 'https://ainow.ai/' # AI Now

# ニュースサイトをクローリングして、本文を取得する
def get_news_text(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    #news_text = soup.find('div', class_='text').text
    #news_texts = soup.find('div', class_='m-miM09') # 日経新聞社
    #news_texts = soup.find_all('h2', class_='grid-item__title') # ledge.ai
    news_texts = soup.find_all('div', class_='article_title') # AI Now
    
    # 配列から抽出したテキストを結合
    news_text = ''
    for news in news_texts:
        news_text += news.text
        
    
    return news_text

# 本文からAIのキーワードを抽出する
def get_ai_keywords(text):
    # 形態素解析
    tagger = MeCab.Tagger('-Ochasen')
    tagger.parse('')
    node = tagger.parseToNode(text)
    keywords = []
    while node:
        # 品詞が名詞、動詞、形容詞の場合にキーワードとして抽出
        if node.feature.split(',')[0] in ['名詞', '動詞', '形容詞']:
            keywords.append(node.surface)
        node = node.next
    # キーワードをカウント
    keywords_count = {}
    for keyword in keywords:
        if keyword in keywords_count:
            keywords_count[keyword] += 1
        else:
            keywords_count[keyword] = 1
    # キーワードを降順に並び替え
    keywords_count = sorted(keywords_count.items(), key=lambda x:x[1], reverse=True)

    # デバッグ用にキーワードを表示
    #for keyword in keywords_count:
    #    print(keyword)

    return keywords_count

# 抽出したキーワードからWordCloudを作成する
def create_wordcloud(keywords_count):
    # フォントを設定
    font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
    # マスク画像を設定
    mask = np.array(Image.open('mask.png'))
    # WordCloudを作成
    #wordcloud = WordCloud(background_color='white', font_path=font_path, mask=mask)
    wordcloud = WordCloud(background_color="black",font_path=font_path, width=800,height=600)

    wordcloud.generate_from_frequencies(dict(keywords_count))
    # WordCloudを保存
    wordcloud.to_file('wordcloud.png')

"""
# WordCloudをTwitterに投稿する
def post_wordcloud():
    # 画像を読み込む
    files = {'media[]': open('wordcloud.png', 'rb')}
    # ツイート本文を設定
    text = 'AIのキーワードを抽出したWordCloudです。'
    # Twitterに投稿
    twitter = OAuth1Session(CK, CS, AT, AS)
    url = 'https://upload.twitter.com/1.1/media/upload.json'
    req_media = twitter.post(url, files=files)
    if req_media.status_code != 200:
        print('画像のアップロードに失敗しました。')
        sys.exit()
    media_id = json.loads(req_media.text)['media_id']
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    params = {'status': text, 'media_ids': media_id}
    req_media = twitter.post(url, params=params)
    if req_media.status_code != 200:
        print('ツイートに失敗しました。')
        sys.exit()
    print('ツイートしました。')
"""

def main():
    # ニュースサイトをクローリングして、本文を取得する
    text = get_news_text(URL)
    # 本文からAIのキーワードを抽出する
    keywords_count = get_ai_keywords(text)
    # 抽出したキーワードからWordCloudを作成する
    create_wordcloud(keywords_count)
    # WordCloudをTwitterに投稿する
    post_wordcloud()

if __name__ == '__main__':
    main()




