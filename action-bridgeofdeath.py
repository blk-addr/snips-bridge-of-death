#!/usr/bin/env python2

import paho.mqtt.client as mqtt
import json
import uuid

mqtt_client = mqtt.Client()
HOST = 'localhost'
PORT = 1883

TOPIC_END_SESSION = 'hermes/dialogueManager/endSession'
TOPIC_SESSION_ENDED = 'hermes/dialogueManager/sessionEnded'
TOPIC_CONTINUE_SESSION = 'hermes/dialogueManager/continueSession'
TOPIC_PLAY_WAV = 'hermes/audioServer/{}/playBytes/'

INTENT_TOPIC_BASE = 'hermes/intent/'
TOPIC_BRIDGE_OF_DEATH = '{}blk_addr:bridgeOfDeath'.format(INTENT_TOPIC_BASE)
TOPIC_NOT_AFRAID = '{}blk_addr:notAfraid'.format(INTENT_TOPIC_BASE)
TOPIC_GET_NAME = '{}blk_addr:getName'.format(INTENT_TOPIC_BASE)
TOPIC_GET_QUEST = '{}blk_addr:getQuest'.format(INTENT_TOPIC_BASE)
TOPIC_GET_COLOR = '{}blk_addr:getColor'.format(INTENT_TOPIC_BASE)
TOPIC_GET_CAPITAL = '{}blk_addr:getAssyrianCapital'.format(INTENT_TOPIC_BASE)
TOPIC_SPEED_OF_SWALLOW = '{}blk_addr:speedOfSwallow'.format(INTENT_TOPIC_BASE)

INTENT_NOT_AFRAID = 'blk_addr:notAfraid'
INTENT_GET_NAME = 'blk_addr:getName'
INTENT_GET_QUEST = 'blk_addr:getQuest'
INTENT_GET_COLOR = 'blk_addr:getColor'
INTENT_GET_CAPITAL = 'blk_addr:getAssyrianCapital'
INTENT_SPEED_OF_SWALLOW = 'blk_addr:speedOfSwallow'

third_question = 0

in_session = False

# Look at The Final Rip Off

def on_connect(client, userdata, flags, rc):
    # Subscribe to topics
    mqtt_client.subscribe(TOPIC_BRIDGE_OF_DEATH)
    mqtt_client.subscribe(TOPIC_NOT_AFRAID)
    mqtt_client.subscribe(TOPIC_GET_NAME)
    mqtt_client.subscribe(TOPIC_GET_QUEST)
    mqtt_client.subscribe(TOPIC_GET_COLOR)
    mqtt_client.subscribe(TOPIC_GET_CAPITAL)
    mqtt_client.subscribe(TOPIC_SPEED_OF_SWALLOW)
    mqtt_client.subscribe(TOPIC_SESSION_ENDED)

    # Set callbacks for topics
    mqtt_client.message_callback_add(TOPIC_BRIDGE_OF_DEATH, bridge_of_death)
    mqtt_client.message_callback_add(TOPIC_NOT_AFRAID, not_afraid)
    mqtt_client.message_callback_add(TOPIC_GET_NAME, get_name)
    mqtt_client.message_callback_add(TOPIC_GET_QUEST, get_quest)
    mqtt_client.message_callback_add(TOPIC_GET_COLOR, get_color)
    mqtt_client.message_callback_add(TOPIC_GET_CAPITAL, get_capital)
    mqtt_client.message_callback_add(TOPIC_SPEED_OF_SWALLOW, speed_of_swallow)
    mqtt_client.message_callback_add(TOPIC_SESSION_ENDED, session_ended)

def bridge_of_death(client, userdata, msg):
    global in_session
    in_session = True

    data = json.loads(msg.payload)
    site_id = data['siteId']
    continue_session(msg, [INTENT_NOT_AFRAID])
    play_wav(site_id, 'mp_stop_cross_bridge.wav')

def not_afraid(client, userdata, msg):
    if not in_session:
        end_session(msg, 'Not in bridge of death session')
        return

    data = json.loads(msg.payload)
    site_id = data['siteId']
    play_wav(site_id, 'mp_what_is_your_name.wav')
    continue_session(msg, [INTENT_GET_NAME])

def get_name(client, userdata, msg):
    if not in_session:
        end_session(msg, 'Not in bridge of death session')
        return

    data = json.loads(msg.payload)
    site_id = data['siteId']
    play_wav(site_id, 'mp_what_is_your_quest.wav')
    continue_session(msg, [INTENT_GET_QUEST])

def get_quest(client, userdata, msg):
    if not in_session:
        end_session(msg, 'Not in bridge of death session')
        return

    global third_question
    data = json.loads(msg.payload)
    site_id = data['siteId']

    # determine which question to ask in order
    if third_question == 0 or third_question > 3: # if this is the first run, or if we got through all
        third_question = 0 # reset the counter
        play_wav(site_id, 'mp_what_is_your_color.wav')
        continue_session(msg, [INTENT_GET_COLOR])
    elif third_question == 1:
        play_wav(site_id, 'mp_what_is_capital_assyria.wav')
        continue_session(msg, [INTENT_GET_CAPITAL])
    elif third_question == 2:
        play_wav(site_id, 'mp_what_is_your_color.wav')
        continue_session(msg, [INTENT_GET_COLOR])
    else:
        play_wav(site_id, 'mp_air_speed_swallow.wav')
        continue_session(msg, [INTENT_SPEED_OF_SWALLOW])

    third_question += 1 # set the counter to the next value for the next run-thru

def get_color(client, userdata, msg):
    if not in_session:
        end_session(msg, 'Not in bridge of death session')
        return

    data = json.loads(msg.payload)
    site_id = data['siteId']
    slots = data['slots']
    color = ''
    second_color = ''

    # populate the first and second colors
    for slot in slots:
        if slot['slotName'] == 'color':
            print('color: {}'.format(slot['rawValue']))
            color = slot['rawValue']
        elif slot['slotName'] == 'secondColor':
            print('secondColor: {}'.format(slot['rawValue']))
            second_color = slot['rawValue']

    if second_color != '' or color == '': # determine if the answer was correct or not
        play_wav(site_id, 'mp_auuuuuuuuugh.wav')
    else:
        play_wav(site_id, 'mp_right_off_you_go.wav')

    end_session(msg, None)

def get_capital(client, userdata, msg):
    if not in_session:
        end_session(msg, 'Not in bridge of death session')
        return

    data = json.loads(msg.payload)
    site_id = data['siteId']
    slots = data['slots']
    capital = ''

    for slot in slots:
        if slot['slotName'] == 'assyriancapital':
            capital = slot['rawValue']

    if capital.lower() == 'assur':
       play_wav(site_id, 'mp_right_off_you_go.wav')
    else:
        play_wav(site_id, 'mp_auuuuuuuuugh.wav')

    end_session(msg, None)

def speed_of_swallow(client, userdata, msg):
    if not in_session:
        end_session(msg, 'Not in bridge of death session')
        return

    data = json.loads(msg.payload)
    site_id = data['siteId']
    slots = data['slots']
    swallow_1 = ''
    swallow_2 = ''

    for slot in slots:
        if slot['slotName'] == 'swallow':
            if swallow_1 == '':
                print('swallow_1: {}'.format(slot['rawValue']))
                swallow_1 = slot['rawValue']
            else:
                print('swallow_2: {}'.format(slot['rawValue']))
                swallow_2 = slot['rawValue']

    if swallow_1 == '':
        play_wav(site_id, 'mp_auuuuuuuuugh.wav')
    else:
        play_wav(site_id, 'mp_what_i_dont_know_that.wav')

    end_session(msg, None)

def play_wav(site_id, wav):
    unique_id = uuid.uuid1()
    file = open('audio/' + wav, 'r')
    data = file.read()
    file.close()
    byte_array = bytearray(data)
    mqtt_client.publish('{}{}'.format(TOPIC_PLAY_WAV.format(site_id), unique_id), byte_array)

def get_json(msg, text):
    data = json.loads(msg.payload)
    site_id = data['siteId']
    session_id = data['sessionId']
    return json.dumps({ 'siteId': site_id, 'sessionId': session_id, 'text': text })

def get_json_with_filter(msg, intent_filter):
    data = json.loads(msg.payload)
    site_id = data['siteId']
    session_id = data['sessionId']
    return json.dumps({ 'siteId': site_id, 'sessionId': session_id, 'text': '',
        'intentFilter': intent_filter,
        'reactivatedFromSessionId': session_id })

def continue_session(msg, intent_filter):
    json = get_json_with_filter(msg, intent_filter)
    mqtt_client.publish(TOPIC_CONTINUE_SESSION, json)

def end_session(msg, text):
    json = get_json(msg, text)
    mqtt_client.publish(TOPIC_END_SESSION, json)

def session_ended(client, userdata, msg):
    global in_session
    in_session = False
    print('Set in_session False')

if __name__ == '__main__':
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(HOST, PORT)
    mqtt_client.loop_forever()