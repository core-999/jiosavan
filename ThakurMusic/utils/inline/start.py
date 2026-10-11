from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import config
from ThakurMusic import app
from ThakurMusic.utils.decorators.language import languageCB


# =========================
# START BUTTONS
# =========================

def start_panel(_):
    return [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT,
            ),
        ]
    ]


def private_panel(_):
    return [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT,
            ),
            InlineKeyboardButton(
                text=_["S_B_6"],
                url=config.SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_5"],
                url=config.OWNER_LINK,
            )
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="settings_back_helper",
            )
        ],
    ]


# =========================
# ABOUT
# =========================

@app.on_callback_query(filters.regex("^about$"))
@languageCB
async def about_callback(client, CallbackQuery, _):

    try:
        await CallbackQuery.answer()
    except:
        pass

    # ABOUT_1 from strings/langs/en.yml
    text = _["ABOUT_1"].format(app.mention)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="• ʙᴀᴄᴋ •",
                    callback_data="settings_back_helper",
                ),
                InlineKeyboardButton(
                    text="• ᴄʟᴏsᴇ •",
                    callback_data="close",
                ),
            ]
        ]
    )

    return await CallbackQuery.edit_message_caption(
        caption=text,
        reply_markup=keyboard,
    )
