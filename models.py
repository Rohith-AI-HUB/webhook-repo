from pymongo import MongoClient, DESCENDING
from datetime import datetime
import os

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'webhook_db')

# Global database connection
db = None
client = None

def init_db():
    """Initialize database connection"""
    global db, client
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        # Test connection
        client.admin.command('ping')
        print(f"Connected to MongoDB successfully: {DATABASE_NAME}")
        
        # Create indexes for better performance
        create_indexes()
        
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

def create_indexes():
    """Create database indexes for better query performance"""
    try:
        # Create compound index on timestamp (descending) and event_type
        db.events.create_index([
            ('timestamp', DESCENDING),
            ('event_type', 1)
        ])
        
        # Create index on repository for filtering
        db.events.create_index('repository')
        
        # Create index on author for filtering
        db.events.create_index('author')
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")

def get_db():
    """Get database connection"""
    global db
    if db is None:
        init_db()
    return db

class WebhookEvent:
    """Model class for webhook events"""
    
    def __init__(self, event_type, author, to_branch, timestamp, repository, 
                 from_branch=None, raw_payload=None):
        self.event_type = event_type
        self.author = author
        self.from_branch = from_branch
        self.to_branch = to_branch
        self.timestamp = timestamp
        self.repository = repository
        self.raw_payload = raw_payload or {}
        self.created_at = datetime.now()
    
    def save(self):
        """Save the event to MongoDB"""
        try:
            db = get_db()
            
            event_doc = {
                'event_type': self.event_type,
                'author': self.author,
                'from_branch': self.from_branch,
                'to_branch': self.to_branch,
                'timestamp': self.timestamp,
                'repository': self.repository,
                'raw_payload': self.raw_payload,
                'created_at': self.created_at
            }
            
            result = db.events.insert_one(event_doc)
            self._id = result.inserted_id
            print(f"Event saved with ID: {self._id}")
            return result.inserted_id
            
        except Exception as e:
            print(f"Error saving event: {e}")
            raise
    
    @staticmethod
    def get_recent_events(limit=50, event_type=None, repository=None):
        """
        Get recent webhook events from the database
        
        Args:
            limit (int): Maximum number of events to return
            event_type (str): Filter by event type (optional)
            repository (str): Filter by repository (optional)
        
        Returns:
            list: List of event documents
        """
        try:
            db = get_db()
            
            # Build query filter
            query_filter = {}
            if event_type:
                query_filter['event_type'] = event_type
            if repository:
                query_filter['repository'] = repository
            
            # Query events, sorted by timestamp (most recent first)
            events = list(db.events.find(query_filter)
                         .sort('timestamp', DESCENDING)
                         .limit(limit))
            
            return events
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    @staticmethod
    def get_event_counts():
        """Get counts of different event types"""
        try:
            db = get_db()
            
            pipeline = [
                {
                    '$group': {
                        '_id': '$event_type',
                        'count': {'$sum': 1}
                    }
                }
            ]
            
            results = list(db.events.aggregate(pipeline))
            
            # Convert to dictionary
            counts = {}
            for result in results:
                counts[result['_id']] = result['count']
            
            return counts
            
        except Exception as e:
            print(f"Error getting event counts: {e}")
            return {}
    
    @staticmethod
    def get_events_by_author(author, limit=20):
        """Get events by specific author"""
        try:
            db = get_db()
            
            events = list(db.events.find({'author': author})
                         .sort('timestamp', DESCENDING)
                         .limit(limit))
            
            return events
            
        except Exception as e:
            print(f"Error fetching events by author: {e}")
            return []
    
    @staticmethod
    def get_events_by_repository(repository, limit=20):
        """Get events by specific repository"""
        try:
            db = get_db()
            
            events = list(db.events.find({'repository': repository})
                         .sort('timestamp', DESCENDING)
                         .limit(limit))
            
            return events
            
        except Exception as e:
            print(f"Error fetching events by repository: {e}")
            return []
    
    @staticmethod
    def delete_old_events(days=30):
        """Delete events older than specified days"""
        try:
            db = get_db()
            
            cutoff_date = datetime.now().replace(day=datetime.now().day - days)
            
            result = db.events.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            print(f"Deleted {result.deleted_count} old events")
            return result.deleted_count
            
        except Exception as e:
            print(f"Error deleting old events: {e}")
            return 0
    
    @staticmethod
    def get_statistics():
        """Get basic statistics about stored events"""
        try:
            db = get_db()
            
            total_events = db.events.count_documents({})
            event_counts = WebhookEvent.get_event_counts()
            
            # Get most active authors
            pipeline = [
                {
                    '$group': {
                        '_id': '$author',
                        'event_count': {'$sum': 1}
                    }
                },
                {
                    '$sort': {'event_count': -1}
                },
                {
                    '$limit': 5
                }
            ]
            
            top_authors = list(db.events.aggregate(pipeline))
            
            return {
                'total_events': total_events,
                'event_type_counts': event_counts,
                'top_authors': top_authors
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}