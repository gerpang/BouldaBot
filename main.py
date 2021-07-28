from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
import logging
from commands import *
import json


def main():

    with open("token.json", "r") as f:
        telegram_token = json.load(f)["Telegram"]["token"]
    updater = Updater(token=telegram_token)
    dp = updater.dispatcher
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    # Add handlers for allowed commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("bop", bop))

    create_events_request_handler = ConversationHandler(
        entry_points=[CommandHandler("create_event", create_event)],
        states={
            CREATE: [MessageHandler(Filters.text & (~Filters.command), create_event_gs)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(create_events_request_handler)

    list_events_request_handler = ConversationHandler(
        entry_points=[CommandHandler("list_events", list_events)],
        states={
            LIST: [
                MessageHandler(Filters.text & (~Filters.command), list_events_requested)
            ]
            # GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],
            # PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            # LOCATION: [
            #     MessageHandler(Filters.location, location),
            #     CommandHandler('skip', skip_location),
            # ],
            # BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(list_events_request_handler)

    dp.add_handler(MessageHandler(Filters.command, unknown))  # must be last
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
