import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging
import ssl
import sys

# Configure logging to print to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Force the configuration
)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already added
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

class AutomationService:
    def __init__(self):
        # Using the provided Gmail credentials
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.smtp_username = 'mutation.forlife06@gmail.com'
        self.smtp_password = 'lqruxxzlxzogqqfh'
        self.sender_email = 'mutation.forlife06@gmail.com'
        print("\n=== Initializing AutomationService ===")
        print(f"SMTP Server: {self.smtp_server}")
        print(f"SMTP Port: {self.smtp_port}")
        print(f"Sender Email: {self.sender_email}")
        logger.info("AutomationService initialized with Gmail credentials")

    def send_email(self, to_email: str, subject: str, content: str):
        """Send an email using SMTP."""
        try:
            print(f"\n=== Attempting to send email to {to_email} ===")
            logger.info(f"Attempting to send email to {to_email}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach HTML content
            msg.attach(MIMEText(content, 'html'))
            print("Email message prepared")
            logger.info("Email message prepared")

            # Create secure SSL/TLS connection
            context = ssl.create_default_context()
            
            try:
                print("Connecting to SMTP server...")
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    logger.info("Connecting to SMTP server...")
                    server.ehlo()  # Can be omitted
                    print("Starting TLS...")
                    server.starttls(context=context)  # Secure the connection
                    logger.info("TLS started")
                    
                    # Login
                    print("Attempting SMTP login...")
                    logger.info("Attempting SMTP login...")
                    server.login(self.smtp_username, self.smtp_password)
                    print("SMTP login successful")
                    logger.info("SMTP login successful")
                    
                    # Send email
                    print("Sending email...")
                    logger.info("Sending email...")
                    server.send_message(msg)
                    print("Email sent successfully")
                    logger.info("Email sent successfully")
                
                return True
            except smtplib.SMTPAuthenticationError as e:
                print(f"SMTP Authentication failed: {str(e)}")
                logger.error(f"SMTP Authentication failed: {str(e)}")
                return False
            except smtplib.SMTPException as e:
                print(f"SMTP error occurred: {str(e)}")
                logger.error(f"SMTP error occurred: {str(e)}")
                return False
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def get_stage_content(self, stage: str, customer_name: str = "there") -> dict:
        """Get content templates for different stages."""
        print(f"\n=== Getting content for stage: {stage} ===")
        logger.info(f"Getting content for stage: {stage}")
        templates = {
            "Awareness": {
                "subject": "Welcome to Our Product!",
                "content": f"""
                <h2>Welcome {customer_name}!</h2>
                <p>We noticed you're exploring our product. Here are some resources to help you get started:</p>
                <ul>
                    <li>Product Overview Guide</li>
                    <li>Getting Started Tutorial</li>
                    <li>Customer Success Stories</li>
                </ul>
                <p>Would you like to schedule a quick demo to learn more?</p>
                <p>Best regards,<br>Your Team</p>
                """
            },
            "Consideration": {
                "subject": "Ready to Take the Next Step?",
                "content": f"""
                <h2>Hi {customer_name},</h2>
                <p>We see you're interested in our product! Here's what we can offer:</p>
                <ul>
                    <li>Free Trial Access</li>
                    <li>Detailed Feature Comparison</li>
                    <li>Custom Pricing Options</li>
                </ul>
                <p>Would you like to speak with our team about your specific needs?</p>
                <p>Best regards,<br>Your Team</p>
                """
            },
            "Decision": {
                "subject": "Special Offer Just for You!",
                "content": f"""
                <h2>Hello {customer_name},</h2>
                <p>We're excited to help you make your decision! Here's a special offer:</p>
                <ul>
                    <li>20% off your first year</li>
                    <li>Free onboarding session</li>
                    <li>Priority support access</li>
                </ul>
                <p>This offer is valid for the next 48 hours. Would you like to proceed?</p>
                <p>Best regards,<br>Your Team</p>
                """
            }
        }
        return templates.get(stage, {
            "subject": "Update on Your Journey",
            "content": f"""
            <h2>Hi {customer_name},</h2>
            <p>We're here to help you with your journey. How can we assist you today?</p>
            <p>Best regards,<br>Your Team</p>
            """
        })

    def trigger_stage_automation(self, customer_id: str, stage: str, customer_email: str, customer_name: str = None):
        """Trigger automated actions based on the customer's stage."""
        try:
            print(f"\n=== Triggering automation for customer {customer_id} at stage {stage} ===")
            logger.info(f"Triggering automation for customer {customer_id} at stage {stage}")
            
            # Get content for the stage
            content = self.get_stage_content(stage, customer_name or "there")
            print(f"Got content for stage {stage}")
            logger.info(f"Got content for stage {stage}")
            
            # Send automated email
            print(f"Sending email to {customer_email}")
            email_sent = self.send_email(
                to_email=customer_email,
                subject=content["subject"],
                content=content["content"]
            )
            print(f"Email send attempt result: {email_sent}")
            logger.info(f"Email send attempt result: {email_sent}")

            # Log the automation
            print(f"Stage automation completed for customer {customer_id} at stage {stage}")
            logger.info(f"Stage automation completed for customer {customer_id} at stage {stage}")
            
            return {
                "success": True,
                "actions_taken": ["email_sent"] if email_sent else [],
                "stage": stage
            }
        except Exception as e:
            print(f"Failed to trigger stage automation: {str(e)}")
            logger.error(f"Failed to trigger stage automation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stage": stage
            } 