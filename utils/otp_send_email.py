import socket
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMessage, get_connection, send_mail


def send_otp_via_email(email, otp_code):
    try:
        subject = "Your Account Verification Code"
        # Get the logo URL and company name from settings or use defaults.
        logo_url = getattr(settings, "COMPANY_LOGO_URL", "https://example.com/logo.png")
        company_name = getattr(settings, "COMPANY_NAME", "Your Company Name")

        html_message = f"""
        <html>
        <body style="margin:0; padding:0; background-color:#f4f4f4;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse:collapse; background-color:#ffffff; margin-top:30px;">
                <tr>
                    <td align="center" style="padding: 40px 0 30px 0;">
                        <img src="{logo_url}" alt="{company_name} Logo" width="200" style="display: block;" />
                    </td>
                </tr>
                <tr>
                    <td style="padding: 20px 30px 40px 30px; font-family: Arial, sans-serif; color: #333333;">
                        <h2 style="color:#333333; text-align:center;">Email Verification</h2>
                        <p style="font-size: 16px;">Dear User,</p>
                        <p style="font-size: 16px;">Your One-Time Password (OTP) for email verification is:</p>
                        <p style="font-size: 32px; color: #007BFF; text-align:center; margin: 20px 0;">{otp_code}</p>
                        <p style="font-size: 16px;">Please use this code to complete your registration. If you did not request this, please ignore this email.</p>
                        <br>
                        <p style="font-size: 14px; color: #777777;">Thank you,<br>{company_name}</p>
                    </td>
                </tr>
            </table>
            <p style="text-align:center; font-family: Arial, sans-serif; font-size: 12px; color: #999999; margin-top:20px;">
                © {company_name}. All rights reserved.
            </p>
        </body>
        </html>
        """
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]

        connection = get_connection(
            timeout=10,
            fail_silently=False,
        )

        send_mail(
            subject, html_message, email_from, recipient_list, connection=connection
        )
        return True, "OTP sent successfully"
    except SMTPException as e:
        return False, f"SMTP Error: {str(e)}"
    except socket.timeout:
        return False, "Email server connection timed out"
    except Exception as e:
        return False, str(e)


class EmailHandler:
    @staticmethod
    def send_email(data):
        email_from = settings.EMAIL_HOST_USER
        email_message = EmailMessage(
            subject=data.get("subject", "No Subject"),
            body=data.get("body", ""),
            from_email=email_from,
            to=[data.get("to_email")],
        )
        if data.get("is_html", False):
            email_message.content_subtype = "html"
        email_message.send()
