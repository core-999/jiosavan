# -----------------------------------------------
# 🔸 ThakurMusic Project
# 🔹 Developed & Maintained by: ThakurMusic Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2025 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# -----------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import Message, ChatMember
import logging
from ThakurMusic import app

logging.basicConfig(level=logging.INFO)

@app.on_message(filters.video_chat_started)
async def video_chat_started(client, message: Message):
    chat = message.chat
    await message.reply(
        f"🎥 vc ဖွင့်ပိဆိုတော့ သူက အရေးမလုပ်လိုက်လို့လား {chat.title}!\n\n ချစ်တယ်ဆိုတာ ယုံနေသ၍ ခံနေရမှာပဲ သီချင်းပဲနားထောင်😄"
    )

@app.on_message(filters.video_chat_ended)
async def video_chat_ended(client, message: Message):
    chat = message.chat
    await message.reply(
        f"🚫 ရပ်လိုက်ပိပေါ့ {chat.title}.\n\nသူက အရေးပေးလာလို့လား 👋"
    )
