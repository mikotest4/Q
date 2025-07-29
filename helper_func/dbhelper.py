import motor.motor_asyncio
import asyncio
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(Config.DB_URI)
        self.db = self.client[Config.DB_NAME]
        self.users_collection = self.db['users']
        
    def setup(self):
        """Setup database connection"""
        try:
            # Test the connection
            asyncio.create_task(self.test_connection())
            logger.info("Database connection established successfully")
            return self
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    
    async def test_connection(self):
        """Test database connection"""
        try:
            await self.client.admin.command('ping')
            logger.info("Database ping successful")
        except Exception as e:
            logger.error(f"Database ping failed: {e}")
    
    async def add_user(self, user_id):
        """Add a new user to the database"""
        try:
            user_data = {
                'user_id': int(user_id),
                'created_at': asyncio.get_event_loop().time()
            }
            
            # Insert user if not exists
            await self.users_collection.update_one(
                {'user_id': int(user_id)},
                {'$setOnInsert': user_data},
                upsert=True
            )
            logger.info(f"User {user_id} added/updated in database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id):
        """Get user from database"""
        try:
            user = await self.users_collection.find_one({'user_id': int(user_id)})
            return user
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_all_users(self):
        """Get all users from database"""
        try:
            users = []
            cursor = self.users_collection.find({})
            async for user in cursor:
                users.append(user)
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def delete_user(self, user_id):
        """Delete user from database"""
        try:
            result = await self.users_collection.delete_one({'user_id': int(user_id)})
            if result.deleted_count > 0:
                logger.info(f"User {user_id} deleted from database")
                return True
            else:
                logger.warning(f"User {user_id} not found in database")
                return False
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    async def get_user_count(self):
        """Get total number of users"""
        try:
            count = await self.users_collection.count_documents({})
            return count
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    async def is_user_exists(self, user_id):
        """Check if user exists in database"""
        try:
            user = await self.users_collection.find_one({'user_id': int(user_id)})
            return user is not None
        except Exception as e:
            logger.error(f"Error checking user existence {user_id}: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        try:
            self.client.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
