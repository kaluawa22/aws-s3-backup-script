import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from pathlib import Path
import smtplib, ssl, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

now = datetime.now()
today = now.strftime("at %I:%M %p on %m/%d/%Y")

listOfBuckets = []
listOfPaths = ['/Users/kaluawa/Projects/aws_backup_script/kaluaws','/Volumes/SanDisk']

# Tuple containing variables that will be used for logging
log_statement = ('/Users/kaluawa/Projects/aws_backup_script/kaluaws', 'was backed up successfully ', today)


def convertTuple(tup):
    # initialize an empty string
    str = ''
    for item in tup:
        str = str + item
    return str

# Function that connects to aws s3 and backs up files including directories
def upload_files(path, bucketname):
    # AWS S3 Credentials
    session = boto3.Session(
        aws_access_key_id='',
        aws_secret_access_key='',
        region_name='us-east-2'
    )
    s3 = session.resource('s3')
    # name of s3 bucket I am backing up to
    # bucket = s3.Bucket('kalutest')
    bucket = s3.Bucket(bucketname)
    # loop to traverse directories and back then up , making sure the file structure stays the same
    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=full_path[len(path) + 1:], Body=data)
    # Statement to write to log file
    with open('log.txt', 'a') as new_file:
        logFile = map(str, log_statement)
        new_file.write(" ".join(logFile) + "\n")


# function call to start script



upload_files('/Users/kaluawa/Projects/aws_backup_script/kaluaws','kalutest')


subject = "AWS Backup Report"
body = convertTuple(log_statement)
sender_email = ""
receiver_email = ""
password = ""
port = 465

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email

# Add body to email
message.attach(MIMEText(body, "plain"))

filename = "log.txt"  # In same directory as script

# Open text file in binary mode
with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filename}",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()
#create SSL connection
context = ssl.create_default_context()

#send email containing current log.txt file and current log message
with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login("kaluawacs@gmail.com", password)
    server.sendmail(sender_email, receiver_email, text)
