import json
import logging

from botocore.vendored import requests

def lambda_handler(event, context):
    # TODO implement
    
    logging.info("API CALLED. EVENT IS:{}".format(event))
    print(event)
    location = event["currentIntent"]["slots"]["location"]
    cuisine = event["currentIntent"]["slots"]["cuisine"]
    diningtime = event["currentIntent"]["slots"]["time"]
    numberofpeople = event["currentIntent"]["slots"]["count"];
    
    print(json.dumps(event))
    
    # print(location + " " + )
    URL = "https://api.yelp.com/v3/businesses/search?location=" + location + "&categories=" + cuisine
    header = {
        
        'Authorization' : 'Bearer XXXXXXXXX---Enter Your Authorization Token Here---XXXXXXXXXXX '
    }
    
    message = "Here are my " + cuisine + " restaurant suggestions for "+  numberofpeople + " people for today at " + diningtime + ": "
    
    tempData = requests.get(URL, headers = header)
    
    print(tempData.text)
    dict=json.loads(tempData.text)
    names = ""
    
    print(dict)
    
    length = min(3,len(dict))
    
    for i in range(0, length):
        names = names + dict["businesses"][i]["name"] + " : "
        address = json.dumps(dict["businesses"][i]["location"]["display_address"])
        
        names = names + address + ", "
    
    names = names.replace('\"','')
    print('Names:',names)
    
    print('Address',address)

        
    print(message)
    
    return {"dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": message + names
                 }
            }} 
    