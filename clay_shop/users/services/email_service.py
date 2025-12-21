import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str) -> bool:
        try:
            subject = "Добро пожаловать"

            html_content = render_to_string(
                "email/welcome.html",
                {"user_name": user_name, "site_url": settings.SITE_URL},
            )

            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Welcome email sent to {user_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending welcome email to {user_email}: {str(e)}")
            return False

    @staticmethod
    def send_verification_email(
        user_email: str, user_name: str, verification_link: str
    ) -> bool:
        try:
            subject = "Подтвердите ваш email"

            html_content = render_to_string(
                "email/verification.html",
                {
                    "user_name": user_name,
                    "verification_link": verification_link,
                },
            )

            text_content = f"""
                Здравствуйте, {user_name}!

                Спасибо за регистрацию в {settings.SITE_NAME}.

                Подтвердите ваш email, перейдя по ссылке:
                {verification_link}

                С уважением,
                Команда {settings.SITE_NAME}
                """

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Verification email sent to {user_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending verification email to {user_email}: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(
        user_email: str, user_name: str, reset_link: str
    ) -> bool:
        try:
            subject = "Восстановление пароля"

            html_content = render_to_string(
                "email/password_reset.html",
                {
                    "user_name": user_name,
                    "reset_link": reset_link,
                    "site_url": settings.SITE_URL,
                },
            )

            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Password reset email sent to {user_email}")
            return True
        except Exception as e:
            logger.error(
                f"Error sending password reset email to {user_email}: {str(e)}"
            )
            return False
