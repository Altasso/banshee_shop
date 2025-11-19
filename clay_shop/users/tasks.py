import logging

from celery import shared_task

from users.services.email_service import EmailService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, user_email: str, user_name: str):
    try:
        success = EmailService.send_welcome_email(user_email, user_name)

        if not success:
            raise Exception("Failed to send welcome email")

        return f"Welcome email sent to {user_email}"

    except Exception as exc:
        logger.error(f"Error in send_welcome_email_task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email_task(
    self, user_email: str, user_name: str, verification_link: str
):
    try:
        success = EmailService.send_verification_email(
            user_email, user_name, verification_link
        )

        if not success:
            raise Exception("Failed to send verification email")

        return f"Verification email sent to {user_email}"

    except Exception as exc:
        logger.error(f"Error in send_verification_email_task: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email_task(
    self, user_email: str, user_name: str, reset_link: str
):
    try:
        success = EmailService.send_password_reset_email(
            user_email, user_name, reset_link
        )

        if not success:
            raise Exception("Failed to send password reset email")
        return f"Password reset email sent to {user_email}"

    except Exception as exc:
        logger.error(f"Error in send_password_reset_email_task: {str(exc)}")
        raise self.retry(exc=exc)
