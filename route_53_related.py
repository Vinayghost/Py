import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# AWS Credentials (Replace with actual credentials)
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
AWS_REGION = "ap-south-1"

# AWS Clients (Using Explicit Credentials)
try:
    ec2_client = boto3.client(
        "ec2",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    route53_client = boto3.client(
        "route53",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
except NoCredentialsError:
    print("AWS credentials not found. Please check your access key and secret key.")
    exit(1)

def get_instance_ip(instance_id):
    """Retrieve the public IP address of the given EC2 instance."""
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response["Reservations"][0]["Instances"][0]
        return instance.get("PublicIpAddress")
    except (IndexError, KeyError):
        print("Instance not found or no public IP assigned.")
        return None
    except ClientError as e:
        print(f"AWS Error: {e}")
        return None

def get_or_create_hosted_zone(domain_name):
    """Fetch the hosted zone ID for a domain, or create one if it doesn't exist."""
    try:
        # List existing hosted zones
        response = route53_client.list_hosted_zones()
        for zone in response["HostedZones"]:
            if zone["Name"] == domain_name + ".":
                print(f"Found existing hosted zone for {domain_name}")
                return zone["Id"].split("/")[-1]  # Extract ID

        # If not found, create a new hosted zone
        print(f"No hosted zone found for {domain_name}, creating one...")
        create_response = route53_client.create_hosted_zone(
            Name=domain_name,
            CallerReference=str(hash(domain_name)),
            HostedZoneConfig={"Comment": "Created by script", "PrivateZone": False},
        )
        hosted_zone_id = create_response["HostedZone"]["Id"].split("/")[-1]
        print(f"Created new hosted zone: {hosted_zone_id}")
        return hosted_zone_id
    except ClientError as e:
        print(f"Error managing hosted zone: {e}")
        return None

def get_hosted_zone_nameservers(hosted_zone_id):
    """Retrieve existing DNS nameservers for the hosted zone."""
    try:
        response = route53_client.get_hosted_zone(Id=hosted_zone_id)
        nameservers = response.get("DelegationSet", {}).get("NameServers", [])
        return nameservers
    except ClientError as e:
        print(f"Error fetching DNS nameservers: {e}")
        return None

def update_route53_record(hosted_zone_id, domain_name, ip_address):
    """Create or update an A record in Route 53 and return DNS nameservers."""
    try:
        nameservers = get_hosted_zone_nameservers(hosted_zone_id)

        # Upsert A record
        route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                "Comment": "Updating A record",
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": domain_name,
                            "Type": "A",
                            "TTL": 300,
                            "ResourceRecords": [{"Value": ip_address}]
                        }
                    }
                ]
            }
        )
        print(f"Route 53 record updated successfully for {domain_name}")
        return nameservers  # Return existing DNS nameservers

    except ClientError as e:
        print(f"Error updating Route 53 record: {e}")
        return None

if __name__ == "__main__":
    instance_id = input("Enter the EC2 instance ID: ")
    domain_name = input("Enter the domain name (e.g., example.com): ")

    ip_address = get_instance_ip(instance_id)
    if ip_address:
        print(f"🌍 Public IP Address of Instance {instance_id}: {ip_address}")

        hosted_zone_id = get_or_create_hosted_zone(domain_name)
        if hosted_zone_id:
            nameservers = update_route53_record(hosted_zone_id, domain_name, ip_address)
            if nameservers:
                print(f"DNS Nameservers for {domain_name}: {', '.join(nameservers)}")
            else:
                print("⚠️ No nameservers found.")
        else:
            print("Failed to retrieve or create hosted zone.")
    else:
        print("Failed to retrieve instance IP.")