import tweepy
import json
import textblob
import config
# override tweepy.StreamListener to add logic to on_status


class MyStreamListener(tweepy.StreamListener):
    count = 0

    def on_status(self, status):
        print(status.text)

    def on_data(self, data):
        # Limits the count to 10 for now
        if MyStreamListener.count > 10:
            print("Exiting...")
            # Returning false will exit the stream loop
            return False

        dict_data = json.loads(data)

        # pass tweet into TextBlob
        tweet = textblob.TextBlob(dict_data["text"])

        # output sentiment polarity
        print(tweet.sentiment.polarity)

        # determine if sentiment is positive, negative, or neutral
        if tweet.sentiment.polarity < 0:
            sentiment = "negative"
        elif tweet.sentiment.polarity == 0:
            sentiment = "neutral"
        else:
            sentiment = "positive"

        print("User: {}".format(dict_data["user"]["screen_name"]))
        print("Tweet: {}".format(dict_data["text"]))
        print("Count: {}".format(MyStreamListener.count))
        print("Sentiment: {}".format(sentiment))
        print("")

        MyStreamListener.count += 1

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


def main():
    # set twitter keys/tokens
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    # class
    myStreamListener = MyStreamListener()
    # set stream details
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)

    try:
        myStream.filter(track=["home depot", "homedepot"], async=False)

    except Exception as error:
        print("Error: {}".format(error.__doc__))
        print("Error Message: ".format(error.message))


# runs at start
if __name__ == "__main__":
    main()
