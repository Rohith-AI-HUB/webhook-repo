from flask import Flask, request, jsonify, render_template
from models import WebhookEvent, init_db
from webhook_handler import process_webhook
import json
from datetime import datetime

app = Flask(__name__)

# Initialize database
init_db()

@app.route('/')
def index():
    """Main dashboard route"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint to receive GitHub events"""
    try:
        # Get the GitHub event type from headers
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        
        # Get the payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No payload received'}), 400
        
        # Process the webhook event
        processed_event = process_webhook(event_type, payload)
        
        if processed_event:
            # Store in database
            event = WebhookEvent(
                event_type=processed_event['event_type'],
                author=processed_event['author'],
                from_branch=processed_event.get('from_branch'),
                to_branch=processed_event['to_branch'],
                timestamp=processed_event['timestamp'],
                repository=processed_event['repository'],
                raw_payload=payload
            )
            event.save()
            
            print(f"Processed {event_type} event from {processed_event['author']}")
            return jsonify({'status': 'success', 'message': 'Webhook processed'}), 200
        else:
            print(f"Ignored {event_type} event - not supported")
            return jsonify({'status': 'ignored', 'message': 'Event type not supported'}), 200
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/events')
def get_events():
    """API endpoint to get recent events for the UI"""
    try:
        events = WebhookEvent.get_recent_events(limit=50)
        events_data = []
        
        for event in events:
            events_data.append({
                '_id': str(event['_id']),
                'event_type': event['event_type'],
                'author': event['author'],
                'from_branch': event.get('from_branch'),
                'to_branch': event['to_branch'],
                'timestamp': event['timestamp'].isoformat(),
                'repository': event['repository']
            })
        
        # Return in the format expected by the frontend
        return jsonify({
            'success': True,
            'events': events_data,
            'count': len(events_data)
        })
        
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'events': []
        }), 500
def format_timestamp(timestamp):
    """Format timestamp according to requirements"""
    # Convert to required format: "1st April 2021 - 9:30 PM UTC"
    day = timestamp.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    formatted = timestamp.strftime(f"{day}{suffix} %B %Y - %I:%M %p UTC")
    return formatted

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("Starting webhook server...")
    print("Dashboard available at: http://localhost:5000")
    print("Webhook endpoint: http://localhost:5000/webhook")
    app.run(debug=True, host='0.0.0.0', port=5000)