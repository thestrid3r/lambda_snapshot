# lambda_snapshot
Use AWS LAMBDA to manage lifecycle of EBS volume in AWS.

This lambda function will create a snapshot of all the volumes that have a specific name, and delete older snapshots based upon your retention days policy and it will then notify the RECIPIENT defined in your function. You can extend it to use it with the tags in your volume too. 

To execute this lambda function use Cloudwatch event as a trigger and based upon the rule of cloudwatch event it will get triggered. e.g: if you want to execute it on a weekly basis then  create a cron schedule  in cloudwatch events which will look like this 

```
0 8 ? * SUN *
```

 > To execute the lambda function will need an IAM role to act as an execution role . Create a IAM roles that will have the following policy attached to it 

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:Describe*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot",
                "ec2:CreateTags",
                "ec2:ModifySnapshotAttribute",
                "ec2:ResetSnapshotAttribute"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

This will grant the lambda function to create and modify the snapshots . If you also want to send mails using this script create a policy with SES sendmail access and attached it to this role .

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
}
```
Set the environment values according to your requirements . 
