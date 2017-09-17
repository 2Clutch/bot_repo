import tweepy
import json
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import time
import config

from oauth2client.client import GoogleCredentials
credentials = GoogleCredentials.get_application_default()


class MyStreamListener(tweepy.StreamListener):
    count = 0

    def __init__(self):
        self.dict_error = {
            "count500Codes": [0, [500, 502, 503, 504]],
            "count420Codes": [60, [420, 429]],
            "count400Codes": [5, [400, 401, 403, 404, 406, 410, 422]]
        }

    def on_status(self, status):
        print(status.text)

    def on_data(self, data):
        MyStreamListener.__init__(self)
        dict_data = json.loads(data)

        # filter out RTs
        if "RT @" not in dict_data["text"] and dict_data["user"]["screen_name"] != tweepy.API(auth).me()._json["screen_name"]:

            # def google sentiment analytics
            def sentiment_text(text):
                # Detects sentiment in the text.
                client = language.LanguageServiceClient()
                if isinstance(text, six.binary_type):
                    text = text.decode('utf-8')

                # Instantiates a plain text document.
                document = types.Document(
                    content=text,
                    type=enums.Document.Type.PLAIN_TEXT)

                # Detects sentiment in the document.
                sentiment = client.analyze_sentiment(document).document_sentiment
                return sentiment.score

            # pass tweet through google sentiment analytics
            sentiment = sentiment_text(dict_data["text"])

            # sentiment logic
            sentiment_type = "neutral"
            middleStr = "glad you enjoyed yourself at @HomeDepot"
            if sentiment < 0:
                # negative
                sentiment_type = "negative"
                middleStr = "sorry your visit didn't go as planned"
            elif sentiment != 0:
                sentiment_type = "positive"

            # reply to tweet
            screenName = dict_data["user"]["screen_name"]
            charLeft = 60 - len(middleStr)
            if len(screenName) > charLeft:
                screenName = screenName[:charLeft - 1]
            string = "Hello @{0}, we're {1}. Let us know about your recent experience: https://goo.gl/H5khzW".format(screenName, middleStr)
            nullArg = tweepy.API(auth).update_status(status=string, in_reply_to_status_id=dict_data["id"])

            print("User: {}".format(dict_data["user"]["screen_name"]))
            print("Tweet: {}".format(dict_data["text"]))
            print("Count: {}".format(MyStreamListener.count))
            print("Sentiment: {}".format(sentiment_type))
            print("Score: {}".format(sentiment))
            print("")

            MyStreamListener.count += 1

    # error handling
    def on_error(self, status_code):
        # check for error code
        timeDelay = 0
        for var in self.dict_error.keys():
            if status_code in self.dict_error["count500Codes"][1] and (.25 * self.dict_error["count500Codes"][0] < 16):
                self.dict_error["count500Codes"][0] += 1
                timeDelay = self.dict_error["count500Codes"][0] * .25
            elif status_code in self.dict_error["count420Codes"][1] or (status_code in self.dict_error["count400Codes"][1] and ((self.dict_error["count400Codes"][0] * 2) < 320)):
                self.dict_error[var][0] *= 2
                timeDelay = self.dict_error[var][0]
            else:
                return None
            # if time delay is known, delay so as to not run_limit.
            if timeDelay:
                print("Error Code: {}".format(status_code))
                print("Time: {}".format(timeDelay))
                return time.sleep(timeDelay + (timeDelay * .05))


def main():
    # set twitter keys/tokens
    global auth
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_token_secret)

    # class
    myStreamListener = MyStreamListener()

    # set stream details
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)

    print(tweepy.API(auth).rate_limit_status()['resources']['users']['/users/lookup'])
    try:
        myStream.filter(track=["homedepot", "home depot"], async=True, languages=["en"])
    except tweepy.TweepError:
        myStream.on_error(tweepy.TweepError.message[0]['code'])


# runs at start
if __name__ == "__main__":
    main()
