import csv
import requests
import json
from telegram import Update
from telegram.ext import CommandHandler, ConversationHandler, CallbackContext
import datetime
from dbhelper import db

CREATE = range(0)
LIST, UPDATE = range(1)

## General
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text="Hi there! How may I assist you today?"
        # ,reply_markup=reply_markup
    )


def bop(update: Update, context: CallbackContext):
    contents = requests.get("https://random.dog/woof.json").json()
    bop_pic = contents["url"]
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=bop_pic)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


## Events


def create_event(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update["message"]["chat"]["username"]

    context.bot.send_message(
        chat_id=chat_id,
        text="Hi {}, please provide the name, date, time, attendees, and venue of the event.".format(
            user
        ),
    )
    return CREATE


def create_event_gs(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update["message"]["chat"]["username"]
    message = update.message.text

    # if last_command == "create_event":
    # temporary:
    event_details = [m.strip() for m in message.split(",")]
    db.add_event(event_details, user)

    context.bot.send_message(
        chat_id=chat_id, text="Thanks {}. Your event has been created.".format(user)
    )
    return ConversationHandler.END
    # context.bot.send_message(chat_id=chat_id, text="Sorry, didn't catch that. Did you mean to /create_event?")
    # return ConversationHandler


def list_events(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update["message"]["chat"]["username"]

    # get events info
    event_list = db.get_events(user)
    event_count = len(event_list)

    message_to_send = """
    Hi {}, you have {} events. Which would you like to know more about? (Please enter the preceding event ID)\n""".format(
        user, event_count
    )
    message_to_send += "\n".join(
        [str(id) + ". " + name for (id, name) in event_list]
    )  ####***********
    message_to_send += (
        "\n Or if you dunno then press /cancel and let me go back to sleep"
    )
    context.bot.send_message(chat_id=chat_id, text=message_to_send)
    return LIST


def list_events_requested(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update["message"]["chat"]["username"]
    message = update.message.text.strip()

    event_dic = db.get_event_info(user, int(message))
    print(">>>", len(event_dic))
    print(event_dic)
    message_to_send = """
    Event {}: {} will be happening on the {} at {}. The venue is {} and {} will be attending. Have fun!
    """.format(
        event_dic["event_id"],
        event_dic["event_name"],
        event_dic["event_date"],
        event_dic["event_time"],
        event_dic["venue"],
        event_dic["attendees"],
    )

    context.bot.send_message(chat_id=chat_id, text=message_to_send)
    context.bot.send_message(
        chat_id=chat_id,
        text="Enter /update_event if you would like to make changes to {}.".format(
            event_dic["event_name"]
        ),
    )
    return ConversationHandler.END
    # context.bot.send_message(chat_id=chat_id, text="Sorry, didn't catch that. Did you mean to /list_events?")
    # return ConversationHandler.END


# def update_event(update: Update, context: CallbackContext):
#     chat_id = update.effective_chat.id
#     user = update["message"]["chat"]["username"]
#     message = update.message.text.strip()

#     return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    # logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        "zzz. Goodnight. Jio me again with /start."  # , reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
