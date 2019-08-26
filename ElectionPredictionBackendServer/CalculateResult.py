from datetime import date
from socket import *
from threading import *
import os
from textblob import TextBlob
import tweepy
import pandas
from tkinter import *


def calculatetweetsdemo(input_obtained, input_month):
    tweet_dict = {}
    name_not_entered = False
    print("called")
    if input_obtained == '':
        name_not_entered = True
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    consumer_key = 'pBQ6uagJoN3eksDl55bzaSepf'
    consumer_secret = 'NEA8UFjkf7325FhKWba02kgQJWSKmQLhCrXzWYyyyaQEXICNic'
    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    tweet_list = []
    final_month = 0
    final_year = 2019

    def calculate_sentiment(tweet):
        test_tweet = TextBlob(cleantweet(tweet))
        if test_tweet.sentiment.polarity > 0:
            return 'positive'
        elif test_tweet.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def cleantweet(tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w+:\ / \ / \S+)", " ", tweet).split())

    def gettweets(final_month, final_year):
        nonlocal months_not_entered
        nonlocal error
        x = re.findall("\D", str(input_month))
        if x:
            error = True
            return
        if input_month == "":
            months_not_entered = True
            return

        entered_month = input_month
        nonlocal notweets
        print(entered_month)
        if entered_month == 0:
            notweets = True
        if entered_month > 24:
            error = True
            print(error)
            return
        todays_date = date.today()
        print(todays_date)
        todays_date = str(todays_date).split("-")
        current_month = int(todays_date[1])

        if entered_month < current_month:
            final_month = current_month - entered_month
        elif 4 - entered_month <= 0:
            quotient = int(entered_month / current_month)
            final_year = final_year - quotient
            entered_month = entered_month % current_month
            final_month = 12 - entered_month
        print(str(final_year) + " " + str(final_month))
        todays_day = todays_date[2]
        print(todays_day)
        nonlocal positive_count, neutral_count, negative_count
        repeated_count = 0
        tweet_counter = 0
        rootDir = os.path.dirname(os.path.abspath(__file__))
        fh = open(rootDir + "/" + input_obtained + str(months) + "tweets" + ".txt", "w", encoding="utf-8")
        for tweet in tweepy.Cursor(api.search, q="#" + input_obtained, lang="en", count = 200,
                                   since=str(final_year) + "-" + str(final_month) + "-"+todays_day).items():
            print("tweet " + str(tweet_counter) + " processed")
            sentiment_type = calculate_sentiment(tweet.text)
            tweets_no_repeat = {'text': tweet.text, 'sentiment': sentiment_type}
            if tweet.retweet_count > 0:
                if tweets_no_repeat not in tweet_list:
                    tweet_list.append(tweets_no_repeat)
                    fh.write(tweet.text.replace("\n","")+"--++=="+sentiment_type+"\n")
                    if sentiment_type == 'positive':
                        positive_count = positive_count + 1
                    elif sentiment_type == 'negative':
                        negative_count = negative_count + 1
                    else:
                        neutral_count = neutral_count + 1
                    print(tweet.text)
                else:
                    if sentiment_type == 'positive':
                        positive_count = positive_count + 1
                    elif sentiment_type == 'negative':
                        negative_count = negative_count + 1
                    else:
                        neutral_count = neutral_count + 1
                    repeated_count += 1

            elif tweet.retweet_count == 0:
                tweet_list.append(tweets_no_repeat)
                fh.write(tweet.text.replace("\n", "") + "--++==" + sentiment_type+"\n")
                if sentiment_type == 'positive':
                    positive_count = positive_count + 1
                elif sentiment_type == 'negative':
                    negative_count = negative_count + 1
                else:
                    neutral_count = neutral_count + 1
                print(tweet.text)
            tweet_counter += 1
        fh.close()
        total_tweets = positive_count + neutral_count + negative_count
        if total_tweets == 0:
            notweets = True
        print(str(positive_count) + " " + str(negative_count) + " " + str(neutral_count))
        print(" " + str(total_tweets))
        print("repeated ", repeated_count)
        print(len(tweet_list))
        nonlocal tweet_dict
        tweet_dict = {'Tweets': tweet_list}
        df = pandas.DataFrame.from_dict(tweet_dict)
        rootDir = os.path.dirname(os.path.abspath(__file__))
        df.to_csv(rootDir + "/" + input_obtained + str(months) + "tweets" + ".csv", index=False)
    error = False
    notweets = False
    months_not_entered = False
    gettweets(final_month, final_year)
    print(error)
    if error:
        return "invalid input"
    if notweets:
        return "no tweets"
    if months_not_entered and name_not_entered:
        return "name and months empty"
    if months_not_entered:
        return "months empty"
    if name_not_entered:
        return "name empty"
    if not error and not notweets:
        total_count = positive_count + neutral_count + negative_count
        if total_count == 0:
            return "total count zero"

        return str(positive_count)+","+str(negative_count)+","+str(neutral_count)


host_name = ""
host_port = 1234
host_addr = (host_name, host_port)
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(host_addr)
server_socket.listen(10)


class ProcessTweetsThread(Thread):
    def __init__(self, input_obtained, months, client_socket):
        Thread.__init__(self)
        self.input_obtained = input_obtained
        self.months = months
        self.client_socket = client_socket

    def run(self):
        print("Thread started")
        result = ""
        rootDir = os.path.dirname(os.path.abspath(__file__))
        path = rootDir + "/" + input_obtained + str(months) + ".txt"
        exists = os.path.isfile(path)
        if exists:
            fh = open(path, "r")
            result = fh.read()
            fh.close()
        else:
            result = calculatetweetsdemo(self.input_obtained, int(self.months))
            fh = open(path, "w")
            fh.write(result)
            fh.close()

        print("Thread processing complete. Waiting to send result.")
        client_socket.send(result.encode())
        print("Thread sent result successfully.")


while True:
    client_socket, client_addr = server_socket.accept()
    input_obtained = client_socket.recv(1024)
    input_obtained = input_obtained.decode()
    input_list = input_obtained.split(",")
    input_obtained = input_list[0]
    months = input_list[1]
    process_thread = ProcessTweetsThread(input_obtained, months, client_socket)
    process_thread.start()


server_socket.close()
