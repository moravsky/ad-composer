#!/usr/bin/env python3
"""
Simple script to test Temporal connection.
Run this after starting the containers to verify that Temporal is working correctly.
"""
import asyncio
from temporalio.client import Client

async def main():
    # Connect to Temporal server
    print("Connecting to Temporal server...")
    client = await Client.connect("localhost:7233")
    
    # Get information about the server
    print("Connected successfully!")
    print(f"Temporal server namespace: {client.namespace}")
    print(f"Temporal server identity: {client.identity}")
    print("\nConnection test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())