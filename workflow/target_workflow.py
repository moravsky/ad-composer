#!/usr/bin/env python3
"""
Temporal child workflow for generating personalized ad content for a single target.
"""
import logging
from datetime import timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from temporalio.workflow import unsafe

from workflow.common_activities import load_config_activity

@dataclass
class PersonalizationTarget:
    """Represents a target for personalization with type and text."""
    type: str
    text: str

@dataclass
class TargetWorkflowParams:
    """Parameters for the TargetWorkflow."""
    company_info_id: int
    target_account_id: int
    personalization_target: PersonalizationTarget

with unsafe.imports_passed_through():
    from workflow.target_activities import (
        get_company_info_activity,
        get_target_account_activity,
        get_contextual_information_activity,
        generate_personalized_content_activity,
        save_personalized_content_activity,
        PersonalizeContentInput,
        SaveContentInput
    )

logger = logging.getLogger(__name__)

@workflow.defn
class TargetWorkflow:
    """Child workflow to generate personalized ad content for a single target."""

    @workflow.run
    async def run(self, params: TargetWorkflowParams) -> Dict[str, Any]:
        """
        Run the personalization workflow for a single target.
        
        Args:
            params: TargetWorkflowParams containing:
                - company_info_id: ID of the company info to use
                - target_account_id: ID of the target account
                - personalization_target: Object with type and text
            
        Returns:
            Dictionary with personalization results
        """
        # Extract parameters from the input object
        company_info_id = params.company_info_id
        target_account_id = params.target_account_id
        personalization_target = params.personalization_target
        # Load configuration
        config = await workflow.execute_activity(
            load_config_activity,
            "target_workflow_config.yaml",
            start_to_close_timeout=timedelta(seconds=5)
        )
        
        # Get configuration values
        activity_timeout = config.get("timeouts", {}).get("activity", 300)
        retry_policy_config = config.get("retry_policy", {})
        
        # Create retry policy from config
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=retry_policy_config.get("initial_interval", 1)),
            backoff_coefficient=retry_policy_config.get("backoff_coefficient", 2.0),
            maximum_interval=timedelta(seconds=retry_policy_config.get("maximum_interval", 60)),
            maximum_attempts=retry_policy_config.get("maximum_attempts", 3),
            non_retryable_error_types=retry_policy_config.get("non_retryable_error_types", [])
        )
        
        workflow.logger.info(f"Starting target workflow for company {company_info_id}, target {target_account_id}")
        
        try:
            # Get company info
            company_info = await workflow.execute_activity(
                get_company_info_activity,
                company_info_id,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(seconds=activity_timeout)
            )
            
            if not company_info:
                raise ApplicationError(f"Company info not found for ID: {company_info_id}")
            
            # Get target account details
            target = await workflow.execute_activity(
                get_target_account_activity,
                target_account_id,
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(seconds=activity_timeout)
            )
            
            if not target:
                raise ApplicationError(f"Target account not found for ID: {target_account_id}")
            
            # Get target account context from their website if available
            target_context = ""
            if target.get("url"):
                target_context = await workflow.execute_activity(
                    get_contextual_information_activity,
                    target["url"],
                    retry_policy=retry_policy,
                    start_to_close_timeout=timedelta(seconds=activity_timeout * 2)  # Longer timeout for web scraping
                )
                workflow.logger.info(f"Retrieved context for target account: {target['name']}")
            
            # Get text to personalize
            text = personalization_target.text
            text_type = personalization_target.type
            
            if not text:
                raise ApplicationError("No text provided for personalization")
            
            # Generate personalized content
            personalized_text = await workflow.execute_activity(
                generate_personalized_content_activity,
                PersonalizeContentInput(
                    company_info=company_info,
                    target_account=target,
                    target_context=target_context,
                    text=text,
                    text_type=text_type
                ),
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(seconds=activity_timeout * 2)  # Longer timeout for AI generation
            )
            
            # Save results to database
            save_result = await workflow.execute_activity(
                save_personalized_content_activity,
                SaveContentInput(
                    company_info_id=company_info_id,
                    target_account_id=target_account_id,
                    original_text=text,
                    personalized_text=personalized_text,
                    text_type=text_type
                ),
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(seconds=activity_timeout)
            )
            
            # Return results
            result = {
                "company_info": {
                    "id": company_info_id,
                    "name": company_info.get("company_name")
                },
                "target_account": {
                    "id": target_account_id,
                    "name": target.get("name")
                },
                "original_text": text,
                "personalized_text": personalized_text,
                "text_type": text_type,
                "success": True,
                "saved": save_result
            }
            
            workflow.logger.info(f"Completed target workflow for company {company_info_id}, target {target_account_id}")
            return result
            
        except Exception as e:
            workflow.logger.error(f"Target workflow failed: {str(e)}")
            return {
                "company_info_id": company_info_id,
                "target_account_id": target_account_id,
                "error": str(e),
                "success": False
            }