#!/usr/bin/env python3
import requests
import json
import argparse
import sys

def send_notification(workflow_id, status, details=None):
    """
    Send a notification to the notification service.
    
    Args:
        workflow_id: The ID of the workflow
        status: The status of the workflow (e.g., 'started', 'completed', 'failed')
        details: Additional details about the workflow (optional)
    """
    url = "http://localhost:8765/send-workflow-notification"
    
    # Prepare notification data
    data = {
        "workflow_id": workflow_id,
        "status": status
    }
    
    # Add details if provided
    if details:
        data["details"] = details
    
    # Send the notification
    try:
        response = requests.post(url, json=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Notification sent successfully: {response.json()}")
        else:
            print(f"Error sending notification: {response.status_code} - {response.text}")
            return False
        
        return True
    
    except Exception as e:
        print(f"Exception sending notification: {str(e)}")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Send a notification to the notification service")
    parser.add_argument("workflow_id", help="The ID of the workflow")
    parser.add_argument("status", choices=["started", "in_progress", "completed", "failed"], 
                        help="The status of the workflow")
    parser.add_argument("--details", help="Additional details about the workflow (JSON string)")
    
    args = parser.parse_args()
    
    # Parse details if provided
    details = None
    if args.details:
        try:
            details = json.loads(args.details)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in details: {args.details}")
            sys.exit(1)
    
    # Send the notification
    success = send_notification(args.workflow_id, args.status, details)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)