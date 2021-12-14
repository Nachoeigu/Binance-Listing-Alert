import tweepy
import requests
import json
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from dotenv import load_dotenv
import os 


class TelegramBot():

    #We put the credentials for logining in Telegram
    def __init__(self):
        self.token = os.getenv('telegram_token')
        self.chat_id = os.getenv('telegram_chat_id')

    #This method get a text as input and send the message to the channel of Telegram    
    def send_message(text):
        url_request = "https://api.telegram.org/bot"+ self.token + "/sendMessage" + "?chat_id=" + self.chat_id + "&text=" + text
        results = requests.get(url_request)

class TwitterBot(TelegramBot):

    #We put the credentials and stablish the conection with the Twitter API and Google API
    def __init__(self):
        load_dotenv()

        #Conection with Twitter API
        auth = tweepy.OAuthHandler(os.getenv('twitter_consumer_key'), os.getenv('twitter_consumer_secret'))
        auth.set_access_token(os.getenv('twitter_access_token'), os.getenv('twitter_access_token_secret'))
        self.api = tweepy.API(auth,wait_on_rate_limit = True)

        # Conection with Google API
        gc = gspread.service_account(filename = 'credentials.json') 
        #Before executing the Bot, we should have the Google spreadsheets where we will store the data. One sheet per figure.
        self.sh = gc.open_by_key(os.getenv('spreadsheet_id')) 

    #We analyze if these figures started following someone new
    def analyzing_new_listings(self):

        #We place the google cursor in the correct sheet
        worksheet = self.sh.get_worksheet(0) #0 = first sheet

        #We extract the last tweet we scraped
        values_list = worksheet.col_values(1)
        description = values_list[1:]

        try:
            #With this we retrieve the basic information about the profile: one of those are the last tweet
            data = self.api.get_user(screen_name = 'binance')
            data = data._json
            data = data['status']['text'].lower()
            
            #If the last tweet is not in the Google spreadsheet
            if data not in description:
                
                #And if the last tweet contains "will list", turn on the alert
                if data.find('will list') != -1:
                    telegram = TelegramBot()

                    try:
                        telegram.send_message(str(data)) 

                    except:
                        telegram.send_message('New listing in Binance: https://twitter.com/binance')

                    try:
                        df = pd.DataFrame({'update':data}) 

                    except:
                        df = pd.DataFrame({'update':data}, index= [0])

                    self.sh.values_append('Hoja 1', {'valueInputOption': 'USER_ENTERED'}, {'values': df.values.tolist()}) 
                
                else:
                    print('Nothing new yet')
                    pass

            else:
                print('Nothing new yet')
                pass

        except:
            print('The process failed')
            pass
