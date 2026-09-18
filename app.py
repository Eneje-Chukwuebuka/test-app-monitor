#!/usr/bin/env python3
"""
Simple Test Application for Monitoring
Demonstrates health checks, crash handling, and logging
"""

from flask import Flask, jsonify
import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Track app state
app_state = {
    'healthy': True,
    'start_time': datetime.now(),
    'request_count': 0
}

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    Monitor uses this to check if app is running
    """
    app_state['request_count'] += 1
    
    if app_state['healthy']:
        logger.info("Health check: OK")
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - app_state['start_time']).total_seconds()
        }), 200
    else:
        logger.warning("Health check: UNHEALTHY")
        return jsonify({'status': 'unhealthy'}), 503

@app.route('/status', methods=['GET'])
def status():
    """
    Detailed status endpoint
    Returns app information
    """
    uptime = (datetime.now() - app_state['start_time']).total_seconds()
    
    status_info = {
        'status': 'healthy' if app_state['healthy'] else 'unhealthy',
        'uptime_seconds': uptime,
        'start_time': app_state['start_time'].isoformat(),
        'requests_processed': app_state['request_count'],
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Status request: {status_info}")
    return jsonify(status_info), 200

@app.route('/crash', methods=['GET'])
def crash():
    """
    Intentional crash endpoint
    Used for testing monitoring and alerting
    """
    logger.critical("CRASH endpoint called - shutting down!")
    
    # Respond to the request first
    response = jsonify({'status': 'crashing'})
    
    # Then crash the app
    os.kill(os.getpid(), 9)
    
    return response, 500

@app.errorhandler(404)
def not_found(error):
    """Handle undefined routes"""
    logger.warning(f"404 Not Found: {error}")
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle server errors"""
    logger.error(f"500 Server Error: {error}")
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Test App Starting")
    logger.info("Listening on 0.0.0.0:4000")
    logger.info("=" * 50)
    
    # Run Flask app
    # debug=False for production-like behavior
    # host='0.0.0.0' to listen on all interfaces
    app.run(
        host='0.0.0.0',
        port=4000,
        debug=False
    )
