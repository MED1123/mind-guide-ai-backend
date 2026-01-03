from app.services.email_service import EmailService
import os

# Test recipient (using the sender address for self-test)
test_email = os.getenv("SMTP_USER", "noreplymoodjournal@gmail.com")

print(f"--- Testing SMTP Email to {test_email} ---")
success = EmailService.send_email(
    to_email=test_email, 
    subject="Mood Journal SMTP Test", 
    html_content="<h1>It works!</h1><p>The Python backend can send emails using your Gmail credentials.</p>"
)

if success:
    print("SUCCESS: Test email sent.")
else:
    print("FAILURE: Could not send email.")
