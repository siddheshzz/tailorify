"""
Celery tasks for bulk email campaigns.
Allows admins to send campaigns to all registered users asynchronously.
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

import resend
from celery import Task, group
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


class CampaignTask(Task):
    """Base task with retry configuration for campaign sending."""
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 2}
    retry_backoff = True
    retry_backoff_max = 300  # 5 minutes
    retry_jitter = True


@celery_app.task(
    bind=True,
    base=CampaignTask,
    name="app.tasks.campaign_tasks.send_bulk_campaign"
)
def send_bulk_campaign(
    self,
    template_id: str,
    template_variables: Dict[str, Any],
    subject: str,
    user_filter: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a bulk email campaign to all registered users (or filtered subset).
    This task orchestrates the campaign by fetching users and creating
    individual email tasks.
    
    Args:
        template_id: Resend template ID to use
        template_variables: Common template variables for all recipients
        subject: Email subject line
        user_filter: Optional filter criteria (e.g., {"user_type": "client", "is_active": True})
    
    Returns:
        Dict with campaign summary
        
    Example:
        user_filter = {"user_type": "client", "is_active": True}
        template_variables = {
            "campaign_name": "Spring Sale 2024",
            "discount_code": "SPRING20",
            "expiry_date": "March 31, 2024"
        }
    """
    try:
        logger.info(f"Starting bulk campaign with template {template_id}")
        
        # Fetch users from database (we need to use sync version for Celery)
        import asyncio
        users = asyncio.run(_fetch_users_for_campaign(user_filter))
        
        if not users:
            logger.warning("No users found for campaign")
            return {
                "success": True,
                "total_users": 0,
                "emails_sent": 0,
                "message": "No users match the filter criteria"
            }
        
        logger.info(f"Found {len(users)} users for campaign")
        
        # Create individual email tasks for each user
        email_tasks = []
        for user in users:
            # Merge common template variables with user-specific ones
            user_template_vars = {
                **template_variables,
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "email": user.get("email"),
            }
            
            # Create task for sending individual campaign email
            task = send_single_campaign_email.s(
                recipient_email=user.get("email"),
                recipient_name=f"{user.get('first_name')} {user.get('last_name')}",
                template_id=template_id,
                template_variables=user_template_vars,
                subject=subject
            )
            email_tasks.append(task)
        
        # Execute all email tasks as a group
        job = group(email_tasks)
        result = job.apply_async()
        
        logger.info(f"Campaign initiated for {len(users)} users. Group ID: {result.id}")
        
        return {
            "success": True,
            "total_users": len(users),
            "group_id": result.id,
            "template_id": template_id,
            "subject": subject,
            "message": f"Campaign email tasks queued for {len(users)} users"
        }
        
    except Exception as e:
        logger.error(f"Failed to initiate bulk campaign: {str(e)}")
        raise self.retry(exc=e, countdown=120)


@celery_app.task(
    bind=True,
    base=CampaignTask,
    name="app.tasks.campaign_tasks.send_single_campaign_email"
)
def send_single_campaign_email(
    self,
    recipient_email: str,
    recipient_name: str,
    template_id: str,
    template_variables: Dict[str, Any],
    subject: str
) -> Dict[str, Any]:
    """
    Send a single campaign email to one user.
    This task is called by send_bulk_campaign for each user.
    
    Args:
        recipient_email: Recipient's email address
        recipient_name: Recipient's full name
        template_id: Resend template ID
        template_variables: Template variables (including user-specific ones)
        subject: Email subject line
    
    Returns:
        Dict with email send result
    """
    try:
        logger.info(f"Sending campaign email to {recipient_email}")
        
        params = {
            "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
            "to": [recipient_email],
            "subject": subject,
            "template_id": template_id,
            "template_variables": template_variables
        }
        
        # Send email via Resend
        response = resend.Emails.send(params)
        
        logger.info(f"Campaign email sent successfully to {recipient_email}. Email ID: {response.get('id')}")
        
        return {
            "success": True,
            "email_id": response.get("id"),
            "recipient": recipient_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send campaign email to {recipient_email}: {str(e)}")
        # Retry with backoff
        raise self.retry(exc=e, countdown=60)


async def _fetch_users_for_campaign(
    user_filter: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Fetch users from database for campaign.
    
    Args:
        user_filter: Optional filter criteria
    
    Returns:
        List of user dictionaries
    """
    async with AsyncSessionLocal() as session:
        # Build query
        query = select(User).where(User.is_active == True)
        
        # Apply filters if provided
        if user_filter:
            if "user_type" in user_filter:
                from app.models.user import UserType
                query = query.where(User.user_type == UserType(user_filter["user_type"]))
        
        # Execute query
        result = await session.execute(query)
        users = result.scalars().all()
        
        # Convert to dict for serialization
        return [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            for user in users
        ]


@celery_app.task(
    bind=True,
    name="app.tasks.campaign_tasks.send_targeted_campaign"
)
def send_targeted_campaign(
    self,
    user_ids: List[str],
    template_id: str,
    template_variables: Dict[str, Any],
    subject: str
) -> Dict[str, Any]:
    """
    Send campaign to specific users (targeted campaign).
    
    Args:
        user_ids: List of user UUIDs to target
        template_id: Resend template ID
        template_variables: Template variables
        subject: Email subject
    
    Returns:
        Dict with campaign summary
        
    Example:
        user_ids = ["123e4567-e89b-12d3-a456-426614174000", "223e4567-e89b-12d3-a456-426614174001"]
    """
    try:
        logger.info(f"Starting targeted campaign for {len(user_ids)} users")
        
        # Fetch specified users from database
        import asyncio
        users = asyncio.run(_fetch_users_by_ids(user_ids))
        
        if not users:
            logger.warning("No users found for targeted campaign")
            return {
                "success": False,
                "message": "No users found with the provided IDs"
            }
        
        # Create individual email tasks
        email_tasks = []
        for user in users:
            user_template_vars = {
                **template_variables,
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "email": user.get("email"),
            }
            
            task = send_single_campaign_email(self,
                recipient_email=user.get("email"),
                recipient_name=f"{user.get('first_name')} {user.get('last_name')}",
                template_id=template_id,
                template_variables=user_template_vars,
                subject=subject
            )
            email_tasks.append(task)
        
        # Execute tasks as group
        job = group(email_tasks)
        result = job.apply_async()
        
        logger.info(f"Targeted campaign initiated for {len(users)} users")
        
        return {
            "success": True,
            "total_users": len(users),
            "group_id": result.id,
            "message": f"Targeted campaign queued for {len(users)} users"
        }
        
    except Exception as e:
        logger.error(f"Failed to initiate targeted campaign: {str(e)}")
        return {"success": False, "error": str(e)}


async def _fetch_users_by_ids(user_ids: List[str]) -> List[Dict[str, Any]]:
    """Fetch users by their IDs."""
    async with AsyncSessionLocal() as session:
        from uuid import UUID
        
        # Convert string IDs to UUIDs
        uuid_ids = [UUID(uid) for uid in user_ids]
        
        # Query users
        query = select(User).where(
            User.id.in_(uuid_ids),
            User.is_active == True
        )
        
        result = await session.execute(query)
        users = result.scalars().all()
        
        return [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            for user in users
        ]