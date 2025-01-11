#!/usr/bin/env python3
import aws_cdk as cdk

from aws_cdk import (
    Stack,
    aws_sns_subscriptions as subscriptions,
    aws_sns as sns,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam
)
from constructs import Construct
from os import path, getenv
from dotenv import load_dotenv

#Load Environment Variables
load_dotenv()

class GDNotificationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        #Aamazon SNS Topic
        sns_topic = sns.Topic(
            self, "GDNotificationTopic",
            display_name="NBA Game Day Notifications",
            topic_name="GDNotificationTopic"
        )
        
        #Lambda Execution Role
        execution_role = iam.Role(
            self, "GDNotificationLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            inline_policies={
                "GDNotificationLambdaPublishSNSInlinePolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "sns:Publish"
                            ],
                            resources=[
                                sns_topic.topic_arn
                            ]
                        )
                    ]
                )
            }
        )
        
        
        #AWS Lambda Function
        gd_lambda_function = _lambda.Function(
            self, "GDNotificationLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="gd_notification.lambda_handler",
            code=_lambda.Code.from_asset("../function/"),
            role=execution_role,
            timeout=cdk.Duration.seconds(60)
        )
        
        gd_lambda_function.add_environment("NBA_API_KEY", getenv("NBA_API_KEY"))
        gd_lambda_function.add_environment("SNS_TOPIC_ARN", sns_topic.topic_arn)
        
        
        #Aamazon SNS Topic Subscription
        sns_topic.add_subscription(subscriptions.EmailSubscription("wynston.s1999@gmail.com"))
        
        #EventBridge Rule
        lambda_target = targets.LambdaFunction(gd_lambda_function)
        events.Rule(
            self, "GDNotificationRule",
            rule_name="GDNotificationRule",
            description="NBA Game Day Notification Rule",
            schedule=events.Schedule.cron(
                minute="0",
                hour="*/2",
                month="*",
                week_day="*",
                year="*"
            ),
            targets=[lambda_target]
        )

#Deploying App
app = cdk.App()
GDNotificationStack(app, "GdNotificationStack",
 )

app.synth()
