#!/usr/bin/env python3
"""
Temporal workflow for generating personalized ad content for multiple targets.
Main workflow spawns child workflows for each personalization job that execute in parallel.
"""
import asyncio
import logging
from datetime import timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from temporalio.workflow import unsafe

from workflow.common_activities import load_config_activity

with unsafe.imports_passed_through():
    from workflow.target_workflow import TargetWorkflow, PersonalizationTarget, TargetWorkflowParams

logger = logging.getLogger(__name__)

# Define data structures
@dataclass
class PersonalizationJob:
    """Represents a personalization job with company info, target account, and personalization target."""
    company_info_id: int
    target_account_id: int
    personalization_target: PersonalizationTarget

@workflow.defn
class AdContentWorkflow:
    """Main workflow to generate personalized ad content for multiple jobs in parallel."""

    @workflow.run
    async def run(self, personalization_jobs: List[PersonalizationJob]) -> Dict[str, Any]:
        """
        Run the ad content generation workflow for multiple personalization jobs in parallel.
        
        Args:
            personalization_jobs: List of PersonalizationJob objects, each containing:
                - company_info_id: ID of the company info to use
                - target_account_id: ID of the target account
                - personalization_target: PersonalizationTarget with type and text
            
        Returns:
            Dictionary with results for each personalization job
        """
        # Load configuration
        config = await workflow.execute_activity(
            load_config_activity,
            "ad_content_workflow_config.yaml",
            start_to_close_timeout=timedelta(seconds=5)
        )
        
        # Get configuration values
        task_queue = config.get("task_queue", "ad-composer-task-queue")
        timeout_seconds = config.get("timeouts", {}).get("workflow_execution", 1800)
        retry_policy_config = config.get("retry_policy", {})
        
        # Create retry policy from config
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=retry_policy_config.get("initial_interval", 1)),
            backoff_coefficient=retry_policy_config.get("backoff_coefficient", 2.0),
            maximum_interval=timedelta(seconds=retry_policy_config.get("maximum_interval", 60)),
            maximum_attempts=retry_policy_config.get("maximum_attempts", 3),
            non_retryable_error_types=retry_policy_config.get("non_retryable_error_types", [])
        )
        
        workflow.logger.info(f"Starting ad content workflow for {len(personalization_jobs)} jobs")
        
        # Create tasks for each personalization job to run in parallel
        child_workflow_tasks = []
        job_identifiers = []
        
        for job in personalization_jobs:
            company_info_id = job.company_info_id
            target_account_id = job.target_account_id
            personalization_target = job.personalization_target
            
            job_identifier = f"company-{company_info_id}-target-{target_account_id}"
            job_identifiers.append(job_identifier)
            
            workflow.logger.info(f"Creating child workflow for job: {job_identifier}")
            
            # Start child workflow for this job
            # Create a params object instead of using args list
            workflow_params = TargetWorkflowParams(
                company_info_id=company_info_id,
                target_account_id=target_account_id,
                personalization_target=personalization_target
            )
            
            child_handle = await workflow.start_child_workflow(
                TargetWorkflow,
                id=f"target-workflow-{job_identifier}-{workflow.info().workflow_id}",
                task_queue=task_queue,
                retry_policy=retry_policy,
                execution_timeout=timedelta(seconds=timeout_seconds),
                arg=workflow_params
            )
            
            # Add to list of tasks
            child_workflow_tasks.append(child_handle)
        
        # Wait for all child workflows to complete
        workflow.logger.info(f"Waiting for {len(child_workflow_tasks)} child workflows to complete")
        results = {}
        
        # Gather results from all child workflows
        for i, task in enumerate(child_workflow_tasks):
            job_identifier = job_identifiers[i]
            try:
                result = await task
                results[job_identifier] = result
                workflow.logger.info(f"Child workflow for {job_identifier} completed successfully")
            except Exception as e:
                workflow.logger.error(f"Child workflow for {job_identifier} failed: {str(e)}")
                results[job_identifier] = {
                    "error": str(e),
                    "success": False
                }
        
        workflow.logger.info(f"Completed ad content workflow for all jobs")
        return results