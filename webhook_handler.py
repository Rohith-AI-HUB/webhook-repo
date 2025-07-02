from datetime import datetime
import json

def process_webhook(event_type, payload):
    """
    Process GitHub webhook payloads and extract relevant information
    
    Args:
        event_type (str): GitHub event type from X-GitHub-Event header
        payload (dict): GitHub webhook payload
    
    Returns:
        dict: Processed event data or None if event should be ignored
    """
    
    if event_type == 'push':
        return process_push_event(payload)
    elif event_type == 'pull_request':
        return process_pull_request_event(payload)
    else:
        # Ignore other event types
        return None

def process_push_event(payload):
    """Process GitHub push events"""
    try:
        # Extract information from push payload
        author = payload['pusher']['name']
        repository = payload['repository']['full_name']
        ref = payload['ref']  # refs/heads/branch_name
        
        # Extract branch name from ref
        to_branch = ref.split('/')[-1] if ref.startswith('refs/heads/') else ref
        
        # Get timestamp
        timestamp = datetime.now()  # GitHub doesn't provide exact push time in payload
        
        # Use head commit timestamp if available
        if payload.get('head_commit') and payload['head_commit'].get('timestamp'):
            timestamp = datetime.fromisoformat(payload['head_commit']['timestamp'].replace('Z', '+00:00'))
        
        return {
            'event_type': 'push',
            'author': author,
            'from_branch': None,  # Push events don't have from_branch
            'to_branch': to_branch,
            'timestamp': timestamp,
            'repository': repository
        }
        
    except KeyError as e:
        print(f"Error processing push event - missing key: {e}")
        return None
    except Exception as e:
        print(f"Error processing push event: {e}")
        return None

def process_pull_request_event(payload):
    """Process GitHub pull request events"""
    try:
        action = payload['action']
        
        # Only process specific PR actions
        if action in ['opened', 'reopened']:
            event_type = 'pull_request'
        elif action == 'closed' and payload['pull_request'].get('merged'):
            event_type = 'merge'
        else:
            # Ignore other PR actions (synchronize, edited, etc.)
            return None
        
        # Extract information from PR payload
        pr = payload['pull_request']
        author = pr['user']['login']
        repository = payload['repository']['full_name']
        from_branch = pr['head']['ref']
        to_branch = pr['base']['ref']
        
        # Get timestamp based on action
        if event_type == 'merge':
            # Use merged_at timestamp for merge events
            timestamp_str = pr.get('merged_at') or pr['updated_at']
        else:
            # Use created_at for new PRs
            timestamp_str = pr['created_at']
        
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        return {
            'event_type': event_type,
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp,
            'repository': repository
        }
        
    except KeyError as e:
        print(f"Error processing pull request event - missing key: {e}")
        return None
    except Exception as e:
        print(f"Error processing pull request event: {e}")
        return None

def validate_payload(payload):
    """Validate that the payload contains required fields"""
    if not isinstance(payload, dict):
        return False
    
    # Basic validation - ensure we have a repository
    if 'repository' not in payload:
        return False
    
    return True

def extract_common_info(payload):
    """Extract common information present in all GitHub webhooks"""
    try:
        return {
            'repository': payload['repository']['full_name'],
            'repository_id': payload['repository']['id'],
            'sender': payload['sender']['login']
        }
    except KeyError:
        return None