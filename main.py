# Rexa Kadal gurun

import asyncio
from sys import version as pyver

import pyrogram
from pyrogram import __version__ as pyrover
from pyrogram import filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message

import config
import mongo
from mongo import db

loop = asyncio.get_event_loop()
SUDO_USERS = config.SUDO_USER

app = pyrogram.Client(
    ":RexaBot:",
    config.API_ID,
    config.API_HASH,
    bot_token=config.BOT_TOKEN,
)

save = {}
grouplist = 1
welcome_group = 2

async def init():
    await app.start()


    # Ini auto buat nambah grup di database rex   



    #Ini auto buat nambah user di database rex
    @app.on_message(filters.command("start"))
    async def start_command(_, message: Message):
        await message.reply("Bot Hidup masseh")

    @app.on_message(filters.command("addpost"))
    async def add_post(_, message: Message):
        if message.reply_to_message:
            chat_id = message.reply_to_message.sender.chat.id
        else:
            if len(message.command) < 2:
                return await message.reply_text("Berikan id grup/channel.")
            chat_id = message.text.split()[1]
            if "@" in chat_id:
                chat_id = chat_id.replace("@", "")
            chat_id = await app.get_chat(chat_id)
            schats = await mongo.get_served_chats()
            if chat_id.id in schats:
                return await message.reply_text(
                    "Grup / Channel ini sudah masuk di list POST",
            )
            added = await mongo.add_served_chat(chat_id.id)
            if added:
                await message.reply_text(f"Berhasil Channel [{chat_id.title}]({chat_id.invite_link}) telah ditambahkan di list POST")
            else:
                await message.reply("Gagal menambahkan Channel ke lisi POST")
                
    @app.on_message(filters.command("getpost"))                    
    async def get_post(_, message: Message):                    
        msg = "<b>LIST CHANNEL POST</b>\n\n"
        served_chats = []
        all_list = await mongo.get_served_chats()
        for chat in all_list:
            served_chats.append(int(chat["chat_id"]))    
        if not all_list:
            await message.reply("<b>Tidak ada blacklist gcast yang tersimpan.</b>")
            return
        for list in served_chats:
            group_name = await app.get_chat(list)
            msg += f"• [{group_name.title}]({group_name.invite_link})\n\n"
        await message.reply(msg)
        
        
    @app.on_message(filters.command("delpost"))
    async def delete_post(_, message: Message):
        if message.reply_to_message:
            chat_id = message.reply_to_message.sender.chat.id
        else:
            if len(message.command) < 2:
                return await message.reply_text("Berikan id grup/channel.")
            chat_id = message.text.split()[1]
            if "@" in chat_id:
                chat_id = chat_id.replace("@", "")
            chat_id = await app.get_chat(chat_id)
            schats = await mongo.get_served_chats()
            if chat_id.id in schats:
                return await message.reply_text(
                    "Grup / Channel ini sudah masuk di list POST",
            )
            added = await mongo.delete_served_chat(chat_id.id)
            if added:
                await message.reply_text(f"Berhasil Channel [{chat_id.title}]({chat_id.invite_link}) telah dihapus dari list POST")
            else:
                await message.reply("Gagal menghapus Channel dari lisi POST")        
        
    # Ini buat stats rex

    @app.on_message(
        filters.command("stats") & filters.user(SUDO_USERS)
    )
    async def stats_func(_, message: Message):
        if db is None:
            return await message.reply_text(
                "MONGO_DB_URI var not defined. Please define it first"
            )
        served_users = len(await mongo.get_served_users())
        served_chats = len(await mongo.get_served_chats())
        text = f""" **Game Bot Stats:**
        
**Python Version :** {pyver.split()[0]}
**Pyrogram Version :** {pyrover}

**Served Users:** {served_users} 
**Served Groups:** {served_chats}"""
        await message.reply_text(text)


    #Ini buat broadcastuser rex

    @app.on_message(
        filters.command("broadcastuser") & filters.user(SUDO_USERS)
    )
    async def broadcast_func(_, message: Message):
        if db is None:
            return await message.reply_text(
                "MONGO_DB_URI var nya mna mas rex. Tambahin dong"
            )
        if message.reply_to_message:
            x = message.reply_to_message.message_id
            y = message.chat.id
        else:
            if len(message.command) < 2:
                return await message.reply_text(
                    "**Usage**:\n/broadcastusers [MESSAGE] or [Reply to a Message]"
                )
            query = message.text.split(None, 1)[1]

        susr = 0
        served_users = []
        susers = await mongo.get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                await app.forward_messages(
                    i, y, x
                ) if message.reply_to_message else await app.send_message(
                    i, text=query
                )
                susr += 1
            except FloodWait as e:
                flood_time = int(e.x)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
        try:
            await message.reply_text(
                f"**Broadcasted Message to {susr} Users.**"
            )
        except:
            pass


    # Ini Post

    @app.on_message(
        filters.command("post") & filters.user(SUDO_USERS)
    )
    async def broad_group(_, message: Message):
        if db is None:
            return await message.reply_text(
                "MONGO_DB_URI ny mna Tambahin dong"
            )
        if message.reply_to_message:
            x = message.reply_to_message.message_id
            y = message.chat.id
        else:
            if len(message.command) < 2:
                return await message.reply_text(
                    "**Usage**:\n/post  [Text] atau [Balas kepesan]"
                )
            query = message.text.split(None, 1)[1]

        scht = 0
        served_chats = []
        schats = await mongo.get_served_chats()
        if not schats:
            return await message.reply("Tidak ada list Channel POST yang tersimpan")
        for chat in schats:
            served_chats.append(int(chat["chat_id"]))
        for i in served_chats:
            try:
                await app.forward_messages(
                    i, y, x
                ) if message.reply_to_message else await app.send_message(
                    i, text=query
                )
                scht += 1
            except FloodWait as e:
                flood_time = int(e.x)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
        try:
            await message.reply_text(
                f"**Konten terposting di {scht} Channel.**"
            )
        except:
            pass

    print("[Bot Posting] - Bot Posting Started")
    await idle()


if __name__ == "__main__":
    loop.run_until_complete(init())
