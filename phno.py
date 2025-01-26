from twilio.rest import Client

# Twilio Credentials (Make sure to replace these with your actual credentials)
TWILIO_ACCOUNT_SID = 'AC5ef25d3c6123ab87fa7eb9fd5d4e48cf'
TWILIO_AUTH_TOKEN = 'c533139e651574e9b40afbb4e3385ef5'
TWILIO_PHONE_NUMBER = '+17178336953'

# Initialize the Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Making the call
call = client.calls.create(
    to='+919500716115',  # The phone number to call (include the country code)
    from_=TWILIO_PHONE_NUMBER,  # Your Twilio phone number (include the country code)
    url='http://demo.twilio.com/docs/voice.xml'  # The URL of the Twilio XML script (e.g., a greeting or a voice prompt)
)

# Print call SID to confirm the call was made
print(f"Call SID: {call.sid}")
