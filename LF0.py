import json
import boto3

print('Loading function')


def lambda_handler(event, context):
   
    
    userId = event['identityID']
    
    print(userId)
    
    # TODO implement
    message = event['message']
    
    client = boto3.client('lex-runtime')
    
    response = client.post_text(
    botName = 'DiningConciergeBot',
    botAlias = 'Prod',
    userId = userId,
    inputText = message)
    
    print(response)

    return response
