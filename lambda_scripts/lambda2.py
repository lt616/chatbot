import argparse
import json
import pprint
from botocore.vendored import requests
import sys
import urllib
import boto3
import time


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


def lambda_handler(event, context):
    
    sqs = boto3.client('sqs')

    queue_url = 'https://sqs.us-west-2.amazonaws.com/219260801235/chatbot-sqs'
    
    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )
    
    # print(response) 
    if not "Messages" in response: 
        return None
    
    message = response['Messages'][0]
    # print(message) 
    receipt_handle = message['ReceiptHandle']
    
    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    # print('Received and deleted message: %s' % message) 
    
    input_msg = json.loads(message['Body'])
    
    res = find_restaurant(input_msg)
    
    # send message
    sns = boto3.client('sns') 
    number = '+19179294401' 
    # sns.publish(PhoneNumber = number, Message=json.dumps(res)) 
    response = sns.publish(PhoneNumber = '+19177054492', Message='Hi, is that Lingyu Gong? Do you know who I am?????')
    # print(response) 
    # save record 
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chatbot_suggestion')
    table.put_item(
        Item={
            'timestamp': str(time.time()), 
            'meal_location': input_msg['MealLocation'], 
            'meal_curisine': input_msg['MealCuisine'], 
            'meal_date': input_msg['MealDate'], 
            'meal_time': input_msg['MealTime'], 
            'client_phone_num': input_msg['ClientPhoneNum'], 
            'client_num': input_msg['ClientNum'], 
            'suggestions': json.dumps(res)
        }
    ) 
    
    print('complete') 
   
    
    
def find_restaurant(message): 
    # Yelp Fusion no longer uses OAuth as of December 7, 2017.
    # You no longer need to provide Client ID to fetch Data
    # It now uses private keys to authenticate requests (API Key)
    # You can find it on
    # https://www.yelp.com/developers/v3/manage_app

    API_KEY = '1d0HZ4tOdS7Lgyh3LOyFmyXU76WsbScZjt03awEvsrkABOTO-BytlmJrb1gA2t3MCaAt8EunBgDozMKF4BrY4DNMWPyVuhzxaOvuu8chnnaCDiPOrwrmzx7f8HjnW3Yx' 
    
    
    # API constants, you shouldn't have to change these.
    API_HOST = 'https://api.yelp.com'
    SEARCH_PATH = '/v3/businesses/search'
    BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
    
    
    # Defaults for our simple example.
    DEFAULT_TERM = 'restaurant'
    DEFAULT_LOCATION = 'Manhanttan'
    SEARCH_LIMIT = 5
    
    url_params = {
        'term': DEFAULT_TERM, 
        'location': message['MealLocation'], 
        'categories': message['MealCuisine'], 
        'limit': SEARCH_LIMIT
    }
    
    url = API_HOST + SEARCH_PATH 
    
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
    } 
    
    response = requests.request('GET', url, headers=headers, params=url_params) 
    
    return response.json()