from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from celery import shared_task
from django.conf import settings
import logging

logger = logging.getLogger('mailer')

def send_otp(to_email, otp):
    logger.info('send_otp: {} - {}'.format(to_email, otp))
    send_mail_in_background.delay(
        to_emails = [to_email],
        template_url = 'mails/otp.html', 
        subject = '[MAILIX.VN] Xác thực đăng nhập',
        context = {
            'otp': otp,
            'email': to_email
        }
    )

def send_forget_password_otp(to_email, otp):
    logger.info('send_forget_password_otp: {} - {}'.format(to_email, otp))
    send_mail_in_background.delay(
        to_emails = [to_email],
        template_url = 'mails/forgot_password.html', 
        subject = '[MAILIX.VN] Quên mật khẩu',
        context = {
            'otp': otp,
            'email': to_email
        }
    )

def send_error_500_email(error_message=None, error_url=None, error_detail=None):
    logger.error('send_error_500_email: {}'.format(error_message))
    send_to_admins.delay(
        template_url = 'mails/500_error.html',
        subject = '[MAILIX.VN] Báo cáo lỗi hệ thống',
        context = {
            'error_message': error_message,
            'error_url': error_url,
            'error_detail': error_detail
        }
    )


@shared_task
def send_to_admins(template_url, subject, context):
    print('[Celery] send_to_admins')
    return mail_admins(
        subject = subject,
        message = '',
        html_message=render_to_string(template_url, context),
    )

@shared_task
def send_mail_in_background(to_emails, template_url, subject, context):
    print('[Celery] send_mail_in_background {}'.format(to_emails))
    return send_mail(
        subject = subject,
        message = '',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=to_emails,
        html_message=render_to_string(template_url, context),
    )
