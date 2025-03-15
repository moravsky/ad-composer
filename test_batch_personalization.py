#!/usr/bin/env python3
"""
Test script for the batch personalization API.
"""
import requests
import json
import psycopg2
import time

# Database connection parameters
DB_PARAMS = {
    "host": "localhost",
    "port": 5433,  # From docker-compose.yml, the exposed port is 5433
    "database": "addb",
    "user": "ad_user",
    "password": "your_secure_password"
}

# API endpoint
API_URL = "http://localhost:8001/api/batch-personalize/"

def get_company_info_id(cursor, company_name="Stampli"):
    """Get the company_info ID for the given company name."""
    cursor.execute("SELECT id FROM company_info WHERE company_name = %s", (company_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        raise ValueError(f"Company '{company_name}' not found in the database")

def get_account_ids(cursor):
    """Get all account IDs and names from the database."""
    cursor.execute("SELECT id, name FROM accounts")
    return {row[1]: row[0] for row in cursor.fetchall()}

def check_personalized_content(cursor, company_info_id, target_account_id):
    """Check if personalized content exists for the given company and target account."""
    cursor.execute(
        """
        SELECT id, original_text, personalized_text, text_type, created_at
        FROM personalized_content
        WHERE company_info_id = %s AND target_account_id = %s
        ORDER BY created_at DESC
        """,
        (company_info_id, target_account_id)
    )
    results = cursor.fetchall()
    return results

def test_batch_personalization():
    """Test the batch personalization API."""
    # Connect to the database
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    
    try:
        # Get the company_info ID
        company_info_id = get_company_info_id(cursor)
        print(f"Found company_info ID: {company_info_id}")
        
        # Get account IDs
        account_ids = get_account_ids(cursor)
        print(f"Found account IDs: {account_ids}")
        
        # Check if we have the accounts we want to test with
        if "YMCA" not in account_ids:
            print("Warning: YMCA account not found in the database")
        if "Pappas Restaurants" not in account_ids:
            print("Warning: Pappas Restaurants account not found in the database")
        
        # Use the first two accounts if our expected ones aren't available
        test_accounts = list(account_ids.items())[:2]
        print(f"Using accounts for testing: {test_accounts}")
        
        # Create test data with the correct IDs
        test_data = {
            "jobs": [
                {
                    "company_info_id": company_info_id,
                    "target_account_id": test_accounts[0][1],  # First account ID
                    "personalization_target": {
                        "type": "product_overview",
                        "text": "Stampli is the only AP automation solution that's purpose-built for Accounts Payable. It centers all communication, documentation, and workflows on top of each invoice, eliminating the need for workarounds, external communications channels, 3rd-party solutions, or manual AP work inside the ERP."
                    }
                },
                {
                    "company_info_id": company_info_id,
                    "target_account_id": test_accounts[1][1],  # Second account ID
                    "personalization_target": {
                        "type": "differentiators",
                        "text": "Least disruption: No need to rework your ERP or change your AP processes.\n\nMost control: One place for all your communication, documentation, and workflows.\n\nSmartest AI: Billy the Bot assists you across the entire invoice process — and he's always learning."
                    }
                }
            ]
        }
        
        # Check if personalized content already exists
        print("\nChecking for existing personalized content...")
        for i, (account_name, account_id) in enumerate(test_accounts):
            results = check_personalized_content(cursor, company_info_id, account_id)
            if results:
                print(f"Found {len(results)} personalized content entries for {account_name}:")
                for result in results:
                    print(f"  ID: {result[0]}")
                    print(f"  Type: {result[3]}")
                    print(f"  Created at: {result[4]}")
                    print(f"  Original text: {result[1][:100]}...")
                    print(f"  Personalized text: {result[2][:100]}...")
                    print()
            else:
                print(f"No personalized content found for {account_name}")
        
        # Ask user if they want to send a new request
        user_input = input("\nDo you want to send a new batch personalization request? (y/n): ")
        if user_input.lower() != 'y':
            print("Exiting without sending a new request.")
            return
        
        print(f"\nSending request to {API_URL}...")
        print(f"Request data: {json.dumps(test_data, indent=2)}")
        
        # Send the request
        response = requests.post(API_URL, json=test_data)
        
        # Check the response
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(f"Response data: {json.dumps(response.json(), indent=2)}")
            
            # Get the workflow ID from the response
            workflow_id = response.json().get("workflow_id")
            if workflow_id:
                print(f"\nWorkflow started with ID: {workflow_id}")
                print(f"You can check the status in the Temporal UI: http://localhost:8080/namespaces/default/workflows/{workflow_id}")
                
                # Wait for the workflow to complete
                print("\nWaiting for the workflow to complete (10 seconds)...")
                time.sleep(10)
                
                # Check for new personalized content
                print("\nChecking for new personalized content...")
                for i, (account_name, account_id) in enumerate(test_accounts):
                    results = check_personalized_content(cursor, company_info_id, account_id)
                    if results:
                        print(f"Found {len(results)} personalized content entries for {account_name}:")
                        for result in results:
                            print(f"  ID: {result[0]}")
                            print(f"  Type: {result[3]}")
                            print(f"  Created at: {result[4]}")
                            print(f"  Original text: {result[1][:100]}...")
                            print(f"  Personalized text: {result[2][:100]}...")
                            print()
                    else:
                        print(f"No personalized content found for {account_name}")
        else:
            print(f"Error: {response.text}")
    
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_batch_personalization()