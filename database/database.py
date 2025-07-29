import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.users_collection = None
        self.settings_collection = None
        self.jobs_collection = None
        self._connection_lock = asyncio.Lock()
        self._connected = False

    async def connect(self):
        """Establish connection to MongoDB"""
        async with self._connection_lock:
            if self._connected:
                return True
                
            try:
                self.client = AsyncIOMotorClient(
                    Config.DB_URI,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000,
                    maxPoolSize=10,
                    minPoolSize=1
                )
                
                # Test the connection
                await self.client.admin.command('ping')
                
                self.db = self.client[Config.DB_NAME]
                self.users_collection = self.db.users
                self.settings_collection = self.db.settings  
                self.jobs_collection = self.db.jobs
                
                self._connected = True
                logger.info("Successfully connected to MongoDB")
                return True
                
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error connecting to MongoDB: {e}")
                return False

    async def setup(self):
        """Initialize database connection and create indexes"""
        if not await self.connect():
            logger.error("Failed to setup database connection")
            return False
            
        try:
            # Create indexes for better performance
            await self.users_collection.create_index("user_id", unique=True)
            await self.settings_collection.create_index("user_id", unique=True)
            await self.jobs_collection.create_index("job_id", unique=True)
            await self.jobs_collection.create_index("user_id")
            await self.jobs_collection.create_index("status")
            
            logger.info("Database indexes created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up database indexes: {e}")
            return False

    async def _ensure_connected(self):
        """Ensure database connection is active"""
        if not self._connected:
            await self.connect()

    async def put_video(self, user_id: int, vid_name: str, filename: str):
        """Store or update video information for a user"""
        await self._ensure_connected()
        
        try:
            user_data = {
                "user_id": user_id,
                "vid_name": vid_name,
                "filename": filename,
                "updated_at": datetime.utcnow()
            }
            
            # Check if user exists
            existing_user = await self.users_collection.find_one({"user_id": user_id})
            
            if existing_user:
                # Update existing user
                await self.users_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "vid_name": vid_name,
                            "filename": filename,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            else:
                # Create new user record
                user_data["created_at"] = datetime.utcnow()
                user_data["sub_name"] = None
                await self.users_collection.insert_one(user_data)
                
            logger.debug(f"Video info saved for user {user_id}: {vid_name}")
            
        except Exception as e:
            logger.error(f"Error saving video info for user {user_id}: {e}")

    async def put_sub(self, user_id: int, sub_name: str):
        """Store or update subtitle information for a user"""
        await self._ensure_connected()
        
        try:
            # Check if user exists
            existing_user = await self.users_collection.find_one({"user_id": user_id})
            
            if existing_user:
                # Update existing user
                await self.users_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "sub_name": sub_name,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            else:
                # Create new user record
                user_data = {
                    "user_id": user_id,
                    "vid_name": None,
                    "sub_name": sub_name,
                    "filename": None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await self.users_collection.insert_one(user_data)
                
            logger.debug(f"Subtitle info saved for user {user_id}: {sub_name}")
            
        except Exception as e:
            logger.error(f"Error saving subtitle info for user {user_id}: {e}")

    async def check_sub(self, user_id: int) -> bool:
        """Check if user has subtitle file"""
        await self._ensure_connected()
        
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if user and user.get("sub_name"):
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error checking subtitle for user {user_id}: {e}")
            return False

    async def check_video(self, user_id: int) -> bool:
        """Check if user has video file"""
        await self._ensure_connected()
        
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if user and user.get("vid_name"):
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error checking video for user {user_id}: {e}")
            return False

    async def get_vid_filename(self, user_id: int) -> Optional[str]:
        """Get video filename for user"""
        await self._ensure_connected()
        
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if user:
                return user.get("vid_name")
            return None
            
        except Exception as e:
            logger.error(f"Error getting video filename for user {user_id}: {e}")
            return None

    async def get_sub_filename(self, user_id: int) -> Optional[str]:
        """Get subtitle filename for user"""
        await self._ensure_connected()
        
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if user:
                return user.get("sub_name")
            return None
            
        except Exception as e:
            logger.error(f"Error getting subtitle filename for user {user_id}: {e}")
            return None

    async def get_filename(self, user_id: int) -> Optional[str]:
        """Get output filename for user"""
        await self._ensure_connected()
        
        try:
            user = await self.users_collection.find_one({"user_id": user_id})
            if user:
                return user.get("filename")
            return None
            
        except Exception as e:
            logger.error(f"Error getting filename for user {user_id}: {e}")
            return None

    async def erase(self, user_id: int) -> bool:
        """Remove user session data"""
        await self._ensure_connected()
        
        try:
            result = await self.users_collection.delete_one({"user_id": user_id})
            if result.deleted_count > 0:
                logger.debug(f"User session erased for user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error erasing user session for user {user_id}: {e}")
            return False

    # Settings Management Methods
    async def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user settings"""
        await self._ensure_connected()
        
        try:
            settings = await self.settings_collection.find_one({"user_id": user_id})
            if settings:
                # Remove MongoDB _id field
                settings.pop("_id", None)
                settings.pop("user_id", None)
                return settings
            return {}
            
        except Exception as e:
            logger.error(f"Error getting settings for user {user_id}: {e}")
            return {}

    async def set_user_setting(self, user_id: int, key: str, value: Any):
        """Set a specific user setting"""
        await self._ensure_connected()
        
        try:
            await self.settings_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        key: value,
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            logger.debug(f"Setting {key}={value} saved for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error setting {key} for user {user_id}: {e}")

    # Job Management Methods
    async def create_job(self, job_id: str, user_id: int, mode: str, status: str = "pending") -> bool:
        """Create a new job record"""
        await self._ensure_connected()
        
        try:
            job_data = {
                "job_id": job_id,
                "user_id": user_id,
                "mode": mode,
                "status": status,
                "created_at": datetime.utcnow()
            }
            
            await self.jobs_collection.insert_one(job_data)
            logger.debug(f"Job {job_id} created for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating job {job_id}: {e}")
            return False

    async def update_job_status(self, job_id: str, status: str):
        """Update job status"""
        await self._ensure_connected()
        
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if status in ["completed", "failed"]:
                update_data["completed_at"] = datetime.utcnow()
                
            await self.jobs_collection.update_one(
                {"job_id": job_id},
                {"$set": update_data}
            )
            logger.debug(f"Job {job_id} status updated to {status}")
            
        except Exception as e:
            logger.error(f"Error updating job {job_id} status: {e}")

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information"""
        await self._ensure_connected()
        
        try:
            job = await self.jobs_collection.find_one({"job_id": job_id})
            if job:
                job.pop("_id", None)  # Remove MongoDB _id field
                return job
            return None
            
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}")
            return None

    async def get_user_jobs(self, user_id: int, status: Optional[str] = None) -> list:
        """Get all jobs for a user, optionally filtered by status"""
        await self._ensure_connected()
        
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status
                
            cursor = self.jobs_collection.find(query).sort("created_at", -1)
            jobs = await cursor.to_list(length=100)
            
            # Remove MongoDB _id fields
            for job in jobs:
                job.pop("_id", None)
                
            return jobs
            
        except Exception as e:
            logger.error(f"Error getting jobs for user {user_id}: {e}")
            return []

    async def cleanup_old_jobs(self, days: int = 7):
        """Clean up old completed/failed jobs"""
        await self._ensure_connected()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await self.jobs_collection.delete_many({
                "status": {"$in": ["completed", "failed"]},
                "completed_at": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up {result.deleted_count} old jobs")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {e}")
            return 0

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Database connection closed")

    # Compatibility methods to maintain interface with existing code
    def check_sub_sync(self, user_id: int) -> bool:
        """Synchronous wrapper for check_sub (for compatibility)"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.check_sub(user_id))
        except:
            return False

    def check_video_sync(self, user_id: int) -> bool:
        """Synchronous wrapper for check_video (for compatibility)"""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.check_video(user_id))
        except:
            return False

# Global database instance
db_instance = None

async def get_database():
    """Get database instance (singleton pattern)"""
    global db_instance
    if db_instance is None:
        db_instance = Database()
        await db_instance.setup()
    return db_instance
