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

import asyncio
import os
from datetime import datetime, timedelta
from typing import Union
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import NoActiveGroupCall
from ntgcalls import TelegramServerError
from pytgcalls.types import Update, StreamEnded, GroupCallParticipant
from pytgcalls import filters as fl
from pytgcalls.types import AudioQuality, VideoQuality
from pytgcalls.types import MediaStream, ChatUpdate
import config
from config import autoclean
from ThakurMusic import LOGGER, YouTube, app
from ThakurMusic.misc import db
from ThakurMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
    is_vc_logger,
    is_thumb_enabled,
)
from ThakurMusic.utils.exceptions import AssistantErr
from ThakurMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from ThakurMusic.utils.inline.play import stream_markup
from ThakurMusic.utils.stream.autoplay import get_related_video, is_autoplay, add_to_history
from ThakurMusic.utils.logger import autoplay_logs
from ThakurMusic.utils.stream.queue import put_queue
from ThakurMusic.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

async def safe_delete(message, delay=0):
    if not message:
        return False
    try:
        if delay > 0:
            await asyncio.sleep(delay)
        await message.delete()
        return True
    except:
        return False

async def cleanup_all_messages(chat_id: int):
    check = db.get(chat_id)
    if not check:
        return
    tasks = []
    for item in check:
        mystic = item.get("mystic")
        queue_msg = item.get("queue_msg")
        if mystic:
            tasks.append(safe_delete(mystic))
        if queue_msg:
            tasks.append(safe_delete(queue_msg))
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(name="ThakurMusicXAss1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        self.userbot2 = Client(name="ThakurMusicXAss2", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING2))
        self.two = PyTgCalls(self.userbot2, cache_duration=100)
        self.userbot3 = Client(name="ThakurMusicXAss3", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING3))
        self.three = PyTgCalls(self.userbot3, cache_duration=100)
        self.userbot4 = Client(name="ThakurMusicXAss4", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING4))
        self.four = PyTgCalls(self.userbot4, cache_duration=100)
        self.userbot5 = Client(name="ThakurMusicXAss5", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING5))
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await cleanup_all_messages(chat_id)
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        await cleanup_all_messages(chat_id)
        try:
            if config.STRING1:
                await self.one.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_call(chat_id)
        except:
            pass
        try:
            await _clear_(chat_id)
        except:
            pass

    async def set_volume(self, chat_id: int, volume: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await assistant.change_volume_call(chat_id, volume)
        except Exception as e:
            LOGGER(__name__).error(f"Volume Error: {e}")

    async def mute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await assistant.mute(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Mute Error: {e}")

    async def unmute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await assistant.unmute(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Unmute Error: {e}")

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == str("0.5"):
                    vs = 2.0
                elif str(speed) == str("0.75"):
                    vs = 1.35
                elif str(speed) == str("1.5"):
                    vs = 0.68
                elif str(speed) == str("2.0"):
                    vs = 0.5
                else:
                    vs = 1.0
                proc = await asyncio.create_subprocess_shell(
                    cmd=(f"ffmpeg -i {file_path} -filter:v setpts={vs}*PTS -filter:a atempo={speed} -c:a libopus -b:a 192k -vbr on -compression_level 10 {out}"),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        stream = (MediaStream(out, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.FHD_1080p, ffmpeg_parameters=f"-ss {played} -to {duration}") if playing[0]["streamtype"] == "video" else MediaStream(out, audio_parameters=AudioQuality.HIGH, ffmpeg_parameters=f"-ss {played} -to {duration}", video_flags=MediaStream.Flags.IGNORE))
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.play(chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def apply_track_mode(self, chat_id: int, file_path, mode, playing):
        played_sec = playing[0].get("played", 0)
        duration = playing[0].get("dur", "00:00")
        streamtype = playing[0].get("streamtype", "audio")
        played_time = seconds_to_min(played_sec)

        if mode == "Echo":
            temp_file = f"/tmp/track_echo_{chat_id}.webm"
            ffmpeg_cmd = f'ffmpeg -i "{file_path}" -af "asetrate=44100*0.85,aresample=44100,aecho=0.8:0.9:1000:0.5,bass=g=8" -c:a libopus -b:a 192k -vbr on -compression_level 10 -y "{temp_file}"'
        elif mode == "Bass":
            temp_file = f"/tmp/track_bass_{chat_id}.webm"
            ffmpeg_cmd = f'ffmpeg -i "{file_path}" -af "apulsator=hz=0.125,bass=g=20:f=80:w=0.8,treble=g=-5" -c:a libopus -b:a 192k -vbr on -compression_level 10 -y "{temp_file}"'
        elif mode == "Slowed":
            temp_file = f"/tmp/track_slowed_{chat_id}.webm"
            ffmpeg_cmd = f'ffmpeg -i "{file_path}" -af "asetrate=44100*0.8,aresample=44100,aecho=0.8:0.88:60:0.4" -c:a libopus -b:a 192k -vbr on -compression_level 10 -y "{temp_file}"'
        elif mode == "Nightcore":
            temp_file = f"/tmp/track_night_{chat_id}.webm"
            ffmpeg_cmd = f'ffmpeg -i "{file_path}" -af "asetrate=44100*1.25,aresample=44100" -c:a libopus -b:a 192k -vbr on -compression_level 10 -y "{temp_file}"'
        else:
            temp_file = file_path
            ffmpeg_cmd = None

        if ffmpeg_cmd:
            proc = await asyncio.create_subprocess_shell(ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()
            actual_duration = await asyncio.get_event_loop().run_in_executor(None, check_duration, temp_file)
            new_seconds = int(actual_duration)
            new_duration = seconds_to_min(new_seconds)

            old_seconds = playing[0].get("seconds", 1)
            ratio = new_seconds / old_seconds
            played_time = seconds_to_min(int(played_sec * ratio))
        else:
            new_seconds = playing[0].get("seconds", 0)
            new_duration = duration

        await self.seek_stream(chat_id, temp_file, played_time, new_duration, streamtype)
        db[chat_id][0]["track_mode"] = mode
        db[chat_id][0]["track_mode_file"] = temp_file if mode != "Normal" else None
        db[chat_id][0]["seconds"] = new_seconds
        db[chat_id][0]["dur"] = new_duration

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except Exception:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        check = db.get(chat_id)
        if check and len(check) > 0:
            mystic = check[0].get("mystic")
            queue_msg = check[0].get("queue_msg")
            if mystic:
                asyncio.create_task(safe_delete(mystic))
            if queue_msg:
                asyncio.create_task(safe_delete(queue_msg))
        if video:
            stream = MediaStream(link, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.FHD_1080p)
        else:
            stream = MediaStream(link, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
        await assistant.play(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        stream = (MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.FHD_1080p, ffmpeg_parameters=f"-ss {to_seek} -to {duration}") if mode == "video" else MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=f"-ss {to_seek} -to {duration}"))
        await assistant.play(chat_id, stream)

    async def stream_call(self, link):
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.play(config.LOGGER_ID, MediaStream(link, audio_parameters=AudioQuality.HIGH))
        await asyncio.sleep(0.2)
        await assistant.leave_call(config.LOGGER_ID)

    async def join_call(self, chat_id: int, original_chat_id: int, link, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        if video:
            stream = MediaStream(link, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.FHD_1080p)
        else:
            stream = MediaStream(link, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
        try:
            await assistant.play(chat_id, stream)
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
        except Exception as e:
            raise AssistantErr(str(e))
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        thumb_status = await is_thumb_enabled(chat_id)

        if check and len(check) > 0:
            mystic = check[0].get("mystic")
            queue_msg = check[0].get("queue_msg")
            if mystic:
                asyncio.create_task(safe_delete(mystic))
            if queue_msg:
                asyncio.create_task(safe_delete(queue_msg))
            if len(check) > 1:
                next_queue = check[1].get("queue_msg")
                if next_queue:
                    asyncio.create_task(safe_delete(next_queue))

        await asyncio.sleep(0.05)

        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)

            if popped:
                rem = popped["file"]
                if rem in autoclean:
                    autoclean.remove(rem)

            if not check:
                if await is_autoplay(chat_id) and popped:
                    last_vidid = popped.get("vidid")
                    if last_vidid and last_vidid not in ["telegram", "soundcloud"]:
                        try:
                            related_vidid, details = await get_related_video(chat_id, last_vidid)
                            if related_vidid:
                                language = await get_lang(chat_id)
                                _ = get_string(language)
                                original_chat_id = popped.get("chat_id", chat_id)
                                mystic = await app.send_message(original_chat_id, "💕 <b>ᴀᴜᴛᴏᴘʟᴀʏ</b> | ꜰᴇᴛᴄʜɪɴɢ ɴᴇxᴛ sᴏɴɢ...💕")

                                title = (details["title"]).title()
                                duration_min = details["duration_min"]

                                try:
                                    file_path, direct = await YouTube.download(related_vidid, mystic, videoid=True, video=False)
                                except:
                                    await mystic.delete()
                                    await _clear_(chat_id)
                                    return await client.leave_call(chat_id)

                                if not file_path:
                                    await mystic.delete()
                                    await _clear_(chat_id)
                                    return await client.leave_call(chat_id)

                                db[chat_id] = []
                                await put_queue(chat_id, original_chat_id, file_path if direct else f"vid_{related_vidid}", title, duration_min, "ᴀᴜᴛᴏᴘʟᴀʏ", related_vidid, 0, "audio")

                                stream = MediaStream(file_path, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
                                try:
                                    await client.play(chat_id, stream)
                                except:
                                    await mystic.delete()
                                    await _clear_(chat_id)
                                    return await client.leave_call(chat_id)

                                await add_active_chat(chat_id)
                                button = stream_markup(_, chat_id)
                                await mystic.delete()

                                caption = _["stream_1"].format(f"https://t.me/{app.username}?start=info_{related_vidid}", title[:23], duration_min, "ᴀᴜᴛᴏᴘʟᴀʏ", "🎵 Audio")

                                if thumb_status:
                                    img = await get_thumb(related_vidid)
                                    run = await app.send_photo(chat_id=original_chat_id, photo=img, has_spoiler=False, caption=caption, reply_markup=InlineKeyboardMarkup(button))
                                else:
                                    run = await app.send_message(chat_id=original_chat_id, text=caption, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)

                                db[chat_id][0]["mystic"] = run
                                db[chat_id][0]["markup"] = "stream"
                                add_to_history(chat_id, related_vidid)
                                try:
                                    await autoplay_logs(chat_id, original_chat_id, title, duration_min, related_vidid)
                                except:
                                    pass
                                return
                        except Exception:
                            pass

                await cleanup_all_messages(chat_id)
                await _clear_(chat_id)
                await app.send_message(chat_id, "<b>💓 သီချင်းပဲ ဆက်နားထောင်ပါ။</b>\n<b>💔 သူကမှာ အဖက်မလုပ်တာ သူငယ်ချင်း 🤣 </b>\n /play <b> ᴛᴏ ᴀᴅᴅ ᴍᴏʀᴇ sᴏɴɢs..!</b>")
                return await client.leave_call(chat_id)
        except:
            try:
                await cleanup_all_messages(chat_id)
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
            except:
                return

        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        user_id = check[0]["user_id"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        db[chat_id][0]["played"] = 0
        exis = (check[0]).get("old_dur")
        if exis:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
        video = True if str(streamtype) == "video" else False

        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await app.send_message(original_chat_id, text=_["call_6"])
            if video:
                stream = MediaStream(link, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.FHD_1080p)
            else:
                stream = MediaStream(link, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
            try:
                await client.play(chat_id, stream)
            except:
                return await app.send_message(original_chat_id, text=_["call_6"])

            button = stream_markup(_, chat_id)
            caption = _["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user, "Vɪᴅᴇᴏ" if video else "🎵 Aᴜᴅɪᴏ")

            if thumb_status:
                img = await get_thumb(videoid)
                run = await app.send_photo(chat_id=original_chat_id, photo=img, has_spoiler=True, caption=caption, reply_markup=InlineKeyboardMarkup(button))
            else:
                run = await app.send_message(chat_id=original_chat_id, text=caption, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)

            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        elif "index_" in queued:
            stream = (MediaStream(videoid, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.FHD_1080p) if str(streamtype) == "video" else MediaStream(videoid, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE))
            try:
                await client.play(chat_id, stream)
            except:
                return await app.send_message(original_chat_id, text=_["call_6"])

            button = stream_markup(_, chat_id)
            caption = _["stream_2"].format(user)

            if thumb_status:
                run = await app.send_photo(chat_id=original_chat_id, photo=config.STREAM_IMG_URL, has_spoiler=True, caption=caption, reply_markup=InlineKeyboardMarkup(button))
            else:
                run = await app.send_message(chat_id=original_chat_id, text=caption, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)

            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        else:
            if video:
                stream = MediaStream(queued, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.FHD_1080p)
            else:
                stream = MediaStream(queued, audio_parameters=AudioQuality.HIGH, video_flags=MediaStream.Flags.IGNORE)
            try:
                await client.play(chat_id, stream)
            except:
                return await app.send_message(original_chat_id, text=_["call_6"])

            button = stream_markup(_, chat_id)
            if videoid == "telegram":
                caption = _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user, "Vɪᴅᴇᴏ" if video else "Aᴜᴅɪᴏ")
                photo = config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL
                if thumb_status:
                    run = await app.send_photo(chat_id=original_chat_id, photo=photo, has_spoiler=True, caption=caption, reply_markup=InlineKeyboardMarkup(button))
                else:
                    run = await app.send_message(chat_id=original_chat_id, text=caption, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif videoid == "soundcloud":
                caption = _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user, "Vɪᴅᴇᴏ" if video else "Aᴜᴅɪᴏ")
                if thumb_status:
                    run = await app.send_photo(chat_id=original_chat_id, photo=config.SOUNCLOUD_IMG_URL, has_spoiler=True, caption=caption, reply_markup=InlineKeyboardMarkup(button))
                else:
                    run = await app.send_message(chat_id=original_chat_id, text=caption, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                caption = _["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user, "Vɪᴅᴇᴏ" if video else "Aᴜᴅɪᴏ")
                if thumb_status:
                    img = await get_thumb(videoid)
                    run = await app.send_photo(chat_id=original_chat_id, photo=img, has_spoiler=True, caption=caption, reply_markup=InlineKeyboardMarkup(button))
                else:
                    run = await app.send_message(chat_id=original_chat_id, text=caption, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        if config.STRING1: pings.append(self.one.ping)
        if config.STRING2: pings.append(self.two.ping)
        if config.STRING3: pings.append(self.three.ping)
        if config.STRING4: pings.append(self.four.ping)
        if config.STRING5: pings.append(self.five.ping)
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        @self.one.on_update(fl.chat_update(ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP | ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.two.on_update(fl.chat_update(ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP | ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.three.on_update(fl.chat_update(ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP | ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.four.on_update(fl.chat_update(ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP | ChatUpdate.Status.CLOSED_VOICE_CHAT))
        @self.five.on_update(fl.chat_update(ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP | ChatUpdate.Status.CLOSED_VOICE_CHAT))
        async def stream_services_handler(client, update: Update):
            await cleanup_all_messages(update.chat_id)
            await self.stop_stream(update.chat_id)

        @self.one.on_update(fl.stream_end())
        @self.two.on_update(fl.stream_end())
        @self.three.on_update(fl.stream_end())
        @self.four.on_update(fl.stream_end())
        @self.five.on_update(fl.stream_end())
        async def stream_end_handler1(client: PyTgCalls, update: StreamEnded):
            await self.change_stream(client, update.chat_id)

ThakurMusic = Call()
