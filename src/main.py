import requests
import tweepy
import sys
import random
from requests_oauthlib import OAuth1

import books
import credentials
import selenium_poll_posting

class TwitterHandler:
    """
    This class handles all Twitter affairs, including:
    - Authentication
    - Poll posting and retrieveng
    - Tweeting text and images
    """
    def __init__(self):
        """
            Inits raw_auth, used to connect to Twitter API to retrieve polls info
            Inits tweepy api, used to fetch all other Twitter info in a more friendly way
        """
        self.raw_auth = OAuth1(
            credentials.consumer_key, 
            credentials.consumer_secret, 
            credentials.access_token, 
            credentials.access_token_secret) 

        auth = tweepy.OAuthHandler(credentials.consumer_key, credentials.consumer_secret)
        auth.set_access_token(credentials.access_token, credentials.access_token_secret)
        
        self.api = tweepy.API(auth)
        self.twitter_id = self.api.me().id

    def get_latest_tweet(self):
        return self.api.user_timeline(id = self.twitter_id, count = 1, tweet_mode="extended")[0]
         
    def has_poll(self,response_json):
        return response_json and 'includes' in response_json and 'polls' in response_json['includes']

    def get_poll(self, tweet_id):
        """
        Fetch poll object from a specific tweet (requires manual connection to twitter api)
        """
        poll_data_url = f'https://api.twitter.com/2/tweets?ids={tweet_id}&expansions=attachments.poll_ids&poll.fields=duration_minutes,end_datetime,options,voting_status'
        response = requests.get(poll_data_url, auth=self.raw_auth)
        response_json = response.json()
        
        if self.has_poll(response_json):
            return response_json['includes']['polls'][0]
        
        return None

    def get_latest_poll(self):
        """
        Retrieve last poll performed by this account
        Returns None if last tweet doesn't contain one
        """
        tweet = self.get_latest_tweet()
        return self.get_poll(tweet.id)

    def get_poll_winner(self, poll):
        """
        Iterates through poll options and returns the label of the one with most votes
        """
        winner = None
        votes = -1
        for option in poll['options']:
            if option['votes'] > votes:
                winner = option
                votes = option['votes']
        return winner['label']
    
    def post_poll(self, text, tweet_id, choice1, choice2, choice3=None,days=0,hours=0,minutes=15):
        """
        Use selenium to post poll 
        """
        pollBot = selenium_poll_posting.PollBot()
        pollBot.run(text, tweet_id, choice1, choice2, choice3, days, hours, minutes)



class Bot:

    def __init__(self):
        """
        Initializes twitter handler
        """
        print("Login in to Twitter API...")
        self.twitter_handler = TwitterHandler()
        self.hours = 1
        self.minutes = 0

    def post(self):
        """
        We only take actions on tweets that contain a hashtag, refering to a book
        If it has a poll then, its a note to continue the book
        It it has no poll then its the first chapter to publish
        """
        print("Fetching latest tweet...")
        latest_tweet = self.twitter_handler.get_latest_tweet()
        hashtags = latest_tweet.entities.get('hashtags')
        
        if not hashtags:
            print("Nothing to do here!")
        else:    
            # Just check for one, we expect no more and if they are they are ignored
            book_hash = hashtags[0]['text']
            if book_hash not in books.BOOK_PATHS:
                print("ERROR: Hashtag is not in books index!")
            else:
                print("Preparing to publish response...")
                book = books.Book(books.BOOK_PATHS[book_hash])

                poll = self.twitter_handler.get_poll(latest_tweet.id)
                if not poll:
                    self.start_publishing(book,latest_tweet.id)
                elif poll['voting_status'] == 'open':
                    print("Poll still open...")
                else:
                    winner = self.twitter_handler.get_poll_winner(poll)
                    self.publish_chapter(book,winner,latest_tweet.id)
                
    def start_publishing(self,book,tweet_id):
        """
        Publishes first chapter of book
        """
        self.publish_chapter(book, book.start,tweet_id)

    def publish_chapter(self,book, chapter_id,tweet_id):
        """
        Publish all pages as images and add a poll at the end to decide how to continue
        unless its the end, then just the images
        """
        chapter = book.guide[chapter_id]
        pages = chapter['pages']
        choices = chapter['choices']

        # Upload pages corresponding to chapter
        chunked_pages = chunks(pages,4)
        for chunk in chunked_pages:
            print("Publishing images..")
            images = [book.get_image(page_id) for page_id in chunk] 
            media_ids = [self.twitter_handler.api.media_upload(i).media_id_string  for i in images] 
            new_tweet = self.twitter_handler.api.update_status(media_ids=media_ids,in_reply_to_status_id=tweet_id)
            tweet_id = new_tweet.id

        # Post choices poll
        utterances = ["cómo seguimos?", "y ahora?", "mmm...", "y ahora qué?", ""]
        if choices:
            print("Publishing poll...")
            text = "#"+book.hash+" "+ random.choice(utterances)
            if len(choices) == 2:
                self.twitter_handler.post_poll(text, tweet_id, choices[0], choices[1], hours=self.hours, minutes=self.minutes)
            elif len(choices) == 3:
                self.twitter_handler.post_poll(text, tweet_id, choices[0], choices[1], choices[2], hours=self.hours, minutes=self.minutes)
            else:
                print("ERROR: choices not properly loaded for: " + book.hash)

        print("All done!")
        
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
if __name__=="__main__":
    bot = Bot() 
    bot.post()      