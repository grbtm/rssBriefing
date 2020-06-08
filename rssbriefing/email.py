"""

    Module with  E-mail sending wrapper functions.
    Generally based on https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
    But using the django.core.mail module instead of unmaintained flask_mail.

    From Django docs:

    Mail is sent using the SMTP host and port specified in the EMAIL_HOST and EMAIL_PORT settings.
    The EMAIL_HOST_USER and EMAIL_HOST_PASSWORD settings, if set, are used to authenticate to the SMTP server,
    and the EMAIL_USE_TLS and EMAIL_USE_SSL settings control whether a secure connection is used.

"""

from django.core.mail import send_mail, send_mass_mail

from flask import current_app as app
from flask import render_template

from rssbriefing.briefing_utils import get_standard_briefing


def send_single_mail(subject,
                     from_email,
                     recipient_list,
                     text_body,
                     html_body=None,
                     fail_silently=False,
                     auth_user=None,
                     auth_password=None,
                     connection=None):
    """
        Email sending wrapper around Django send_email method.

        Be aware:
        recipients in same recipient_list will see all other addresses in the email messages’ “To:” field

    :param subject: [Str]
    :param from_email: [Str]
    :param recipient_list: [Lst[Str] Each recipient will see other recipients in the “To:” field of the email message.
    :param text_body: [Str]
    :param html_body: If html_message is provided, the resulting email will be a multipart/alternative email with message as the text/plain content type and html_message as the text/html content type.
    :param fail_silently: [Bool] When it’s False, send_mail() will raise an smtplib.SMTPException if an error occurs.
    :param auth_user: [Str] opt. username to use to authenticate to the SMTP server. If this isn’t provided, Django will use the value of the EMAIL_HOST_USER setting.
    :param auth_password: [Str] opt.  password to use to authenticate to the SMTP server. If this isn’t provided, Django will use the value of the EMAIL_HOST_PASSWORD setting.
    :param connection: The optional email backend to use to send the mail. If unspecified, an instance of the default backend will be used.
    :return:
    """

    send_mail(subject=subject,
              message=text_body,
              from_email=from_email,
              recipient_list=recipient_list,
              fail_silently=fail_silently,
              auth_user=auth_user,
              auth_password=auth_password,
              connection=connection,
              html_message=html_body)


def send_multiple_mails_single_connection(datatuple,
                                          fail_silently=False,
                                          auth_user=None,
                                          auth_password=None,
                                          connection=None):
    """
        Email sending wrapper around Django send_mass_mail method.

        Be aware:
        recipients in same recipient_list will see all other addresses in the email messages’ “To:” field

    :param datatuple: [Tuple] in which each element is in this format: (subject, message, from_email, recipient_list)
    :param fail_silently: [Bool] When it’s False, send_mail() will raise an smtplib.SMTPException if an error occurs.
    :param auth_user: [Str] opt. username to use to authenticate to the SMTP server. If this isn’t provided, Django will use the value of the EMAIL_HOST_USER setting.
    :param auth_password: [Str] opt.  password to use to authenticate to the SMTP server. If this isn’t provided, Django will use the value of the EMAIL_HOST_PASSWORD setting.
    :param connection:
    :return:
    """

    send_mass_mail(datatuple=datatuple,
                   fail_silently=fail_silently,
                   auth_user=auth_user,
                   auth_password=auth_password,
                   connection=connection)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_single_mail(subject="[RoboBriefing] Reset Your Password",
                     from_email=app.config['ADMINS'][0],
                     recipient_list=[user.email],
                     text_body=render_template('email/reset_password.txt',
                                               user=user, token=token),
                     html_body=render_template('email/reset_password.html',
                                               user=user, token=token))

def send_standard_briefing(user):
    briefing_items, latest_briefing_date = get_standard_briefing()

    if briefing_items:
        send_single_mail(subject="Today's RoboBriefing",
                         from_email=app.config['ADMINS'][0],
                         recipient_list=[user.email],
                         text_body=render_template('briefing/briefing_email.txt',
                                                   user=user, items=briefing_items))
