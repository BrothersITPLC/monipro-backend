import socket
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMessage, get_connection


def send_team_user_creation_email(email, name, organization_name, default_password):
    try:
        subject = "Your Team Account Has Been Created"
        logo_url = getattr(settings, "COMPANY_LOGO_URL", "https://example.com/logo.png")
        company_name = getattr(settings, "COMPANY_NAME", "Your Company Name")
        login_url = getattr(settings, "LOGIN_URL", "http://localhost:5173/auth")

        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <tr>
                        <td align="center" style="padding: 40px 0 30px 0;">
                            <img src="{logo_url}" alt="{company_name} Logo" width="200" style="display: block; max-width: 100%; height: auto;" />
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 20px 30px 40px 30px;">
                            <h2 style="color:#333333; text-align:center; margin-bottom: 30px;">Welcome to the Team!</h2>
                            <p style="font-size: 16px; color: #555555; line-height: 1.5;">Dear {name},</p>
                            <p style="font-size: 16px; color: #555555; line-height: 1.5;">
                                You have been added as a team member to {organization_name}'s organization.
                            </p>
                            <p style="font-size: 16px; color: #555555; line-height: 1.5;">
                                Your account has been created with your email address: {email}
                            </p>
                            <div style="background-color: #f8f9fa; border-radius: 6px; padding: 20px; margin: 20px 0;">
                                <p style="font-size: 16px; color: #555555; line-height: 1.5;">Your temporary login credentials:</p>
                                <p style="font-size: 16px; color: #555555; line-height: 1.5;">Email: {email}</p>
                                <p style="font-size: 16px; color: #555555; line-height: 1.5;">Password: {default_password}</p>
                                <p style="font-size: 16px; color: #555555; text-align:center; margin-top: 20px;">
                                    <a href="{login_url}" style="color: #007bff; text-decoration: none; font-weight: bold;">Click here to login</a>
                                </p>
                            </div>
                            <p style="font-size: 16px; color: #555555; line-height: 1.5;">
                                For security reasons, we recommend changing your password after your first login.
                            </p>
                            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                            <p style="font-size: 14px; color: #777777;">Best regards,<br>{company_name}</p>
                        </td>
                    </tr>
                </table>
                <p style="text-align:center; font-size: 12px; color: #999999; margin-top:20px;">
                    © {company_name}. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """

        email_message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
            connection=get_connection(timeout=10, fail_silently=False),
        )

        email_message.content_subtype = "html"
        email_message.send()

        return True, "Team user creation email sent successfully"
    except SMTPException as e:
        return False, f"SMTP Error: {str(e)}"
    except socket.timeout:
        return False, "Email server connection timed out"
    except Exception as e:
        return False, str(e)
