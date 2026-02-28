"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           DevOps Boto3 Automation Toolkit                           ║
║                    Complete AWS Infrastructure Management Suite                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

This comprehensive module provides essential Boto3 operations for DevOps automation,
covering the most critical AWS services and use cases in modern cloud infrastructure
management and CI/CD pipelines.

📋 COVERED SERVICES & USE CASES:
═══════════════════════════════════════════════════════════════════════════════════════
1️⃣  EC2 - Instance provisioning and management
2️⃣  S3 - Automated backups and log uploads  
3️⃣  IAM - Users, roles, and policies management
4️⃣  Lambda - Function deployment and execution
5️⃣  CloudWatch - Monitoring, metrics, and alarms
6️⃣  ELB/ALB - Load balancer management
7️⃣  RDS - Database provisioning and snapshots
8️⃣  ECR - Docker image repository management
9️⃣  SNS - Notifications and alerting system
🔟 SQS - Message queues for CI/CD workflows

🎯 TARGET AUDIENCE: DevOps Engineers, Cloud Architects, Site Reliability Engineers
🚀 USE CASE: Production automation, infrastructure as code, CI/CD pipelines
📅 VERSION: 1.0 | DATE: November 2025 | AUTHOR: DevOps Training Module
"""

import boto3
import json
import time
import base64
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError

# ════════════════════════════════════════════════════════════════════════════════════════
#                                   AWS CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════════════

AWS_ACCESS_KEY = "YOUR_ACCESS_KEY_HERE"
AWS_SECRET_KEY = "YOUR_SECRET_KEY_HERE"
AWS_REGION = "us-east-1"  # Default region


def get_aws_client(service_name, region=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        🔧 UNIVERSAL AWS CLIENT FACTORY                          │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates configured AWS service clients for any AWS service with proper error handling.
    
    Parameters:
    -----------
    service_name : str
        AWS service name (e.g., 'ec2', 's3', 'iam', 'lambda', 'cloudwatch')
    region : str, optional
        AWS region override (default: uses global AWS_REGION)
    
    Returns:
    --------
    boto3.client : Configured AWS service client
    """
    try:
        return boto3.client(
            service_name,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=region or AWS_REGION
        )
    except Exception as e:
        print(f"❌ Error creating {service_name} client: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                                 1️⃣ EC2 MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════════════

def provision_ec2_instance(instance_name, ami_id, instance_type="t2.micro", key_name=None, security_groups=None, user_data=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                     🚀 EC2 INSTANCE PROVISIONING ENGINE                        │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Provisions EC2 instances with comprehensive configuration options for DevOps automation.
    """
    ec2 = get_aws_client('ec2')
    if not ec2:
        return None
    
    try:
        params = {
            'ImageId': ami_id,
            'InstanceType': instance_type,
            'MinCount': 1,
            'MaxCount': 1,
            'TagSpecifications': [{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': instance_name}]
            }]
        }
        
        if key_name:
            params['KeyName'] = key_name
        if security_groups:
            params['SecurityGroupIds'] = security_groups
        if user_data:
            params['UserData'] = user_data
        
        response = ec2.run_instances(**params)
        instance_id = response['Instances'][0]['InstanceId']
        
        print(f"🚀 Instance '{instance_name}' provisioned successfully!")
        print(f"📋 Instance ID: {instance_id}")
        print(f"⚙️  Instance Type: {instance_type}")
        return instance_id
        
    except ClientError as e:
        print(f"❌ EC2 provisioning error: {e}")
        return None


def manage_ec2_lifecycle(instance_id, action):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       🔄 EC2 LIFECYCLE MANAGEMENT                              │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Manages EC2 instance lifecycle operations for automation workflows.
    
    Actions: 'start', 'stop', 'reboot', 'terminate'
    """
    ec2 = get_aws_client('ec2')
    if not ec2:
        return False
    
    try:
        if action == 'start':
            ec2.start_instances(InstanceIds=[instance_id])
            print(f"▶️ Starting instance {instance_id}...")
        elif action == 'stop':
            ec2.stop_instances(InstanceIds=[instance_id])
            print(f"⏸️ Stopping instance {instance_id}...")
        elif action == 'reboot':
            ec2.reboot_instances(InstanceIds=[instance_id])
            print(f"🔄 Rebooting instance {instance_id}...")
        elif action == 'terminate':
            ec2.terminate_instances(InstanceIds=[instance_id])
            print(f"💥 Terminating instance {instance_id}...")
        else:
            print(f"❌ Invalid action: {action}")
            return False
            
        print(f"✅ {action.title()} operation initiated successfully")
        return True
        
    except ClientError as e:
        print(f"❌ EC2 lifecycle error: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════════════════
#                              2️⃣ S3 BACKUP & LOGGING
# ════════════════════════════════════════════════════════════════════════════════════════

def automated_s3_backup(source_path, bucket_name, backup_prefix="backups/"):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      💾 AUTOMATED S3 BACKUP SYSTEM                             │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Performs automated backups to S3 with timestamp organization for DevOps workflows.
    """
    s3 = get_aws_client('s3')
    if not s3:
        return False
    
    try:
        import os
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.basename(source_path)
        s3_key = f"{backup_prefix}{timestamp}_{filename}"
        
        s3.upload_file(source_path, bucket_name, s3_key)
        
        print(f"💾 Backup completed successfully!")
        print(f"📁 Source: {source_path}")
        print(f"🪣 Destination: s3://{bucket_name}/{s3_key}")
        return s3_key
        
    except Exception as e:
        print(f"❌ S3 backup error: {e}")
        return False


def upload_logs_to_s3(log_file_path, bucket_name, log_prefix="logs/"):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📊 LOG AGGREGATION SYSTEM                                │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Uploads application and system logs to S3 for centralized log management.
    """
    s3 = get_aws_client('s3')
    if not s3:
        return False
    
    try:
        import os
        
        date_folder = datetime.now().strftime("%Y/%m/%d")
        filename = os.path.basename(log_file_path)
        s3_key = f"{log_prefix}{date_folder}/{filename}"
        
        s3.upload_file(log_file_path, bucket_name, s3_key)
        
        print(f"📊 Log upload successful!")
        print(f"📁 Log file: {log_file_path}")
        print(f"🗂️  S3 location: s3://{bucket_name}/{s3_key}")
        return s3_key
        
    except Exception as e:
        print(f"❌ Log upload error: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════════════════
#                                3️⃣ IAM MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════════════

def create_iam_user(username, initial_password=None, attach_policies=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        👤 IAM USER PROVISIONING                                │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates IAM users with optional password and policy attachment for access management.
    """
    iam = get_aws_client('iam')
    if not iam:
        return False
    
    try:
        # Create user
        iam.create_user(UserName=username)
        print(f"👤 IAM user '{username}' created successfully!")
        
        # Set password if provided
        if initial_password:
            iam.create_login_profile(
                UserName=username,
                Password=initial_password,
                PasswordResetRequired=True
            )
            print(f"🔐 Login profile created with password reset required")
        
        # Attach policies if provided
        if attach_policies:
            for policy_arn in attach_policies:
                iam.attach_user_policy(UserName=username, PolicyArn=policy_arn)
                print(f"📋 Attached policy: {policy_arn}")
        
        return True
        
    except ClientError as e:
        print(f"❌ IAM user creation error: {e}")
        return False


def create_iam_role(role_name, assume_role_policy, attach_policies=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                         🎭 IAM ROLE PROVISIONING                               │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates IAM roles for service-to-service authentication and cross-account access.
    """
    iam = get_aws_client('iam')
    if not iam:
        return None
    
    try:
        # Create role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy),
            Description=f"DevOps automation role: {role_name}"
        )
        
        role_arn = response['Role']['Arn']
        print(f"🎭 IAM role '{role_name}' created successfully!")
        print(f"🔗 Role ARN: {role_arn}")
        
        # Attach policies if provided
        if attach_policies:
            for policy_arn in attach_policies:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                print(f"📋 Attached policy: {policy_arn}")
        
        return role_arn
        
    except ClientError as e:
        print(f"❌ IAM role creation error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                              4️⃣ LAMBDA MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════════════

def deploy_lambda_function(function_name, zip_file_path, handler, runtime, role_arn, description=""):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      ⚡ LAMBDA FUNCTION DEPLOYMENT                              │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Deploys Lambda functions for serverless automation and event-driven workflows.
    """
    lambda_client = get_aws_client('lambda')
    if not lambda_client:
        return None
    
    try:
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zip_content},
            Description=description,
            Timeout=60,
            MemorySize=128
        )
        
        function_arn = response['FunctionArn']
        print(f"⚡ Lambda function '{function_name}' deployed successfully!")
        print(f"🔗 Function ARN: {function_arn}")
        return function_arn
        
    except Exception as e:
        print(f"❌ Lambda deployment error: {e}")
        return None


def invoke_lambda_function(function_name, payload=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       🎯 LAMBDA FUNCTION EXECUTION                             │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Triggers Lambda functions with optional payload for CI/CD automation.
    """
    lambda_client = get_aws_client('lambda')
    if not lambda_client:
        return None
    
    try:
        params = {'FunctionName': function_name}
        
        if payload:
            params['Payload'] = json.dumps(payload)
        
        response = lambda_client.invoke(**params)
        
        print(f"🎯 Lambda function '{function_name}' invoked successfully!")
        
        if 'Payload' in response:
            result = json.loads(response['Payload'].read())
            print(f"📋 Response: {result}")
            return result
        
        return True
        
    except Exception as e:
        print(f"❌ Lambda invocation error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                             5️⃣ CLOUDWATCH MONITORING
# ════════════════════════════════════════════════════════════════════════════════════════

def create_cloudwatch_alarm(alarm_name, metric_name, namespace, threshold, comparison_operator, resource_id):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      📊 CLOUDWATCH ALARM CREATION                              │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates CloudWatch alarms for proactive monitoring and alerting.
    """
    cloudwatch = get_aws_client('cloudwatch')
    if not cloudwatch:
        return False
    
    try:
        cloudwatch.put_metric_alarm(
            AlarmName=alarm_name,
            ComparisonOperator=comparison_operator,
            EvaluationPeriods=2,
            MetricName=metric_name,
            Namespace=namespace,
            Period=300,
            Statistic='Average',
            Threshold=threshold,
            ActionsEnabled=True,
            AlarmDescription=f'DevOps monitoring alarm for {resource_id}',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': resource_id
                },
            ]
        )
        
        print(f"📊 CloudWatch alarm '{alarm_name}' created successfully!")
        print(f"🎯 Monitoring: {metric_name} in {namespace}")
        print(f"⚠️  Threshold: {threshold} ({comparison_operator})")
        return True
        
    except ClientError as e:
        print(f"❌ CloudWatch alarm error: {e}")
        return False


def get_cloudwatch_metrics(namespace, metric_name, start_time, end_time, resource_id=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📈 METRICS DATA RETRIEVAL                                │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Retrieves CloudWatch metrics data for analysis and reporting.
    """
    cloudwatch = get_aws_client('cloudwatch')
    if not cloudwatch:
        return None
    
    try:
        dimensions = []
        if resource_id:
            dimensions.append({'Name': 'InstanceId', 'Value': resource_id})
        
        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average', 'Maximum']
        )
        
        datapoints = response['Datapoints']
        print(f"📈 Retrieved {len(datapoints)} metric datapoints")
        print(f"📊 Metric: {metric_name} from {namespace}")
        
        return sorted(datapoints, key=lambda x: x['Timestamp'])
        
    except ClientError as e:
        print(f"❌ CloudWatch metrics error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                            6️⃣ LOAD BALANCER MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════════════

def create_application_load_balancer(lb_name, subnets, security_groups):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                   ⚖️ APPLICATION LOAD BALANCER CREATION                        │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates Application Load Balancers for high availability and traffic distribution.
    """
    elbv2 = get_aws_client('elbv2')
    if not elbv2:
        return None
    
    try:
        response = elbv2.create_load_balancer(
            Name=lb_name,
            Subnets=subnets,
            SecurityGroups=security_groups,
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
        
        lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
        lb_dns = response['LoadBalancers'][0]['DNSName']
        
        print(f"⚖️ Application Load Balancer '{lb_name}' created successfully!")
        print(f"🔗 ARN: {lb_arn}")
        print(f"🌐 DNS Name: {lb_dns}")
        return lb_arn
        
    except ClientError as e:
        print(f"❌ Load Balancer creation error: {e}")
        return None


def create_target_group(tg_name, vpc_id, port=80, protocol='HTTP'):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       🎯 TARGET GROUP MANAGEMENT                               │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates target groups for load balancer traffic routing and health checks.
    """
    elbv2 = get_aws_client('elbv2')
    if not elbv2:
        return None
    
    try:
        response = elbv2.create_target_group(
            Name=tg_name,
            Protocol=protocol,
            Port=port,
            VpcId=vpc_id,
            HealthCheckEnabled=True,
            HealthCheckPath='/',
            HealthCheckProtocol=protocol,
            HealthCheckIntervalSeconds=30,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=5
        )
        
        tg_arn = response['TargetGroups'][0]['TargetGroupArn']
        
        print(f"🎯 Target Group '{tg_name}' created successfully!")
        print(f"🔗 ARN: {tg_arn}")
        print(f"🏥 Health checks enabled on {protocol}:{port}")
        return tg_arn
        
    except ClientError as e:
        print(f"❌ Target Group creation error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                               7️⃣ RDS MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════════════

def create_rds_instance(db_instance_id, db_name, engine, username, password, instance_class='db.t3.micro'):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      🗄️ RDS DATABASE PROVISIONING                              │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Provisions RDS database instances for application data storage.
    """
    rds = get_aws_client('rds')
    if not rds:
        return None
    
    try:
        response = rds.create_db_instance(
            DBInstanceIdentifier=db_instance_id,
            DBName=db_name,
            Engine=engine,
            MasterUsername=username,
            MasterUserPassword=password,
            DBInstanceClass=instance_class,
            AllocatedStorage=20,
            StorageType='gp2',
            BackupRetentionPeriod=7,
            MultiAZ=False,
            PubliclyAccessible=True,
            StorageEncrypted=True
        )
        
        endpoint = response['DBInstance'].get('Endpoint', {}).get('Address', 'Pending...')
        
        print(f"🗄️ RDS instance '{db_instance_id}' creation initiated!")
        print(f"🔧 Engine: {engine} | Class: {instance_class}")
        print(f"🌐 Endpoint: {endpoint}")
        return db_instance_id
        
    except ClientError as e:
        print(f"❌ RDS creation error: {e}")
        return None


def create_rds_snapshot(db_instance_id, snapshot_id=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📸 RDS SNAPSHOT CREATION                                 │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates RDS snapshots for backup and disaster recovery.
    """
    rds = get_aws_client('rds')
    if not rds:
        return None
    
    try:
        if not snapshot_id:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            snapshot_id = f"{db_instance_id}-snapshot-{timestamp}"
        
        response = rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=db_instance_id
        )
        
        print(f"📸 RDS snapshot creation initiated!")
        print(f"🗄️ Database: {db_instance_id}")
        print(f"📋 Snapshot ID: {snapshot_id}")
        return snapshot_id
        
    except ClientError as e:
        print(f"❌ RDS snapshot error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                              8️⃣ ECR MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════════════

def create_ecr_repository(repository_name):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                     🐳 ECR REPOSITORY CREATION                                 │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates ECR repositories for Docker image storage and management.
    """
    ecr = get_aws_client('ecr')
    if not ecr:
        return None
    
    try:
        response = ecr.create_repository(
            repositoryName=repository_name,
            imageScanningConfiguration={'scanOnPush': True},
            encryptionConfiguration={'encryptionType': 'AES256'}
        )
        
        repo_uri = response['repository']['repositoryUri']
        
        print(f"🐳 ECR repository '{repository_name}' created successfully!")
        print(f"🔗 Repository URI: {repo_uri}")
        print(f"🔍 Image scanning enabled on push")
        return repo_uri
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
            print(f"ℹ️ ECR repository '{repository_name}' already exists")
            # Get existing repository URI
            response = ecr.describe_repositories(repositoryNames=[repository_name])
            return response['repositories'][0]['repositoryUri']
        else:
            print(f"❌ ECR repository error: {e}")
            return None


def get_ecr_login_token():
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       🔐 ECR AUTHENTICATION TOKEN                              │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Gets ECR login token for Docker CLI authentication.
    """
    ecr = get_aws_client('ecr')
    if not ecr:
        return None
    
    try:
        response = ecr.get_authorization_token()
        token_data = response['authorizationData'][0]
        
        token = base64.b64decode(token_data['authorizationToken']).decode('utf-8')
        username, password = token.split(':')
        endpoint = token_data['proxyEndpoint']
        
        print(f"🔐 ECR login token retrieved successfully!")
        print(f"🌐 Registry Endpoint: {endpoint}")
        print(f"⏰ Token expires: {token_data['expiresAt']}")
        
        return {
            'username': username,
            'password': password,
            'endpoint': endpoint,
            'expires_at': token_data['expiresAt']
        }
        
    except ClientError as e:
        print(f"❌ ECR authentication error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                              9️⃣ SNS NOTIFICATIONS
# ════════════════════════════════════════════════════════════════════════════════════════

def create_sns_topic(topic_name):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📢 SNS TOPIC CREATION                                    │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates SNS topics for distributed notifications and alerting.
    """
    sns = get_aws_client('sns')
    if not sns:
        return None
    
    try:
        response = sns.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        
        print(f"📢 SNS topic '{topic_name}' created successfully!")
        print(f"🔗 Topic ARN: {topic_arn}")
        return topic_arn
        
    except ClientError as e:
        print(f"❌ SNS topic creation error: {e}")
        return None


def send_sns_notification(topic_arn, subject, message):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      📨 SNS MESSAGE PUBLISHING                                 │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Sends notifications via SNS for alerts and status updates.
    """
    sns = get_aws_client('sns')
    if not sns:
        return False
    
    try:
        response = sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        
        message_id = response['MessageId']
        print(f"📨 SNS notification sent successfully!")
        print(f"📋 Message ID: {message_id}")
        print(f"📢 Subject: {subject}")
        return message_id
        
    except ClientError as e:
        print(f"❌ SNS notification error: {e}")
        return False


def subscribe_to_sns_topic(topic_arn, protocol, endpoint):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📧 SNS SUBSCRIPTION MANAGEMENT                           │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates SNS subscriptions for email, SMS, or webhook notifications.
    """
    sns = get_aws_client('sns')
    if not sns:
        return None
    
    try:
        response = sns.subscribe(
            TopicArn=topic_arn,
            Protocol=protocol,  # 'email', 'sms', 'http', 'https', 'lambda'
            Endpoint=endpoint
        )
        
        subscription_arn = response['SubscriptionArn']
        print(f"📧 SNS subscription created successfully!")
        print(f"🔗 Subscription ARN: {subscription_arn}")
        print(f"📮 Protocol: {protocol} | Endpoint: {endpoint}")
        return subscription_arn
        
    except ClientError as e:
        print(f"❌ SNS subscription error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                              🔟 SQS MESSAGE QUEUES
# ════════════════════════════════════════════════════════════════════════════════════════

def create_sqs_queue(queue_name, is_fifo=False):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📬 SQS QUEUE CREATION                                    │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates SQS queues for decoupled communication in CI/CD workflows.
    """
    sqs = get_aws_client('sqs')
    if not sqs:
        return None
    
    try:
        attributes = {}
        
        if is_fifo:
            queue_name = f"{queue_name}.fifo"
            attributes['FifoQueue'] = 'true'
            attributes['ContentBasedDeduplication'] = 'true'
        
        response = sqs.create_queue(
            QueueName=queue_name,
            Attributes=attributes
        )
        
        queue_url = response['QueueUrl']
        print(f"📬 SQS queue '{queue_name}' created successfully!")
        print(f"🔗 Queue URL: {queue_url}")
        print(f"📊 Type: {'FIFO' if is_fifo else 'Standard'}")
        return queue_url
        
    except ClientError as e:
        print(f"❌ SQS queue creation error: {e}")
        return None


def send_sqs_message(queue_url, message_body, message_attributes=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📤 SQS MESSAGE SENDING                                   │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Sends messages to SQS queues for workflow coordination.
    """
    sqs = get_aws_client('sqs')
    if not sqs:
        return None
    
    try:
        params = {
            'QueueUrl': queue_url,
            'MessageBody': message_body
        }
        
        if message_attributes:
            params['MessageAttributes'] = message_attributes
        
        response = sqs.send_message(**params)
        message_id = response['MessageId']
        
        print(f"📤 SQS message sent successfully!")
        print(f"📋 Message ID: {message_id}")
        return message_id
        
    except ClientError as e:
        print(f"❌ SQS message sending error: {e}")
        return None


def receive_sqs_messages(queue_url, max_messages=1):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      📥 SQS MESSAGE RECEIVING                                  │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Receives and processes messages from SQS queues.
    """
    sqs = get_aws_client('sqs')
    if not sqs:
        return None
    
    try:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_messages,
            WaitTimeSeconds=10  # Long polling
        )
        
        messages = response.get('Messages', [])
        print(f"📥 Received {len(messages)} message(s) from queue")
        
        for message in messages:
            print(f"📋 Message ID: {message['MessageId']}")
            print(f"📄 Body: {message['Body']}")
        
        return messages
        
    except ClientError as e:
        print(f"❌ SQS message receiving error: {e}")
        return None


# ════════════════════════════════════════════════════════════════════════════════════════
#                             🚀 DEVOPS WORKFLOW EXAMPLES
# ════════════════════════════════════════════════════════════════════════════════════════

def complete_web_app_deployment():
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                    🌐 COMPLETE WEB APPLICATION DEPLOYMENT                      │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Demonstrates a complete DevOps workflow combining multiple AWS services.
    """
    print("🚀 Starting complete web application deployment workflow...")
    
    # 1. Create SNS topic for notifications
    topic_arn = create_sns_topic("deployment-notifications")
    
    # 2. Create SQS queue for deployment tasks
    queue_url = create_sqs_queue("deployment-tasks")
    
    # 3. Create ECR repository for application images
    repo_uri = create_ecr_repository("my-web-app")
    
    # 4. Provision RDS database
    db_id = create_rds_instance(
        db_instance_id="webapp-db",
        db_name="webapp",
        engine="mysql",
        username="admin",
        password="SecurePassword123!"
    )
    
    # 5. Create CloudWatch alarm for monitoring
    create_cloudwatch_alarm(
        alarm_name="HighCPUUsage",
        metric_name="CPUUtilization",
        namespace="AWS/EC2",
        threshold=80.0,
        comparison_operator="GreaterThanThreshold",
        resource_id="i-1234567890abcdef0"
    )
    
    print("✅ Web application infrastructure deployment completed!")
    return {
        'topic_arn': topic_arn,
        'queue_url': queue_url,
        'repo_uri': repo_uri,
        'db_id': db_id
    }


if __name__ == "__main__":
    # ═══════════════════════════════════════════════════════════════════════════════════
    #                        🎯 DEVOPS BOTO3 TOOLKIT DEMO
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    print("🌟 " + "="*80 + " 🌟")
    print("           🛠️ DEVOPS BOTO3 AUTOMATION TOOLKIT")
    print("           Complete AWS Infrastructure Management")
    print("🌟 " + "="*80 + " 🌟")
    
    print("\n📋 Available DevOps Operations:")
    print("═" * 50)
    print("1️⃣  EC2 - Instance provisioning and lifecycle management")
    print("2️⃣  S3 - Automated backups and centralized logging")
    print("3️⃣  IAM - User and role management with policies")
    print("4️⃣  Lambda - Serverless function deployment and execution")
    print("5️⃣  CloudWatch - Monitoring, metrics, and alerting")
    print("6️⃣  ELB/ALB - Load balancer and target group management")
    print("7️⃣  RDS - Database provisioning and snapshot management")
    print("8️⃣  ECR - Container registry and image management")
    print("9️⃣  SNS - Notification and alerting system")
    print("🔟 SQS - Message queues for workflow coordination")
    
    print("\n🚀 Quick Start Examples:")
    print("═" * 50)
    print("# Provision EC2 instance")
    print("# provision_ec2_instance('web-server', 'ami-12345', 't2.micro')")
    print("")
    print("# Create automated backup")
    print("# automated_s3_backup('/path/to/file', 'backup-bucket')")
    print("")
    print("# Deploy Lambda function")
    print("# deploy_lambda_function('processor', 'function.zip', 'index.handler', 'python3.9', role_arn)")
    print("")
    print("# Send notification")
    print("# send_sns_notification(topic_arn, 'Deployment Complete', 'Application deployed successfully')")
    
    print("\n💡 Configuration Required:")
    print("═" * 50)
    print("⚙️  Update AWS_ACCESS_KEY and AWS_SECRET_KEY variables")
    print("🌍 Set appropriate AWS_REGION for your deployment")
    print("🔐 Ensure IAM permissions for all services used")
    print("📋 Review and customize function parameters as needed")
    
    print("\n🎯 Example: Complete Web App Deployment")
    print("═" * 50)
    print("# Uncomment below to run full deployment workflow:")
    print("# complete_web_app_deployment()")
    
    print("\n✅ Toolkit ready for DevOps automation!")