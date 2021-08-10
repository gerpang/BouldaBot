import csv
from nestedconversationbot import TYPING
import requests
import json
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    CallbackContext,
)
import datetime
from dbhelper import db

## State definitions
# Top level Conversation
SELECTING_ACTION, CREATE, LIST, EDIT = map(chr, range(4))
# 2nd level Conversation
SELECTING_EVENT, SELECTING_FEATURE = map(chr, range(4, 6))
# # 3rd level Conversation
# SELECTING_SOMETHING_ELSE = map(chr, range(8))
# Meta states
STOPPING, SHOWING, SHOWING_FEATURES = map(chr, range(6, 9))
END = ConversationHandler.END
# Other constants
(
    EVENT_ID,
    EVENT_NAME,
    EVENT_DATE,
    EVENT_TIME,
    ATTENDEES,
    VENUE,
    OWNER,
    START_OVER,
    FEATURES,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(9, 20))


# Helper
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# Top level callback
def start(update: Update, context: CallbackContext) -> str:
    menu_text = """
        Select any of the below options to create, edit or view events. To stop anytime, just say /stop.
"""

    buttons = [
        [
            InlineKeyboardButton(text="Create event", callback_data=str(CREATE)),
            InlineKeyboardButton(text="Edit event", callback_data=str(EDIT)),
        ],
        [
            InlineKeyboardButton(text="View events", callback_data=str(LIST)),
            InlineKeyboardButton(text="X", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=menu_text, reply_markup=keyboard)
    else:
        user = update.effective_user.username
        hi_text = "Hi there, {}! How may I assist you today?".format(user)
        update.message.reply_text(text=hi_text)
        update.message.reply_text(text=menu_text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text("Okay, bye.")

    return END


def end(update: Update, context: CallbackContext) -> int:
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()

    text = "See you around!"
    update.callback_query.edit_message_text(text=text)

    return END


def bop(update: Update, context: CallbackContext):
    # easter egg feature
    contents = requests.get("https://random.dog/woof.json").json()
    bop_pic = contents["url"]
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=bop_pic)
    return EDIT


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.",
    )


## Events


def create_event(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user.username

    context.bot.send_message(
        chat_id=chat_id,
        text="Hi {}, please provide the name, date, time, attendees, and venue of the event.".format(
            user
        ),
    )
    return CREATE


def create_event_gs(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user.username
    message = update.message.text

    event_details = [m.strip() for m in message.split(",")]
    db.add_event(event_details, user)

    context.bot.send_message(
        chat_id=chat_id, text="Thanks {}. Your event has been created.".format(user)
    )
    return ConversationHandler.END
    # context.bot.send_message(chat_id=chat_id, text="Sorry, didn't catch that. Did you mean to /create_event?")
    # return ConversationHandler


def list_events(update: Update, context: CallbackContext):
    user = update.effective_user.username  # .effective_user.username
    event_list = db.get_events(user)
    event_count = len(event_list)
    buttons = [
        [
            InlineKeyboardButton(
                text=str(id) + ". " + str(name), callback_data=str(EVENT_ID) + str(id)
            )
            for (id, name) in event_list
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text = "Hi {}, you have {} events. Which would you like to know more about?".format(
        user, event_count
    )
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_EVENT


def get_event(update: Update, context: CallbackContext):
    user = update.effective_user.username
    selected_event = update.callback_query.data.replace(str(EVENT_ID), "")

    event_dic = db.get_event_info(user, selected_event)
    event_info_text = """
    Event {}: {} will be happening on the {} at {}. The venue is {} and {} will be attending. Have fun!
    """.format(
        event_dic["event_id"],
        event_dic["event_name"],
        event_dic["event_date"],
        event_dic["event_time"],
        event_dic["venue"],
        event_dic["attendees"],
    )

    buttons = [
        [
            InlineKeyboardButton(
                text="Edit Event", callback_data=str(EDIT) + str(selected_event)
            ),
            InlineKeyboardButton(
                text="Back to All Events", callback_data=str(SELECTING_EVENT)
            ),
            InlineKeyboardButton(text="Exit", callback_data=str(END)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=event_info_text, reply_markup=keyboard)
    print("SHOWING EVENTS")
    return SHOWING_FEATURES


def show_data(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = "TESTING@#!@$%(@#U$@)#($"
    buttons = [[InlineKeyboardButton(text="Back", callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    user_data[START_OVER] = True
    return SHOWING


def get_event_features(update: Update, context: CallbackContext):
    print("IN get_event_features")
    user = update.effective_user.username
    selected_event = update.callback_query.data.replace(str(EDIT), "")
    event_dic = db.get_event_info(user, selected_event)
    button_list = list(
        InlineKeyboardButton(
            text="Edit {}".format(col.replace("_", " ").title()),
            callback_data="{}{}-{}".format(str(EDIT), str(selected_event), str(col)),
        )
        for col in event_dic.keys()
        if col != "event_id"
    )
    button_list.append(InlineKeyboardButton(text="Go back", callback_data=str(SHOWING)))
    buttons = list(chunks(button_list, 3))
    keyboard = InlineKeyboardMarkup(buttons)
    text = "What would you like to edit?"
    update.callback_query.answer()
    update.callback_query.edit_message_reply_markup(reply_markup=keyboard)
    return SELECTING_FEATURE


def get_feature_input(update: Update, context: CallbackContext):
    selected_event, selected_feature = update.callback_query.data.replace(
        str(EDIT), ""
    ).split("-")

    text = "Ok, tell me what *{}* should be changed to\.".format(
        selected_feature.replace("_", " ").title()
    )
    user_data = context.user_data
    print(user_data)
    user_data["UPDATE"] = {
        "CURRENT_FEATURE": selected_feature,
        "CURRENT_EVENT": selected_event,
    }
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.MARKDOWN_V2)
    return TYPING


def update_event(update: Update, context: CallbackContext):
    ### Call dbhelper command that updates the event data

    # user_data[FEATURES][user_data[CURRENT_FEATURE]] = update.message.text
    # user_data[START_OVER] = True
    user = update.effective_user.username
    user_data = context.user_data

    user_data["UPDATE"]["FEATURE_INPUT"] = update.message.text
    event_details = user_data
    db.update_event_info(user, event_details)
    update.message.reply_text("Ok, updated the event.")
    return LIST  # get_event(update, context)


def echo(update: Update, context: CallbackContext):
    stmt = update.message.text
    print("HEREEEEEEEEE")
    print(stmt)

    return stop


# text = "Updating {} to {}. Please confirm." #Yes/No buttons.
