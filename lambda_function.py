import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Merchant') 

def lambda_handler(event, context):
    
    merchant_name = event.get('merchant_name')
    merchant_token = event.get('merchant_token')
    
    # Look up the merchant in DynamoDB by name
    response = table.get_item(
        Key={
            'Name': merchant_name,
            'Token': merchant_token
        }
    )
  
    item = response.get('Item')
    if item:
        auth_status = "Merchant Authorized"
    else:
        auth_status = "Merchant Not Authorized"
    
    body = f"Status: 200 OK\n\nAuthorization: {auth_status}\n\nReceived:\n\n"
    body += "\n".join(f"{key}: {value}" for key, value in event.items())
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": body
    }
