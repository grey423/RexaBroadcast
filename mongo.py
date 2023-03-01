# Rexa si kadal gurun

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from config import MONGO_DB_URI

db = None

if MONGO_DB_URI != None:
    mongo = MongoClient(MONGO_DB_URI)
    db = mongo.RexaBot

    usersdb = db.users
    chatsdb = db.chats

    # Ini get Users nya om
    async def is_served_user(user_id: int) -> bool:
        user = await usersdb.find_one({"user_id": user_id})
        if not user:
            return False
        return True

    async def get_served_users() -> list:
        users_list = []
        async for user in usersdb.find({"user_id": {"$gt": 0}}):
            users_list.append(user)
        return users_list

    async def add_served_user(user_id: int):
        is_served = await is_served_user(user_id)
        if is_served:
            return
        return await usersdb.insert_one({"user_id": user_id})
 
   # Ini Get Chats nya om
    async def get_served_chats() -> list:
        chats_list = []
        async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
            chats_list.append(chat)
        return chats_list


    async def is_served_chat(chat_id: int) -> bool:
        chat = await chatsdb.find_one({"chat_id": chat_id})
        if not chat:
            return False
        return True


    async def add_served_chat(chat_id: int):
        is_served = await is_served_chat(chat_id)
        if is_served:
            await chatsdb.update_one(
                {"$set": {"chat_id": chat_id}},
            )
        else:
            await chatsdb.insert_one({"chat_id": chat_id})
    
    
    async def delete_served_chat(chat_id: int):
        await chatsdb.delete_one({"chat_id": chat_id})    

else:
    async def add_served_user(user_id: int):
        return True

    async def add_served_chat(chat_id: int):
        return True
    
    async def delete_served_chat(chat_id: int):
        return True
