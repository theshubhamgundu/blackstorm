import pymongo
from Sibyl_System import System, SIBYL, ENFORCERS, Sibyl_logs, system_cmd
import re
import Sibyl_System.plugins.Mongo_DB.message_blacklist as db
import Sibyl_System.plugins.Mongo_DB.name_blacklist as wlc_collection


@System.on(system_cmd(pattern=r'addbl ', allow_slash=False))
async def addbl(event):
    flag = re.match(".addbl -e (.*)", event.text, re.DOTALL)
    if flag:
        text = re.escape(flag.group(1))
    else:
        try:
            text = event.text.split(" ", 1)[1]
        except BaseException:
            return
    a = await db.update_blacklist(text, add=True)
    if a:
        await System.send_message(event.chat_id, f"Added {text} to blacklist")
    else:
        await System.send_message(event.chat_id, f" {text} is already blacklisted")


@System.on(system_cmd(pattern=r'addwlcbl'))
async def wlcbl(event):
    flag = re.match(".addbl -e (.*)", event.text, re.DOTALL)
    if flag:
        text = re.escape(flag.group(1))
    else:
        try:
            text = event.text.split(" ", 1)[1]
        except BaseException:
            return
    a = await wlc_collection.update_wlc_blacklist(text, add=True)
    if a:
        await System.send_message(event.chat_id, f"Added {text} to blacklist")
    else:
        await System.send_message(event.chat_id, f" {text} is already blacklisted")


@System.on(system_cmd(pattern=r'rmwlcbl'))
async def rmwlcbl(event):
    try:
        text = event.text.split(" ", 1)[1]
    except BaseException:
        return
    a = await wlc_collection.update_wlc_blacklist(text, add=False)
    if a:
        await System.send_message(event.chat_id, f"Removed {text} from blacklist")
    else:
        await System.send_message(event.chat_id, f"{text} is not blacklisted")


@System.on(system_cmd(pattern=r'rmbl ', allow_slash=False))
async def rmbl(event):
    try:
        text = event.text.split(" ", 1)[1]
    except BaseException:
        return
    a = await db.update_blacklist(text, add=False)
    if a:
        await System.send_message(event.chat_id, f"Removed {text} from blacklist")
    else:
        await System.send_message(event.chat_id, f"{text} is not blacklisted")


@System.on(system_cmd(pattern=r'listbl'))
async def listbl(event):
    bl_list = await db.get_blacklist()
    msg = "Currently Blacklisted strings:\n"
    for x in bl_list:
        msg += f"•{x}\n"
    await System.send_message(event.chat_id, msg)


@System.on(events.MessageEdited(incoming=True))
@System.on(events.NewMessage(incoming=True))
async def auto_gban_request(event):
    if event.from_id in ENFORCERS or event.from_id in SIBYL:
        return
    if event.chat_id == Sibyl_logs:
        return
    text = event.text
    words = await db.get_blacklist()
    if words:
        for word in words:
            pattern = r"( |^|[^\w])" + word + r"( |$|[^\w])"
            if re.search(pattern, text, flags=re.IGNORECASE):
                await System.send_message(Sibyl_logs, f"$AUTO\nTriggered by: [{event.from_id}](tg://user?id={event.from_id})\nMessage: {event.text}")
                return


@System.on(events.ChatAction())  # pylint:disable=E0602
async def auto_wlc_gban(event):
    user = await event.get_user()
    if user.id in ENFORCERS or user.id in SIBYL:
        return
    if event.user_joined:
        words = await wlc_collection.get_wlc_bl()
        if words:
            text = user.first_name
            for word in words:
                pattern = r"( |^|[^\w])" + word + r"( |$|[^\w])"
                if re.search(pattern, text, flags=re.IGNORECASE):
                    await System.send_message(Sibyl_logs, f"$AUTO\nTriggered by: [{event.from_id}](tg://user?id={event.from_id})\nUser joined and blacklisted string in name\nMatched String = {word}")

__plugin_name__ = "blacklist"

help_plus = """
Here is help for **String Blacklist**
`/addbl` - **Add trigger to blacklist**
`/rmbl` - **remove trigger from blacklist**
`/listbl` - **list blacklisted words**
Here is help for **Welcome Name-String Blacklist**
`/addwlcbl` - **Add new blacklisted name-string**
`/rmwlcbl` - **Remove blacklisted welcome-name-string**
Flags( -e // escape text ) to addbl & addwlcbl

**Notes:**
`/` `?` `.` `!` are supported prefixes.
**Example:** `/addbl` or `?addbl` or `.addbl`
"""
