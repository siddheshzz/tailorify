"""
Celery tasks for sending transactional emails via Resend.
Handles order confirmations, welcome emails, and template-based emails.
"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID

import resend
from celery import Task

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


class EmailTask(Task):
    """Base task with retry configuration for email sending."""
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="app.tasks.email_tasks.send_order_confirmation_email"
)
def send_order_confirmation_email(
    self,
    order_id: str,
    customer_email: str,
    customer_name: str,
    order_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send order confirmation email to customer.
    
    Args:
        order_id: UUID of the order
        customer_email: Customer's email address
        customer_name: Customer's full name
        order_details: Dictionary containing order information
            - service_name: str
            - description: str
            - quoted_price: str
            - estimated_completion: str
            - order_number: str
    
    Returns:
        Dict with email send result
        
    Example:
        order_details = {
            "service_name": "Custom Tailored Suit",
            "description": "3-piece suit with measurements",
            "quoted_price": "$599.99",
            "estimated_completion": "February 15, 2024",
            "order_number": "ORD-12345"
        }
    """
    try:
        logger.info(f"Sending order confirmation email for order {order_id} to {customer_email}")
        
        # If template ID is configured, use template
        if settings.EMAIL_TEMPLATE_ORDER_CONFIRMATION:
            params = {
                "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
                "to": [customer_email],
                "subject": f"Order Confirmation - {order_details.get('order_number', order_id)}",
                "template_id": settings.EMAIL_TEMPLATE_ORDER_CONFIRMATION,
                "template_variables": {
                    "customer_name": customer_name,
                    "order_id": order_id,
                    **order_details
                }
            }
        else:
            # Use HTML email without template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9fafb; }}
                    .order-details {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4F46E5; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Order Confirmation</h1>
                    </div>
                    <div class="content">
                        <p>Dear {customer_name},</p>
                        <p>Thank you for your order! We're excited to create your custom {order_details.get('service_name', 'item')}.</p>
                        
                        <div class="order-details">
                            <h3>Order Details</h3>
                            <p><strong>Order Number:</strong> {order_details.get('order_number', order_id)}</p>
                            <p><strong>Service:</strong> {order_details.get('service_name', 'N/A')}</p>
                            <p><strong>Description:</strong> {order_details.get('description', 'N/A')}</p>
                            <p><strong>Quoted Price:</strong> {order_details.get('quoted_price', 'N/A')}</p>
                            <p><strong>Estimated Completion:</strong> {order_details.get('estimated_completion', 'N/A')}</p>
                        </div>
                        
                        <p>We'll keep you updated on the progress of your order. If you have any questions, please don't hesitate to contact us.</p>
                        <p>Best regards,<br>The Tailorify Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from Tailorify. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
                "to": [customer_email],
                "subject": f"Order Confirmation - {order_details.get('order_number', order_id)}",
                "html": html_content
            }
        
        # Send email via Resend
        response = resend.Emails.send(params)
        
        logger.info(f"Order confirmation email sent successfully for order {order_id}. Email ID: {response.get('id')}")
        
        return {
            "success": True,
            "email_id": response.get("id"),
            "order_id": order_id,
            "recipient": customer_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order {order_id}: {str(e)}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="app.tasks.email_tasks.send_template_email"
)
def send_template_email(
    self,
    recipient_email: str,
    template_id: str,
    template_variables: Dict[str, Any],
    subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email using a Resend template.
    Used by admins to send custom template-based emails.
    
    Args:
        recipient_email: Recipient's email address
        template_id: Resend template ID
        template_variables: Variables to populate the template
        subject: Optional custom subject line
    
    Returns:
        Dict with email send result
        
    Example:
        template_variables = {
            "first_name": "John",
            "order_status": "Ready for Pickup",
            "pickup_date": "Tomorrow"
        }
    """
    try:
        logger.info(f"Sending template email (template: {template_id}) to {recipient_email}")
        
        params = {
            "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
            "to": [recipient_email],
            "template_id": template_id,
            "template_variables": template_variables
        }
        
        # Add custom subject if provided
        if subject:
            params["subject"] = subject
        
        # Send email via Resend
        response = resend.Emails.send(params)
        
        logger.info(f"Template email sent successfully. Email ID: {response.get('id')}")
        
        return {
            "success": True,
            "email_id": response.get("id"),
            "recipient": recipient_email,
            "template_id": template_id
        }
        
    except Exception as e:
        logger.error(f"Failed to send template email to {recipient_email}: {str(e)}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=EmailTask,
    name="app.tasks.email_tasks.send_welcome_email"
)
def send_welcome_email(
    self,
    user_email: str,
    user_name: str
) -> Dict[str, Any]:
    """
    Send welcome email to new users.
    
    Args:
        user_email: New user's email address
        user_name: New user's full name
    
    Returns:
        Dict with email send result
    """
    try:
        logger.info(f"Sending welcome email to {user_email}")
        
        if settings.EMAIL_TEMPLATE_WELCOME:
            # Use template if configured
            params = {
                "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
                "to": [user_email],
                "subject": f"Welcome to {settings.RESEND_FROM_NAME}!",
                "template_id": settings.EMAIL_TEMPLATE_WELCOME,
                "template_variables": {
                    "user_name": user_name
                }
            }
        else:
            # Use simple HTML email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4F46E5; color: white; padding: 30px; text-align: center; }}
                    .content {{ padding: 30px; background-color: #f9fafb; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Tailorify!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user_name},</p>
                        <p>Welcome to Tailorify! We're thrilled to have you join our community of custom tailoring enthusiasts.</p>
                        <p>With Tailorify, you can:</p>
                        <ul>
                            <li>Place custom tailoring orders</li>
                            <li>Track your order status in real-time</li>
                            <li>Save your measurements for future orders</li>
                            <li>View our portfolio of past work</li>
                        </ul>
                        <p>We look forward to creating something special for you!</p>
                        <p>Best regards,<br>The Tailorify Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": f"{settings.RESEND_FROM_NAME} <{settings.RESEND_FROM_EMAIL}>",
                "to": [user_email],
                "subject": f"Welcome to {settings.RESEND_FROM_NAME}!",
                "html": html_content
            }
        
        # Send email via Resend
        response = resend.Emails.send(params)
        
        logger.info(f"Welcome email sent successfully. Email ID: {response.get('id')}")
        
        return {
            "success": True,
            "email_id": response.get("id"),
            "recipient": user_email
        }
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
        # Retry the task
        raise self.retry(exc=e, countdown=60)