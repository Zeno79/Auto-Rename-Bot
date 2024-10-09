import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db['users']  # Ensure proper collection reference

    def new_user(self, user_id):
        return {
            '_id': int(user_id),
            'file_id': None,
            'caption': None,
            'format_template': None,
            'media_type': None  # Default media type setting
        }

    async def add_user(self, bot, message):
        user_id = message.from_user.id
        if not await self.is_user_exist(user_id):
            user_data = self.new_user(user_id)
            await self.users.insert_one(user_data)
            await send_log(bot, message.from_user)

    async def is_user_exist(self, user_id):
        user = await self.users.find_one({'_id': int(user_id)})
        return bool(user)

    async def set_thumbnail(self, user_id, file_id):
        await self.users.update_one({'_id': int(user_id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, user_id):
        user = await self.users.find_one({'_id': int(user_id)})
        return user['file_id'] if user and 'file_id' in user else None

    async def set_caption(self, user_id, caption):
        await self.users.update_one({'_id': int(user_id)}, {'$set': {'caption': caption}})

    async def get_caption(self, user_id):
        user = await self.users.find_one({'_id': int(user_id)})
        return user['caption'] if user and 'caption' in user else None

    async def set_format_template(self, user_id, format_template):
        await self.users.update_one({'_id': int(user_id)}, {'$set': {'format_template': format_template}})

    async def get_format_template(self, user_id):
        user = await self.users.find_one({'_id': int(user_id)})
        return user['format_template'] if user and 'format_template' in user else None

    async def set_media_preference(self, user_id, media_type):
        await self.users.update_one({'_id': int(user_id)}, {'$set': {'media_type': media_type}})

    async def get_media_preference(self, user_id):
        user = await self.users.find_one({'_id': int(user_id)})
        return user['media_type'] if user and 'media_type' in user else None

    async def total_users_count(self):
        count = await self.users.count_documents({})
        return count

    async def get_all_users(self):
        return self.users.find({})

    async def delete_user(self, user_id):
        await self.users.delete_many({'_id': int(user_id)})

# Create a global instance of the Database class
madflixbotz = Database(Config.DB_URL, Config.DB_NAME)
