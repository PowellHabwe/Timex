import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Replace these with your actual Gmail credentials and the recipient email
sender_email = "powellhabwe@gmail.com"
receiver_email = "powellhabwenawal@example.com"  # This can be your own email for testing
app_password = "hzle kasb vtfs ppuf"  # This is the app password you generated in Gmail

# Create the message
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Test Email"

# Email body
body = "This is a test email from Python!"
message.attach(MIMEText(body, "plain"))

# Send the email
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)  # Using SSL for secure connection
    server.login(sender_email, app_password)  # Log in using email and app password
    server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.quit()  # Close the connection to the mail server
