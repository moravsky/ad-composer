import os
import logging
import socketio
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    await sio.emit('hello', {'message': f'Welcome to the notification service, user: {sid}!'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")
    # Note: We can't send a message to a disconnected client, but we log it for completeness

@sio.event
async def subscribe_workflow(sid, data):
    """
    Subscribe to a workflow by joining its room.
    """
    try:
        workflow_id = data.get('workflow_id')
        if not workflow_id:
            await sio.emit('error', {'message': 'Workflow ID is required'}, room=sid)
            return
        
        # Join workflow room
        room_name = f"workflow:{workflow_id}"
        await sio.enter_room(sid, room_name)
        logger.info(f"Client {sid} joined room {room_name}")
        
        await sio.emit('subscribed', {
            'status': 'success', 
            'workflow_id': workflow_id
        }, room=sid)
    
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        await sio.emit('error', {'message': f'Subscription failed: {str(e)}'}, room=sid)

@sio.event
async def unsubscribe_workflow(sid, data):
    """
    Unsubscribe from a workflow by leaving its room.
    """
    try:
        workflow_id = data.get('workflow_id')
        if not workflow_id:
            await sio.emit('error', {'message': 'Workflow ID is required'}, room=sid)
            return
        
        # Leave workflow room
        room_name = f"workflow:{workflow_id}"
        await sio.leave_room(sid, room_name)
        logger.info(f"Client {sid} left room {room_name}")
        
        await sio.emit('unsubscribed', {
            'status': 'success', 
            'workflow_id': workflow_id
        }, room=sid)
    
    except Exception as e:
        logger.error(f"Unsubscription error: {str(e)}")
        await sio.emit('error', {'message': f'Unsubscription failed: {str(e)}'}, room=sid)

# HTTP endpoint to send workflow notifications
async def send_workflow_notification(request):
    """
    Send a notification to all clients subscribed to a workflow.
    """
    try:
        data = await request.json()
        workflow_id = data.get('workflow_id')
        
        if not workflow_id:
            return web.json_response({'error': 'Workflow ID is required'}, status=400)
        
        # Send notification to all clients in the workflow room
        room_name = f"workflow:{workflow_id}"
        notification = {
            'type': 'workflow_update',
            'workflow_id': workflow_id,
            'data': data
        }
        
        await sio.emit('workflow_notification', notification, room=room_name)
        logger.info(f"Sent notification for workflow {workflow_id} to room {room_name}")
        
        return web.json_response({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return web.json_response({'error': str(e)}, status=500)

# Function to serve the test client HTML
async def serve_test_client(request):
    """
    Serve the test client HTML page.
    """
    try:
        with open('test_client.html', 'r') as file:
            html_content = file.read()
        return web.Response(text=html_content, content_type='text/html')
    except Exception as e:
        logger.error(f"Error serving test client: {str(e)}")
        return web.Response(text=f"Error: {str(e)}", status=500)

# Add HTTP routes
app.router.add_post('/send-workflow-notification', send_workflow_notification)
app.router.add_get('/test-client', serve_test_client)

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('WS_HOST', '0.0.0.0')
    port = int(os.getenv('WS_PORT', 8765))
    
    logger.info(f"Starting notification service on {host}:{port}")
    web.run_app(app, host=host, port=port)