import json
import time
import boto3

def lambda_handler(event, context):
    # TODO implement
    
    # string = event.message
    client = boto3.client('lex-runtime'); 
    response = client.post_text(
        botName='FindRestaurantsBot',
        botAlias='$LATEST',
        userId='Usqwer12312313',
        sessionAttributes={},
        inputText=event["message"]
    )
    
    return {
        'statusCode': 200,
        'headers': { 
            'Access-Control-Allow-Origin': '*', 
            'X-Requested-With': '*', 
            'Access-Control-Allow-Headers': 'Content-Type,Authorization, X-Amz-Date,X-Api-Key,X-Amz-Security-Token', 
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        }, 
        'body': {
            'messages': [
               {
                    'type': "String", 
                    'unstructured': {
                        'id': '001', 
                        'text': response['message'], 
                        'timestamp': time.time() 
                    }
                } 
            ]
        }
    }
