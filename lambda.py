import os
import json
import urllib3

# Get secrets from Lambda environment variables
mg_api = os.environ["MG_API"]
bcc_emails = os.environ["EMAILS"]

# Import the automatic email from res/formMail.txt
with open("formmail.txt", "r") as myfile:
    formMail = myfile.read()


def lambda_handler(event, context):
    # Import the submitted contact info
    in_dict = json.loads(event["body"])
    # Start pool manager
    http = urllib3.PoolManager()
    # Use the secret API key for mailgun
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
        url="https://api.mailgun.net/v3/mail.thinktutor.org/messages",
        fields=r_dict,
        headers=headers,
    )
    return {"statusCode": r.status, "body": r.data.decode("utf-8")}

