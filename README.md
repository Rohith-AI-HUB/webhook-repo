# GitHub Webhook Project

This project consists of two repositories that work together to capture GitHub events via webhooks and display them in a web interface.

## Project Overview

- **action-repo**: A GitHub repository configured with webhooks to send events
- **webhook-repo**: A Flask application that receives webhooks, stores data in MongoDB, and provides a UI

## Architecture

```
GitHub Repository (action-repo) 
    ↓ (webhook events)
Flask Webhook Endpoint (webhook-repo)
    ↓ (store events)
MongoDB Database
    ↓ (polling every 15s)
Web UI Dashboard
```

## Repository Structure

### webhook-repo Structure
```
webhook-repo/
├── app.py                 # Main Flask application
├── models.py             # MongoDB schema definitions
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css    # UI styling
│   └── js/
│       └── main.js      # Frontend JavaScript
├── templates/
│   └── index.html       # Main UI template
├── config.py            # Configuration settings
├── webhook_handler.py   # Webhook processing logic
└── README.md           # This file
```

### action-repo Structure
```
action-repo/
├── README.md           # Repository documentation
├── src/                # Sample source code
│   └── main.py        # Sample application
└── .github/           # GitHub Actions (optional)
    └── workflows/
        └── ci.yml     # Sample workflow
```

## Prerequisites (Windows)

### 1. Install Python 3.8+
- Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Verify installation: `python --version`

### 2. Install MongoDB
- Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
- Install with default settings
- MongoDB will run as a Windows service automatically

### 3. Install Git
- Download from [git-scm.com](https://git-scm.com/download/win)
- Use default installation options

### 4. Install ngrok (for local webhook testing)
- Download from [ngrok.com](https://ngrok.com/download)
- Extract to a folder in your PATH
- Sign up for free account and get auth token
- Run: `ngrok authtoken YOUR_AUTH_TOKEN`

## Setup Instructions

### Step 1: Create GitHub Repositories

1. **Create action-repo**:
   ```bash
   # Create new repository on GitHub named 'action-repo'
   git clone https://github.com/YOUR_USERNAME/action-repo.git
   cd action-repo
   
   # Add some initial files
   echo "# Action Repository" > README.md
   mkdir src
   echo "print('Hello World')" > src/main.py
   
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create webhook-repo**:
   ```bash
   # Create new repository on GitHub named 'webhook-repo'
   git clone https://github.com/YOUR_USERNAME/webhook-repo.git
   cd webhook-repo
   ```

### Step 2: Setup webhook-repo

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Create requirements.txt**:
   ```
   Flask==2.3.3
   pymongo==4.5.0
   python-dotenv==1.0.0
   requests==2.31.0
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create project files** (see file explanations below)

### Step 3: Configure MongoDB

1. **Start MongoDB service** (if not already running):
   ```bash
   net start MongoDB
   ```

2. **Verify MongoDB connection**:
   ```bash
   # Open MongoDB shell
   mongosh
   # Should connect successfully
   ```

### Step 4: Setup Webhook Endpoint

1. **Start your Flask application**:
   ```bash
   python app.py
   ```

2. **Expose local server using ngrok**:
   ```bash
   # In a new terminal
   ngrok http 5000
   ```
   Note the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 5: Configure GitHub Webhook

1. Go to your `action-repo` on GitHub
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `https://your-ngrok-url.ngrok.io/webhook`
   - **Content type**: `application/json`
   - **Events**: Select "Let me select individual events"
     - ✅ Pushes
     - ✅ Pull requests
   - **Active**: ✅ Checked

## File Explanations

### Core Application Files

#### `app.py` - Main Flask Application
```python
# Main entry point for the Flask application
# Sets up routes, initializes database connection
# Handles webhook endpoint and UI rendering
# Starts the development server
```

#### `webhook_handler.py` - Webhook Processing Logic
```python
# Processes incoming GitHub webhook payloads
# Extracts relevant information (author, branch, timestamp)
# Formats data according to specified requirements  
# Handles different event types (push, pull_request, merge)
```

#### `models.py` - MongoDB Schema Definitions
```python
# Defines database schema for storing webhook events
# Creates MongoDB collections and indexes
# Provides data access methods
# Handles database connections and operations
```

#### `config.py` - Configuration Settings
```python
# Contains application configuration
# Database connection strings
# Environment-specific settings
# Security configurations
```

### Frontend Files

#### `templates/index.html` - Main UI Template
```html
<!-- Main dashboard template -->
<!-- Displays webhook events in required format -->
<!-- Includes JavaScript for auto-refresh every 15 seconds -->
<!-- Clean and minimal design -->
```

#### `static/css/style.css` - UI Styling
```css
/* Clean and minimal styling for the dashboard */
/* Responsive design for different screen sizes */
/* Event type specific styling */
/* Loading and status indicators */
```

#### `static/js/main.js` - Frontend JavaScript
```javascript
// Handles auto-refresh functionality (15-second polling)
// Makes AJAX calls to fetch latest events
// Updates UI dynamically without page reload
// Handles error states and loading indicators
```

## Expected Event Formats

### Push Events
**Format**: `{author} pushed to {to_branch} on {timestamp}`  
**Example**: "Travis pushed to staging on 1st April 2021 - 9:30 PM UTC"

### Pull Request Events
**Format**: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`  
**Example**: "Travis submitted a pull request from staging to master on 1st April 2021 - 9:00 AM UTC"

### Merge Events (Bonus)
**Format**: `{author} merged branch {from_branch} to {to_branch} on {timestamp}`  
**Example**: "Travis merged branch dev to master on 2nd April 2021 - 12:00 PM UTC"

## MongoDB Schema

```javascript
{
  "_id": ObjectId,
  "event_type": "push" | "pull_request" | "merge",
  "author": "string",
  "from_branch": "string",      // null for push events
  "to_branch": "string",
  "timestamp": ISODate,
  "repository": "string",
  "raw_payload": {}             // Original GitHub payload
}
```

## Testing the Application

### 1. Test Webhook Endpoint
```bash
# Send test POST request
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 2. Test Database Connection
```bash
# Check if events are being stored
mongosh
use webhook_db
db.events.find()
```

### 3. Test UI Polling
- Open browser to `http://localhost:5000`
- Verify events appear automatically
- Check browser console for any errors

## Troubleshooting

### Common Issues on Windows

1. **MongoDB won't start**:
   ```bash
   # Check if service is running
   sc query MongoDB
   # Start service manually
   net start MongoDB
   ```

2. **Python virtual environment issues**:
   ```bash
   # Use full path if activation fails
   C:\path\to\your\project\venv\Scripts\activate.bat
   ```

3. **Port already in use**:
   ```bash
   # Find process using port 5000
   netstat -ano | findstr :5000
   # Kill process (replace PID)
   taskkill /PID <PID> /F
   ```

4. **ngrok connection issues**:
   - Ensure you're using the HTTPS URL
   - Check if ngrok is authenticated
   - Verify firewall isn't blocking connections

## Deployment Considerations

For production deployment:
- Use environment variables for sensitive configuration
- Set up proper MongoDB authentication
- Use a production WSGI server (gunicorn)
- Implement proper logging and error handling
- Set up SSL certificates for webhook endpoint

## Development Workflow

1. Make changes to code
2. Test locally with ngrok
3. Trigger events on action-repo (push, PR)
4. Verify events appear in UI
5. Check MongoDB for proper data storage
6. Commit and push changes

## Submission

Provide the following repository links:
- **action-repo**: `https://github.com/YOUR_USERNAME/action-repo`
- **webhook-repo**: `https://github.com/YOUR_USERNAME/webhook-repo`

Make sure both repositories are public and contain all necessary code and documentation.