import os
import json
import urllib3

# Get mailgun secret from Lambda environment variables
mg_api = os.environ["MG_API"]
# Get hCaptcha secret from Lambda environment variables
h_captcha = os.environ["HC_API"]
bcc_emails = os.environ["EMAILS"]

# Use this (public) sitekey for hCaptcha
hcKey = "8398bfb2-83c8-45fe-b3c8-a6cedbef3549"
# Use this url for hCaptcha
hcURL = "https://hcaptcha.com/siteverify"
# Use this url for mailgun
mgURL = "https://api.mailgun.net/v3/thinktutor.org/messages"

# Import the automatic email from res/formMail.txt
with open("formmail.txt", "r") as myfile:
    formMail = myfile.read()


def lambda_handler(event, context):
    # Import the submitted contact info
    in_dict = json.loads(event["body"])
    # Get hCaptch token
    h_token = in_dict['h-captcha-response']
    # Start pool manager
    http = urllib3.PoolManager()
    h_dict = {
        'secret': h_captcha,
        'response': h_token,
        'sitekey': hcKey
    }
    h = http.request(
        method="POST",
        url=hcURL,
        fields=h_dict,
    )
    captcha_response = json.loads(h.data.decode("utf-8"))
    if captcha_response['success']:
        # Use the secret API key for mailgun in header
        headers = urllib3.util.make_headers(basic_auth="api:" + mg_api)
        # Format the body of the request for mailgun
        r_dict = {
            "from": "Think Tutor <hello@thinktutor.org>",
            "to": in_dict["name"] + "<" + in_dict["email"] + ">",
            "bcc": bcc_emails,
            "subject": "Thank you for contacting ThinkTutor",
            "text": formMail
            + "\n\n> "
            + in_dict["body"].replace("\n", "\n> ")
            + "\n>\n>---\n> "
            + in_dict["name"]
            + "\n> "
            + in_dict["email"],
        }
        # Actually make the request
        r = http.request(
            method="POST",
            url=mgURL,
            fields=r_dict,
            headers=headers,
        )
        return {"statusCode": r.status, "body": r.data.decode("utf-8")}
    else:
        return {"statusCode": 400, "body": "Captcha validation failed"}

