import csv
import requests
import json
from telegram import Update
from telegram.ext import CommandHandler, ConversationHandler, CallbackContext
import datetime

CREATE = range(0)
LIST = range(0)

## General 
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Hi there! How may I assist you today?"
                           # ,reply_markup=reply_markup
    )

def bop(update: Update, context: CallbackContext):
    contents = requests.get('https://random.dog/woof.json').json()    
    bop_pic = contents['url']
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=bop_pic)

def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

## Events

def create_event(update: Update, context: CallbackContext):
    chat_id=update.effective_chat.id
    user = update["message"]["chat"]["username"]
    with open('mem.json','r') as f:
        mem = json.load(f)
    mem['Users'][user] = {"last_command":"create_event"}
    with open('mem.json','w') as f:
        # json.dumps(mem, f, default=str)
        json.dump(mem, f)

    context.bot.send_message(chat_id=chat_id, text="Hi {}, please provide the name, date, time, duration, attendees and venue of the event.".format(user))
    return CREATE
    
def create_event_gs(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update["message"]["chat"]["username"]
    message = update.message.text
    with open('mem.json','r') as f:
        mem = json.load(f)
    assert user in mem['Users']
    last_command = mem['Users'][user]["last_command"]
    
    if last_command == "create_event":
        event_id = max([int(x) for x in mem['Events'].keys()]) + 1
        # temporary: 
        name, date, time, duration, attendees, venue = message.split(',')
        mem['Events'][str(event_id)] = {
            "ID" : event_id,
            "Title" : name,
            "Date" : date,
            "Time" : time,
            "Duration" : duration,
            "Attendees" : attendees,
            "Venue" : venue,
            "Status": "Upcoming"
        }
        with open('mem.json','w') as f:
            json.dump(mem, f)


        context.bot.send_message(chat_id=chat_id, text="Your event has been created.")
        return ConversationHandler.END
    context.bot.send_message(chat_id=chat_id, text="Sorry, didn't catch that. Did you mean to /create_event?")
    return ConversationHandler.END
    
    
def list_events(update: Update, context: CallbackContext):
    chat_id=update.effective_chat.id
    user = update["message"]["chat"]["username"]
    with open('mem.json','r') as f:
        mem = json.load(f)
    mem['Users'][user] = {"last_command":"list_events"}
    with open('mem.json','w') as f:
        json.dump(mem, f)

    # get events info
    event_list = ["{}. {}".format(d['ID'], d["Title"]) for d in mem['Events'].values() if d['Status'] == "Upcoming"]
    event_count = len(event_list)

    message_to_send = """
    Hi {}, you have {} upcoming events. Which would you like to know more about? (Please enter the preceding event ID)\n""".format(user, event_count)
    message_to_send += "\n".join(event_list)
    message_to_send += "\n Or if you dunno then press /cancel and let me go back to sleep"
    context.bot.send_message(chat_id=chat_id, text=message_to_send)
    return LIST

def list_events_requested(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update["message"]["chat"]["username"]
    message = update.message.text.strip()
    with open('mem.json','r') as f:
        mem = json.load(f)
    assert user in mem['Users']
    try:
        assert message in mem['Events'] # requested a valid id
    except AssertionError as e:
        context.bot.send_message(chat_id=chat_id, text="Please enter a valid event ID number.")
    last_command = mem['Users'][user]["last_command"]
    
    if last_command == "list_events":
        event_dic = mem['Events'][message]
        message_to_send = """
        Event {}: {} will be happening on the {} at {} for {}. The venue is {} and {} will be attending. Have fun!
        """.format(event_dic['ID'],event_dic['Title'],event_dic['Date'],event_dic['Time'],event_dic['Duration'],event_dic['Venue'],event_dic['Attendees'])
        
        with open('mem.json','w') as f:
            json.dump(mem, f)

        context.bot.send_message(chat_id=chat_id, text=message_to_send)
        context.bot.send_message(chat_id=chat_id, text="Enter /update_event if you would like to make changes to {}.".format(event_dic['Title']))
        return ConversationHandler.END
    context.bot.send_message(chat_id=chat_id, text="Sorry, didn't catch that. Did you mean to /list_events?")
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'zzz. Goodnight. Jio me again if you want to /create_event.' #, reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END