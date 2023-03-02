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



    @app.on_message(filters.command("start"))
    async def start_command(_, message: Message):
        await mongo.add_served_user(message.from_user.id)
        msg = """
👋🏻 Hallo, <a href=tg://openmessage?user_id={message.from_user.id}>{message.from_user.first_name} {message.from_user.last_name or ''}</a> Ada yang bisa kami bantu?      
Silahkan sampaikan keinginan kamu disini.
"""
        await message.reply(msg)

        
    @app.on_message(filters.command("menu"))
    async def menu_command(_, message: Message):
        msg = """
LIST MENU BOT

• /post [text] atau [balas ke pesan] - Untuk memposting konten ke semua channel yang tersimpan di list POST.
  contoh : /post promo hari ini gaes.

• /addpost [id / username channel] - Untuk menambahkan channel ke list POST.
  contoh : /addpost @channelku

• /delpost [id / username channel] - Untuk menghapus channel dari list POST.
  contoh : /delpost @channelku

• /getpost - Untuk melihat list channel POST yang terisimpan.

• /broadcast [text] atau [balas ke pesan] - Untuk menyiarkan pesan atau broadcasting ke semua user yang pernah start bot.

• /stats - Untuk melihat statistik pengguna bot
"""
        await message.reply(msg)


    @app.on_message(filters.command("addpost"))
    async def add_post(_, message: Message):
        if message.reply_to_message:
            chat_id = message.reply_to_message.sender.chat.id
        else:
            if len(message.command) < 2:
                return await message.reply_text("Berikan id / username channel")
            chat_id = message.text.split()[1]
            if "@" in chat_id:
                chat_id = chat_id.replace("@", "")
            chat_id = await app.get_chat(chat_id)
            schats = await mongo.get_served_chats()
            if chat_id.id in schats:
                return await message.reply_text(
                    "Channel ini sudah masuk di list POST",
            )
            added = await mongo.add_served_chat(chat_id.id)
            if added:
                await message.reply_text(f"Berhasil Channel [{chat_id.title}]({chat_id.invite_link}) telah ditambahkan di list POST")
            else:
                await message.reply("Gagal menambahkan Channel ke lis POST")
                
                
    @app.on_message(filters.command("getpost"))                    
    async def get_post(_, message: Message):                    
        msg = "<b>LIST CHANNEL POST</b>\n\n"
        count = 0    
        served_chats = []
        all_list = await mongo.get_served_chats()
        for chat in all_list:
            served_chats.append(int(chat["chat_id"]))    
        if not all_list:
            await message.reply("Tidak ada list channel yang tersimpan.</b>")
            return
        for list in served_chats:
            group_name = await app.get_chat(list)
            count += 1       
            msg += f"{count}. [{group_name.title}]({group_name.invite_link})\n\n"
        await message.reply(msg)
        
        
    @app.on_message(filters.command("delpost"))
    async def delete_post(_, message: Message):
        if message.reply_to_message:
            chat_id = message.reply_to_message.sender.chat.id
        else:
            if len(message.command) < 2:
                return await message.reply_text("Berikan username atau id channel.")
            chat_id = message.text.split()[1]
            if "@" in chat_id:
                chat_id = chat_id.replace("@", "")
            chat_id = await app.get_chat(chat_id)
            schats = await mongo.get_served_chats()
            if chat_id.id in schats:
                return await message.reply_text(
                    "Channel ini sudah masuk di list POST",
            )
            added = await mongo.delete_served_chat(chat_id.id)
            if added:
                await message.reply_text(f"Berhasil Channel [{chat_id.title}]({chat_id.invite_link}) telah dihapus dari list POST")
            else:
                await message.reply("Gagal menghapus Channel dari list POST")        
        
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
        text = f"""📊 **Statistik Bot:**
        
👤 Stats Pengguna: {served_users} Users
"""
        await message.reply_text(text)


    #Ini buat broadcastuser rex

    @app.on_message(
        filters.command("broadcast") & filters.user(SUDO_USERS)
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
                    "**Usage**:\n/broadcast [MESSAGE] or [Reply to a Message]"
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
                    "**Usage**:\n/post  [Text] atau [Balas ke pesan]"
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

        
    @app.on_message(filters.private)
    async def incoming_private(_, message):
        user_id = message.from_user.id
        if await mongo.is_banned_user(user_id):
            return
        if user_id in SUDO_USERS:
            if message.reply_to_message:
                if (
                    message.text == "/unblock"
                    or message.text == "/block"
                    or message.text == "/broadcast"
                ):
                    return
                replied_id = message.reply_to_message_id
                try:
                    replied_user_id = save[replied_id]
                except Exception as e:
                    print(e)
                    return await message.reply_text(
                        "Failed to fetch user. You might've restarted bot or some error happened. Please check logs"
                    )
                try:
                    return await app.copy_message(
                        replied_user_id,
                        message.chat.id,
                        message.id,
                    )
                except Exception as e:
                    print(e)
                    return await message.reply_text(
                        "Failed to send the message, User might have blocked the bot or something wrong happened. Please check logs"
                    )
        else:
            if await mongo.is_group():
                try:
                    forwarded = await app.forward_messages(
                        "-1001692951846",
                        message.chat.id,
                        message.id,
                    )
                    save[forwarded.id] = user_id
                except:
                    pass
            else:
                for user in SUDO_USERS:
                    try:
                        forwarded = await app.forward_messages(
                            user, message.chat.id, message.id
                        )
                        save[forwarded.id] = user_id
                    except:
                        pass

    @app.on_message(
        filters.group & filters.user(SUDO_USERS),
        group=grouplist,
    )
    async def incoming_groups(_, message):
        if message.reply_to_message:
            if (
                message.text == "/unblock"
                or message.text == "/block"
                or message.text == "/broadcast"
            ):
                return
            replied_id = message.reply_to_message_id
            try:
                replied_user_id = save[replied_id]
            except Exception as e:
                print(e)
                return await message.reply_text(
                    "Failed to fetch user. You might've restarted bot or some error happened. Please check logs"
                )
            try:
                return await app.copy_message(
                    replied_user_id,
                    message.chat.id,
                    message.id,
                )
            except Exception as e:
                print(e)
                return await message.reply_text(
                    "Failed to send the message, User might have blocked the bot or something wrong happened. Please check logs"
                )
                    
    print("[Bot Posting] - Bot Posting Started")
    await idle()


if __name__ == "__main__":
    loop.run_until_complete(init())
