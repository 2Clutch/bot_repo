import tweepy
import json
import textblob
import config
# override tweepy.StreamListener to add logic to on_status


class MyStreamListener(tweepy.StreamListener):
    count = 0
    # limit = 10

    def on_status(self, status):
        print(status.text)

    def on_data(self, data):
        # Limits the count to 10 for now
        # if MyStreamListener.count > MyStreamListener.limit:
        #     print("Exiting...")
        #     # Returning false will exit the stream loop
        #     return False

        dict_data = json.loads(data)

        # filter out RTs
        if "RT @" not in dict_data["text"]:
            # pass tweet into TextBlob
            tweet = textblob.TextBlob(dict_data["text"])

            sentiment = ""
            # determine if sentiment is positive, negative, or neutral
            if tweet.sentiment.polarity < 0:
                # negative
                sentiment = "negative"
                string = "Hello @{}, we're sorry your visit didn't go as planned. Please follow this link, https://goo.gl/H5khzW, and let us know about your recent experience.".format(dict_data["user"]["screen_name"])
                # a = tweepy.API(auth).send_direct_message(user=dict_data["user"]["screen_name"], text=string)
                a = tweepy.API(auth).update_status(status=string, in_reply_to_status_id=dict_data["id"])

            elif tweet.sentiment.polarity > 0:
                # positive
                sentiment = "positive"
                string = "Hello @{}, we're glad you enjoyed yourself at @HomeDepot. Please follow this link, https://goo.gl/H5khzW, and let us know about your recent experience.".format(dict_data["user"]["screen_name"])
                # a = tweepy.API(auth).send_direct_message(user=dict_data["user"]["screen_name"], text=string)
                a = tweepy.API(auth).update_status(status=string, in_reply_to_status_id=dict_data["id"])

            print("User: {}".format(dict_data["user"]["screen_name"]))
            print("Tweet: {}".format(dict_data["text"]))
            print("Count: {}".format(MyStreamListener.count))
            print("Sentiment: {}".format(sentiment))
            print("Score: {}".format(tweet.sentiment.polarity))
            print("")

            MyStreamListener.count += 1

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


def main():
    # set twitter keys/tokens
    global auth
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    # class
    myStreamListener = MyStreamListener()
    # set stream details
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
    try:
        myStream.filter(track=["homedepot", "homedepot"], async=True, languages=["en"])

    except Exception as error:
        print("Error: {}".format(error.__doc__))
        print("Error Message: ".format(error.message))


# runs at start
if __name__ == "__main__":
    main()
