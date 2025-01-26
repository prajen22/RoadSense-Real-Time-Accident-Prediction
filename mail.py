import requests

def send_simple_message():
    # Replace 'YOUR_API_KEY' with your actual Mailgun API key.
    # Replace 'your_domain' with your Mailgun domain (e.g., 'sandboxb47b7b34b723423b935965fbd26eac0e.mailgun.org')
    response = requests.post(
        "https://api.mailgun.net/v3/sandboxb47b7b34b723423b935965fbd26eac0e.mailgun.org/messages",  # The endpoint for sending emails
        auth=("api", "64183e8e533d1395e59d5374b630f395-191fb7b6-716ba616"),  # Mailgun API key
        data={
            "from": "Excited User <mailgun@sandboxb47b7b34b723423b935965fbd26eac0e.mailgun.org>",  # From address
            "to": ["bar@example.com", "YOU@sandboxb47b7b34b723423b935965fbd26eac0e.mailgun.org"],  # List of recipients
            "subject": "Hello",  # Email subject
            "text": "Testing some Mailgun awesomeness!"  # Body of the email
        }
    )
    
    # Check if the email was sent successfully
    if response.status_code == 200:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email. Status code: {response.status_code}, Response: {response.text}")

# Call the function to send the email
send_simple_message()
