#!/usr/bin/env python3
"""
Temporal worker for ad content generation workflows.
"""
import asyncio
import logging
import os
import yaml
from datetime import timedelta

from temporalio.client import Client
from temporalio.worker import Worker

from workflow.common_activities import load_config_activity
from workflow.ad_content_workflow import AdContentWorkflow
from workflow.target_workflow import TargetWorkflow
from workflow.target_activities import (
    get_company_info_activity,
    get_target_account_activity,
    get_contextual_information_activity,
    generate_personalized_content_activity,
    save_personalized_content_activity
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_config(config_file):
    """Load configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "config", config_file)
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def get_db_connection_params():
    """Get database connection parameters from environment variables."""
    return {
        "host": os.environ.get("DB_HOST", "db"),
        "port": os.environ.get("DB_PORT", "5432"),
        "dbname": os.environ.get("DB_NAME", "addb"),
        "user": os.environ.get("DB_USER", "ad_user"),
        "password": os.environ.get("DB_PASSWORD", "your_secure_password")
    }

async def main():
    # Load main workflow config
    config = load_config("ad_content_workflow_config.yaml")
    task_queue = config.get("task_queue", "ad-composer-task-queue")
    
    # Worker configuration
    max_concurrent_activities = config.get("max_concurrent_activities", 10)
    max_concurrent_workflows = config.get("max_concurrent_workflows", 5)
    
    # Get Temporal host from environment variable
    temporal_host = os.environ.get("TEMPORAL_HOST", "temporal:7233")
    
    # Connect to Temporal server
    logger.info(f"Connecting to Temporal server at {temporal_host}...")
    client = await Client.connect(temporal_host)
    logger.info(f"Connected to Temporal server: {client.identity}")
    
    # Create worker with concurrency settings
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[AdContentWorkflow, TargetWorkflow],
        activities=[
            load_config_activity,
            get_company_info_activity,
            get_target_account_activity,
            get_contextual_information_activity,
            generate_personalized_content_activity,
            save_personalized_content_activity
        ],
        max_concurrent_activities=max_concurrent_activities,
        max_concurrent_workflow_tasks=max_concurrent_workflows
    )
    
    # Log database connection info (without password)
    db_params = get_db_connection_params()
    logger.info(f"Database connection: host={db_params['host']}, port={db_params['port']}, dbname={db_params['dbname']}, user={db_params['user']}")
    
    logger.info(f"Starting worker on task queue: {task_queue}")
    logger.info(f"Max concurrent activities: {max_concurrent_activities}")
    logger.info(f"Max concurrent workflows: {max_concurrent_workflows}")
    
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())