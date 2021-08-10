from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
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
        level=logging.DEBUG,
    )

    # Add handlers for allowed commands
    # dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("bop", bop))

    create_events_request_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(create_event, pattern="^" + str(CREATE) + "$")
        ],
        states={
            CREATE: [MessageHandler(Filters.text & (~Filters.command), create_event_gs)]
        },
        fallbacks=[CommandHandler("stop", stop)],
    )
    dp.add_handler(create_events_request_handler)

    list_events_request_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(list_events, pattern="^" + str(LIST) + "$"),
            CallbackQueryHandler(get_event, pattern="^" + str(SELECTING_EVENT) + "$"),
        ],
        states={
            SELECTING_EVENT: [
                CallbackQueryHandler(get_event, pattern="^" + str(EVENT_ID))
            ],
            SHOWING: [
                CallbackQueryHandler(get_event_features, pattern="^" + str(EDIT)),
                CallbackQueryHandler(
                    list_events, pattern="^" + str(SELECTING_EVENT) + "$"
                ),
            ],
            SHOWING_FEATURES: [
                CallbackQueryHandler(get_event_features, pattern="^" + str(EDIT)),
            ],
            SELECTING_FEATURE: [
                CallbackQueryHandler(get_feature_input, pattern="^" + str(EDIT)),
            ],
            TYPING: [MessageHandler(Filters.text & ~Filters.command, update_event)],
        },
        fallbacks=[CommandHandler("stop", stop), CommandHandler("echo", echo)],
        map_to_parent={
            # SHOWING:SHOWING,
            END: SELECTING_ACTION,
            STOPPING: END,
        },
    )
    dp.add_handler(list_events_request_handler)

    ## Top level Conv Handler
    selection_handlers = [
        create_events_request_handler,
        list_events_request_handler,
        # CallbackQueryHandler(create_events_request_handler, pattern="^" + str(CREATE) + "$"),
        CallbackQueryHandler(bop, pattern="^" + str(EDIT) + "$"),
        CallbackQueryHandler(end, pattern="^" + str(END) + "$"),
    ]
    start_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SHOWING: [CallbackQueryHandler(start, pattern="^" + str(END) + "$")],
            SELECTING_ACTION: selection_handlers,
            # CREATE: selection_handlers,
            # LIST: [list_events_request_handler],
            # EDIT: [list_events_request_handler],
            STOPPING: [CommandHandler("start", start)],
        },
        fallbacks=[CommandHandler("stop", stop), CommandHandler("echo", echo)],
    )
    dp.add_handler(start_conv)

    ## 2nd level
    # add_event_conv = ConversationHandler(
    #     entry_points=[
    #         CallbackQueryHandler(select_level, pattern="^" + str(CREATE) + "$")
    #     ],
    #     states={},
    #     fallbacks=[],
    #     map_to_parent=[],
    # )

    # dp.add_handler(MessageHandler(Filters.command, unknown))  # must be last
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
