# -*- coding: utf-8 -*-
"""SMA_YOUTUBE.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Xwzm9w7swHypjhqwJOPKlphOqU2ngZsk
"""

# # pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
# !pip install --upgrade google-api-python-client

# !pip install nltk
# !python -m nltk.downloader vader_lexicon

import os
import csv
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from nltk.sentiment import SentimentIntensityAnalyzer
import re

# !pip install vaderSentiment
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

# from google.colab import drive
# drive.mount('/content/drive')

# %cd '/content/drive/My Drive/'

# with open('devEnv.txt', 'r') as f:
#     api_key = f.read().strip()

# print(api_key)
# %cd ../..
# # from access_key import access_key

from googleapiclient.discovery import build
import pandas as pd

# %cd ../..

api_key = 'XXX-XXX'
video_ids = []
with open('vdoLinks.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # skip header row
    for row in reader:
        video_ids.append(row[0])

def video_comments(video_id):
    # empty list for storing reply and sentiment scores
    replies = []
    sentiment_scores = []

    # creating youtube resource object
    youtube = build('youtube', 'v3', developerKey=api_key)

    # retrieve youtube video results
    video_response = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id,
        maxResults=100  # retrieve only the first 100 comment threads
    ).execute()

    # create empty list to store sentiments
    sentiments = []

    # iterate video response
    while video_response:
        # extracting required info from each result object
        for item in video_response['items']:
            # extracting comments
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']

            # apply sentiment analysis on comment using VADER
            sentiment = sia.polarity_scores(comment)

            # append sentiment to list
            sentiments.append(sentiment)

            # #get sentiment score of comment
            # sentiment_score = get_sentiment_score(comment)

            # #append sentiment score to list
            # sentiment_scores.append(sentiment_score)
            # print(sentiment_scores)

            # if reply is there
            replycount = item['snippet']['totalReplyCount']
            if replycount > 0:
                # iterate through all reply
                for reply in item['replies']['comments']:
                    # Extract reply
                    reply = reply['snippet']['textDisplay']

                    # apply sentiment analysis on reply using VADER
                    reply_sentiment = sia.polarity_scores(reply)

                    # append sentiment to list
                    sentiments.append(reply_sentiment)

                    #sentimet score
                    scores = sia.polarity_scores(reply)

                    # print comment with list of reply
                    # print(comment, replies, scores, end='\n\n')


        # stop iteration after retrieving first 100 comment threads
        if len(video_response['items']) >= 100:
            break

        # retrieve next page of comment threads
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                maxResults=100,
                pageToken=video_response['nextPageToken']
            ).execute()
        else:
            break

    # calculate overall sentiment score for the video
    sentiment_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
    for sentiment in sentiments:
        if sentiment['compound'] >= 0.05:
            sentiment_scores['positive'] += 1
        elif sentiment['compound'] <= -0.05:
            sentiment_scores['negative'] += 1
        else:
            sentiment_scores['neutral'] += 1
    return sentiment_scores

# Retrieve video statistics by ID
def video_stats(video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_response = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    ).execute()

    # extract video statistics
    for item in video_response['items']:
        views = int(item['statistics']['viewCount'])
        likes = int(item['statistics']['likeCount'])
        # dislikes = int(item['statistics']['dislikeCount'])
        duration = item['contentDetails']['duration']
    return views, likes, duration

# Get top-10 videos by total views
def top_videos(df):
    df = df.sort_values('views', ascending=False)
    top_10 = df.head(10)
    return top_10

# Get bottom-10 videos by total views
def bottom_videos(df):
    df = df.sort_values('views', ascending=True)
    bottom_10 = df.head(10)
    return bottom_10

# Get most liked video
def most_liked_video(df):
    df = df.sort_values('likes', ascending=False)
    most_liked = df.head(1)
    return most_liked

# Get least liked video
def least_liked_video(df):
    df = df.sort_values('likes', ascending=True)
    least_liked = df.head(1)
    return least_liked

# Get video with the highest duration
def highest_duration_video(df):
    df['duration_seconds'] = df['duration'].apply(lambda x: pd.to_timedelta(x).total_seconds())
    df = df.sort_values('duration_seconds', ascending=False)
    highest_duration = df.head(1)
    return highest_duration
    # return get_duration_in_seconds(highest_duration)

if __name__ == '__main__':
    # video_ids = ['VwIWfvW3SD8','Sc1OI1i-Kgs','mdvJJMAjZlc','GUV6BJ5MGqE','pzcBs8XrvyQ','Arfujgk7R3Y','v73QW4UbeLg','zXLgYBSdv74','PSxYv2F_xN8', 'sDEZSFNQmP0', '3bZoB8PiXas']

    # create an empty list to store the extracted video data
    data = []
    video_ids= video_ids[:30]
    # sentiment_scores = []
    # iterate through video ids to extract video statistics and comments
    for video_id in video_ids:
        try:
          views, likes, duration = video_stats(video_id)
          comments = video_comments(video_id)
          print("Comments is::::")
          print(comments)
          # comments, video_sentiment_scores = video_comments(video_id)
          # sentiment_scores.append(video_sentiment_scores)
          data.append({
              'video_id': video_id,
              'views': views,
              'likes': likes,
              # 'dislikes': dislikes,
              'duration': duration,
              'comments': comments,
              # 'sentiment_score': sentiment_scores
          })
        except Exception as e:
          print(f"An error occurred while processing video ID {video_id}: {e}")
          continue

    # create a dataframe from the extracted video data
    df = pd.DataFrame(data)

    # get top-10 videos by total views
    top_10 = top_videos(df)
    print("\nTop 10 videos by total views:\n", top_10)

    # get bottom-10 videos by total views
    bottom_10 = bottom_videos(df)
    print("\nBottom 10 videos by total views:\n", bottom_10)

    # get most liked video
    most_liked = most_liked_video(df)
    print("\nMost liked video:\n", most_liked)

    # get least liked video
    least_liked = least_liked_video(df)
    print("\nLeast liked video:\n", least_liked)

    # get video with the highest duration
    highest_duration = highest_duration_video(df)
    print("\nVideo with highest duration:\n", highest_duration)

