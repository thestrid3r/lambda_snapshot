import boto3
import datetime
import os
from botocore.exceptions import ClientError


ec2 = boto3.client('ec2', os.environ['regionname'])
today = datetime.date.today()
today_string = today.strftime('%Y-%m-%d')


def send_email(BODY_HTML):
    SENDER = os.environ['SENDER']
    RECIPIENT = os.environ['RECIPIENT']
    AWS_SES_REGION = os.environ['AWS_SES_REGION']
    SUBJECT = "weekly backup for {instance_name}".format(
        instance_name=os.environ['Instance_name'])
    CHARSET = "UTF-8"
    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_SES_REGION)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def lambda_handler(event, context):
    # filter based upon name of volume
    vol_names = ec2.describe_volumes(
        Filters=[{'Name': 'tag:Name', 'Values': [os.getenv('volume_name')]}])
    if len(vol_names['Volumes']) == 0:
        BODY_HTML = """<html>
        <head></head>
        <body>
            <p><strong> No volumes found for {instance_name}, contact the administrator , Weekly backup failed </strong></p>
        </body>
        </html>""".format(instance_name=os.environ['Instance_name'])
        send_email(BODY_HTML)

    for volume in vol_names['Volumes']:
        # create snapshot
        # print(volume['VolumeId'])
        Snapshot_Id = ec2.create_snapshot(
            VolumeId=volume['VolumeId'], Description='Created by Lambda weekly backup function')
        # print(Snapshot_Id)
        ec2_resource = boto3.resource(
            'ec2', region_name=os.environ['regionname'])
        snapshot = ec2_resource.Snapshot(Snapshot_Id['SnapshotId'])
        if 'Tags' in volume:
            for tags in volume['Tags']:
                if tags["Key"] == 'Name':
                    volumename = tags["Value"]+'-'+today_string
            # Add volume name to snapshot for easier identification
        snapshot.create_tags(Tags=[
            {'Key': 'Name', 'Value': volumename},
            {'Key': 'Instance_name', 'Value': os.environ['Instance_name']}
        ])
        # print(Snapshot_Id['SnapshotId'],volumename)
        # send mail upon successfull
        BODY_HTML = """<html>
        <head></head>
        <body>
            <p>
            weekly snapshot creation for instance <b>{instance_name}</b> is done , with snapshot id <b>{snapshot_id}</b>.
            <p>
        </body>
        </html>""".format(snapshot_id=Snapshot_Id['SnapshotId'], instance_name=os.environ['Instance_name'])
        send_email(BODY_HTML)
