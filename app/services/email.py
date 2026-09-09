import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


# In-memory test mailbox for unit testing
_test_outbox = []


def get_test_outbox():
    """Returns test outbox and clears it when requested."""
    return _test_outbox


def clear_test_outbox():
    """Clears the test outbox."""
    _test_outbox.clear()


def send_password_reset_email(user, reset_url: str) -> bool:
    """
    Sends a secure password reset email to the user.
    If SMTP server is configured, sends via smtplib.
    If in development/testing or SMTP is unconfigured, logs the reset link safely.
    """
    subject = "Reset Your SkyGuard AI Password"
    sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@skyguard.ai')
    recipient = user.email

    text_content = f"""Hello {user.name},

We received a request to reset the password for your SkyGuard AI account ({user.email}).

Please click the link below to set a new password:
{reset_url}

This link is single-use and will expire in 1 hour.

If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.

Best regards,
The SkyGuard AI Team
https://skyguard.ai
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #05070c; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #05070c; padding: 40px 20px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 540px; background-color: #0a0e17; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 14px; overflow: hidden; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7);">
          <!-- Header -->
          <tr>
            <td style="padding: 28px 32px; background: linear-gradient(135deg, rgba(0, 240, 255, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%); border-bottom: 1px solid rgba(255, 255, 255, 0.07);">
              <table role="presentation" width="100%">
                <tr>
                  <td>
                    <span style="font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">SkyGuard <span style="color: #00f0ff;">AI</span></span>
                  </td>
                  <td align="right">
                    <span style="font-size: 0.75rem; font-weight: 700; color: #00f0ff; background: rgba(0, 240, 255, 0.12); border: 1px solid rgba(0, 240, 255, 0.3); padding: 4px 10px; border-radius: 9999px;">SECURITY ALERT</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          
          <!-- Body Content -->
          <tr>
            <td style="padding: 32px;">
              <h2 style="margin: 0 0 16px; font-size: 1.35rem; color: #ffffff; font-weight: 700;">Password Reset Request</h2>
              <p style="margin: 0 0 20px; font-size: 0.95rem; line-height: 1.6; color: #94a3b8;">
                Hello <strong>{user.name}</strong>,
              </p>
              <p style="margin: 0 0 24px; font-size: 0.95rem; line-height: 1.6; color: #94a3b8;">
                We received a request to reset the password for your SkyGuard AI account. Click the button below to choose a new password:
              </p>
              
              <!-- CTA Button -->
              <table role="presentation" width="100%" style="margin: 28px 0;">
                <tr>
                  <td align="center">
                    <a href="{reset_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #00f0ff 0%, #3b82f6 100%); color: #05070c; font-weight: 700; font-size: 0.95rem; text-decoration: none; padding: 12px 28px; border-radius: 8px; box-shadow: 0 4px 18px rgba(0, 240, 255, 0.35);">
                      Reset My Password →
                    </a>
                  </td>
                </tr>
              </table>
              
              <p style="margin: 0 0 16px; font-size: 0.85rem; line-height: 1.5; color: #64748b;">
                Or copy and paste this secure link directly into your browser:<br>
                <a href="{reset_url}" style="color: #00f0ff; word-break: break-all; font-size: 0.8rem;">{reset_url}</a>
              </p>
              
              <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 12px 16px; margin-top: 24px;">
                <p style="margin: 0; font-size: 0.8rem; line-height: 1.5; color: #fbbf24;">
                  ⏱ <strong>Security Notice:</strong> This link is single-use and will expire in <strong>1 hour</strong>. If you did not make this request, you can safely ignore this email.
                </p>
              </div>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 20px 32px; background-color: #070a12; border-top: 1px solid rgba(255, 255, 255, 0.05); text-align: center; font-size: 0.775rem; color: #475569;">
              &copy; 2026 SkyGuard AI. Zero-Fabrication Resume & Career Intelligence Engine.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    # Record to in-memory test outbox for unit testing
    _test_outbox.append({
        'to': recipient,
        'subject': subject,
        'reset_url': reset_url,
        'user_id': user.id
    })

    mail_server = current_app.config.get('MAIL_SERVER')
    
    # If in testing mode or mail server is not configured, log link and succeed
    if not mail_server or current_app.config.get('TESTING'):
        current_app.logger.info(f"[AUTH] Password reset email generated for {recipient}: {reset_url}")
        return True

    # Live SMTP Dispatch
    try:
        mail_port = int(current_app.config.get('MAIL_PORT', 587))
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP(mail_server, mail_port, timeout=10)
        if mail_use_tls:
            server.starttls()
        if mail_username and mail_password:
            server.login(mail_username, mail_password)
            
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        current_app.logger.info(f"[AUTH] Password reset email sent via SMTP to {recipient}")
        return True
    except Exception as e:
        current_app.logger.error(f"[AUTH] Failed to send password reset email via SMTP: {e}", exc_info=True)
        return False
