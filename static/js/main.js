// GitHub Webhook Dashboard - Frontend JavaScript
// Compatible with existing index.html structure

class WebhookDashboard {
    constructor() {
        this.refreshInterval = 15000; // 15 seconds
        this.intervalId = null;
        this.isLoading = false;
        this.lastUpdateTime = null;
        this.eventCounts = {
            total: 0,
            push: 0,
            pull_request: 0,
            merge: 0
        };
        
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupDashboard());
        } else {
            this.setupDashboard();
        }
    }

    setupDashboard() {
        // Get DOM elements
        this.elements = {
            statusDot: document.getElementById('status-dot'),
            statusText: document.getElementById('status-text'),
            loading: document.getElementById('loading'),
            emptyState: document.getElementById('empty-state'),
            eventsList: document.getElementById('events-list'),
            manualRefresh: document.getElementById('manual-refresh'),
            lastUpdated: document.getElementById('last-updated'),
            totalCount: document.getElementById('total-count'),
            pushCount: document.getElementById('push-count'),
            prCount: document.getElementById('pr-count'),
            mergeCount: document.getElementById('merge-count'),
            eventTemplate: document.getElementById('event-template')
        };
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load initial data
        this.loadEvents();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        // Handle page visibility changes
        this.handleVisibilityChange();
    }

    setupEventListeners() {
        // Manual refresh button
        if (this.elements.manualRefresh) {
            this.elements.manualRefresh.addEventListener('click', () => {
                this.loadEvents(true);
            });
        }
    }

    async loadEvents(forceRefresh = false) {
        if (this.isLoading && !forceRefresh) return;
        
        this.isLoading = true;
        this.showLoading();
        this.updateStatus('connecting', 'Fetching events...');

        try {
            const response = await fetch('/api/events', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayEvents(data.events || []);
            this.updateStatus('online', 'Connected');
            this.updateEventCounts(data.events || []);
            this.lastUpdateTime = new Date();
            
        } catch (error) {
            console.error('Error loading events:', error);
            this.handleError(error);
            this.updateStatus('error', 'Connection failed');
        } finally {
            this.isLoading = false;
            this.hideLoading();
            this.updateLastUpdateTime();
        }
    }

    displayEvents(events) {
        const eventsList = this.elements.eventsList;
        const emptyState = this.elements.emptyState;

        if (!eventsList) return;

        if (events.length === 0) {
            eventsList.innerHTML = '';
            if (emptyState) {
                emptyState.style.display = 'block';
            }
            return;
        }

        if (emptyState) {
            emptyState.style.display = 'none';
        }

        // Sort events by timestamp (most recent first)
        const sortedEvents = events.sort((a, b) => 
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        // Clear existing events
        eventsList.innerHTML = '';

        // Create event elements
        sortedEvents.forEach((event, index) => {
            const eventElement = this.createEventElement(event);
            if (eventElement) {
                // Add staggered animation - handle both DocumentFragment and Element
                if (eventElement.style) {
                    eventElement.style.animationDelay = `${index * 0.1}s`;
                } else if (eventElement.firstElementChild) {
                    eventElement.firstElementChild.style.animationDelay = `${index * 0.1}s`;
                }
                eventsList.appendChild(eventElement);
            }
        });
    }

    createEventElement(event) {
        const template = this.elements.eventTemplate;
        if (!template) {
            // Fallback if template doesn't exist
            return this.createEventElementFallback(event);
        }

        const eventElement = template.content.cloneNode(true);
        const eventItem = eventElement.querySelector('.event-item');
        
        if (!eventItem) return this.createEventElementFallback(event);

        // Add event type class
        eventItem.classList.add(`event-${event.event_type}`);
        eventItem.setAttribute('data-event-id', event._id || '');

        // Set event icon and badge
        const badge = eventElement.querySelector('.event-type-badge');
        if (badge) {
            badge.textContent = this.getEventIcon(event.event_type);
            badge.classList.add(`badge-${event.event_type}`);
        }

        // Set event message
        const message = eventElement.querySelector('.event-message');
        if (message) {
            message.textContent = this.formatEventMessage(event);
        }

        // Set repository name
        const repo = eventElement.querySelector('.event-repo');
        if (repo && event.repository) {
            repo.textContent = event.repository;
        }

        // Set timestamp
        const time = eventElement.querySelector('.event-time');
        if (time) {
            time.textContent = this.formatTimestamp(event.timestamp);
            time.setAttribute('title', new Date(event.timestamp).toLocaleString());
        }

        return eventElement;
    }

    createEventElementFallback(event) {
        const eventDiv = document.createElement('div');
        eventDiv.className = `event-item event-${event.event_type}`;
        eventDiv.setAttribute('data-event-id', event._id || '');
        
        eventDiv.innerHTML = `
            <div class="event-icon">
                <span class="event-type-badge badge-${event.event_type}">${this.getEventIcon(event.event_type)}</span>
            </div>
            <div class="event-content">
                <div class="event-message">${this.formatEventMessage(event)}</div>
                <div class="event-meta">
                    <span class="event-repo">${event.repository || ''}</span>
                    <span class="event-time" title="${new Date(event.timestamp).toLocaleString()}">
                        ${this.formatTimestamp(event.timestamp)}
                    </span>
                </div>
            </div>
        `;
        
        return eventDiv;
    }

    formatEventMessage(event) {
        const { event_type, author, from_branch, to_branch } = event;
        
        switch (event_type) {
            case 'push':
                return `${author} pushed to ${to_branch}`;
            case 'pull_request':
                return `${author} submitted a pull request from ${from_branch} to ${to_branch}`;
            case 'merge':
                return `${author} merged branch ${from_branch} to ${to_branch}`;
            default:
                return `${author} performed ${event_type} action`;
        }
    }

    getEventIcon(eventType) {
        const icons = {
            'push': '📤',
            'pull_request': '🔄',
            'merge': '🔀'
        };
        return icons[eventType] || '📋';
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        // Relative time for recent events
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        // Absolute time for older events
        const options = {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        return date.toLocaleDateString('en-US', options);
    }

    updateEventCounts(events) {
        // Reset counts
        this.eventCounts = {
            total: events.length,
            push: 0,
            pull_request: 0,
            merge: 0
        };

        // Count events by type
        events.forEach(event => {
            if (this.eventCounts.hasOwnProperty(event.event_type)) {
                this.eventCounts[event.event_type]++;
            }
        });

        // Update UI
        if (this.elements.totalCount) {
            this.elements.totalCount.textContent = this.eventCounts.total;
        }
        if (this.elements.pushCount) {
            this.elements.pushCount.textContent = this.eventCounts.push;
        }
        if (this.elements.prCount) {
            this.elements.prCount.textContent = this.eventCounts.pull_request;
        }
        if (this.elements.mergeCount) {
            this.elements.mergeCount.textContent = this.eventCounts.merge;
        }
    }

    showLoading() {
        if (this.elements.loading) {
            this.elements.loading.style.display = 'flex';
        }
        
        if (this.elements.manualRefresh) {
            this.elements.manualRefresh.disabled = true;
            this.elements.manualRefresh.textContent = 'Loading...';
        }
    }

    hideLoading() {
        if (this.elements.loading) {
            this.elements.loading.style.display = 'none';
        }
        
        if (this.elements.manualRefresh) {
            this.elements.manualRefresh.disabled = false;
            this.elements.manualRefresh.textContent = 'Refresh Now';
        }
    }

    updateStatus(status, message) {
        if (this.elements.statusDot) {
            this.elements.statusDot.className = `status-dot status-${status}`;
        }
        
        if (this.elements.statusText) {
            this.elements.statusText.textContent = message;
        }
    }

    updateLastUpdateTime() {
        if (this.elements.lastUpdated && this.lastUpdateTime) {
            const timeString = this.lastUpdateTime.toLocaleTimeString();
            this.elements.lastUpdated.textContent = timeString;
        }
    }

    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear any existing interval
        
        this.intervalId = setInterval(() => {
            if (!document.hidden) { // Only refresh if page is visible
                this.loadEvents();
            }
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    handleVisibilityChange() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoRefresh();
                this.updateStatus('paused', 'Auto-refresh paused');
            } else {
                this.startAutoRefresh();
                this.loadEvents(); // Refresh when page becomes visible
            }
        });
    }

    handleError(error) {
        console.error('Dashboard error:', error);
        
        // Show error in events list
        if (this.elements.eventsList) {
            this.elements.eventsList.innerHTML = `
                <div class="error-message">
                    <div class="error-icon">⚠️</div>
                    <h3>Connection Error</h3>
                    <p>Failed to load webhook events: ${error.message}</p>
                    <p>The server might be down or there could be a network issue.</p>
                    <button onclick="window.webhookDashboard.loadEvents(true)" class="btn-retry">
                        🔄 Try Again
                    </button>
                </div>
            `;
        }
        
        // Hide empty state
        if (this.elements.emptyState) {
            this.elements.emptyState.style.display = 'none';
        }
    }

    // Public methods
    refresh() {
        this.loadEvents(true);
    }

    getStatus() {
        return {
            isLoading: this.isLoading,
            lastUpdateTime: this.lastUpdateTime,
            refreshInterval: this.refreshInterval,
            isAutoRefreshActive: !!this.intervalId,
            eventCounts: this.eventCounts
        };
    }

    // Utility method to format events according to requirements
    formatEventForDisplay(event) {
        const timestamp = new Date(event.timestamp).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'UTC'
        }) + ' UTC';

        switch (event.event_type) {
            case 'push':
                return `${event.author} pushed to ${event.to_branch} on ${timestamp}`;
            case 'pull_request':
                return `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${timestamp}`;
            case 'merge':
                return `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${timestamp}`;
            default:
                return `${event.author} performed ${event.event_type} action on ${timestamp}`;
        }
    }
}

// Initialize dashboard when script loads
window.webhookDashboard = new WebhookDashboard();

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebhookDashboard;
}