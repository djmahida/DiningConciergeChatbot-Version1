import math
import dateutil.parser
import datetime
import time
import os
import logging
import LambdaForYelpApi

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

validationError = None

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }



def validate_dining_suggestion(location, time, cuisine):
    
    locationList = ['jersey city', 'hoboken', 'newport' , 'brooklyn' , 'manhattan']
    cuisineList = ['chinese' , 'indian' , 'mexican', 'japanese']

    
    if location is not None and location.lower() not in locationList:
        return build_validation_result(False,
                                       'location',
                                       'Currently, there is no service in {}, Please select from {}'.format(location,locationList))
    if cuisine is not None and cuisine.lower() not in cuisineList:
        return build_validation_result(False,
                                       'cuisine',
                                       'Please select cuisine from {}'.format(cuisineList))

    if time is not None:
        if len(time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Time', None)

        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'Time', "Can you please tell me a Valid time?")


    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def diningSuggestionIntent(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    cuisine = get_slots(intent_request)["cuisine"]
    time = get_slots(intent_request)["time"]
    numberOfPeople = get_slots(intent_request)["count"]
    location = get_slots(intent_request)["location"]
    
    source = intent_request['invocationSource']
    
    
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_dining_suggestion(location, time, cuisine)
        
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

        return delegate(output_session_attributes, get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thanks, your order for {} has been placed and will be ready for pickup by {} on {}'.format(flower_type, pickup_time, date)})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greetingIntent(intent_request)
        
    elif intent_name == 'ThankyouIntent':
        return thankyouIntent(intent_request)
        
    elif intent_name == 'DiningSuggestionIntent':
        return diningSuggestionIntent(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    
    logging.info("")
    currentIntent = event['currentIntent']['name']
    invocationSource = event['invocationSource']
    
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    
    if invocationSource == "DialogCodeHook":
        return dispatch(event)

    elif invocationSource == "FulfillmentCodeHook":
        return LambdaForYelpApi.lambda_handler_new(event,context)