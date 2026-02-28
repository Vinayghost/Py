"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                EC2 Management Utility                                ║
║                          Advanced AWS EC2 Operations & Monitoring                   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

This module provides comprehensive EC2 instance management capabilities including:
- Instance creation, management, and termination
- Advanced search and filtering based on resource usage
- Security group analysis and monitoring
- Memory and performance issue detection
- Multi-region support for AWS operations

Author: Training Module
Date: November 2025
Version: 2.0
"""

import boto3
from botocore.exceptions import NoCredentialsError, ClientError


# ════════════════════════════════════════════════════════════════════════════════════════
#                                   AWS CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════════════

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY") 
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")  # Default to ap-south-1 if not set


def get_ec2_client(region):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                            🔧 AWS EC2 CLIENT FACTORY                             │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates and returns a configured AWS EC2 client for the specified region.
    This is the foundation method used by all other EC2 operations.
    
    Parameters:
    -----------
    region : str
        The AWS region name (e.g., 'us-east-1', 'ap-south-1', 'eu-west-1')
    
    Returns:
    --------
    boto3.client
        Configured EC2 client ready for API operations
    
    Example:
    --------
    >>> client = get_ec2_client('us-east-1')
    >>> instances = client.describe_instances()
    
    Note:
    -----
    Uses the global AWS credentials defined at the module level.
    Ensure proper IAM permissions are configured for EC2 operations.
    """
    return boto3.client(
        "ec2",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=region
    )

def create_instance(ami_id, instance_type="t2.micro", key_name=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                          🚀 EC2 INSTANCE CREATION ENGINE                        │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Launches a new EC2 instance with specified configuration parameters.
    This function handles the complete instance creation workflow including
    error handling and success confirmation.
    
    Parameters:
    -----------
    ami_id : str
        Amazon Machine Image ID (e.g., 'ami-12345678')
        Defines the operating system and initial software configuration
    
    instance_type : str, optional
        EC2 instance type specification (default: 't2.micro')
        Common types: t2.micro, t2.small, t3.medium, m5.large, etc.
    
    key_name : str, optional
        EC2 Key Pair name for SSH access (default: None)
        Required for secure shell access to the instance
    
    Returns:
    --------
    str or None
        Instance ID of the created instance on success, None on failure
    
    Raises:
    -------
    ClientError
        When AWS API call fails (insufficient permissions, quota limits, etc.)
    
    Example:
    --------
    >>> instance_id = create_instance('ami-12345678', 't2.micro', 'my-key-pair')
    >>> print(f"Created instance: {instance_id}")
    
    Security Note:
    --------------
    Always use key pairs for production instances to enable secure access.
    """
    try:
        # Execute the instance creation API call
        response = get_ec2_client(AWS_REGION).run_instances(
            ImageId=ami_id,           # Operating system image
            InstanceType=instance_type,   # Hardware specification
            MinCount=1,               # Minimum instances to launch
            MaxCount=1,               # Maximum instances to launch
            KeyName=key_name          # SSH key pair for access
        )
        
        # Extract the instance ID from the response
        instance_id = response["Instances"][0]["InstanceId"]
        print(f"✅ EC2 instance '{instance_id}' created successfully.")
        return instance_id
        
    except ClientError as e:
        print(f"❌ Error creating instance: {e}")
        return None

def list_instances_by_region(region=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        🌍 MULTI-REGION INSTANCE DISCOVERY                       │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Discovers and lists all EC2 instances across specified regions or all available regions.
    This function provides a comprehensive overview of your EC2 infrastructure across
    the AWS global infrastructure.
    
    Parameters:
    -----------
    region : str, optional
        Specific AWS region to search (default: None)
        If None, searches all available regions for comprehensive coverage
    
    Returns:
    --------
    None
        Prints formatted instance information directly to console
    
    Output Format:
    --------------
    For each region with instances:
    - Region name header
    - Instance ID and current state
    - Clean, readable formatting
    
    Example:
    --------
    >>> list_instances_by_region('us-east-1')  # Single region
    >>> list_instances_by_region()             # All regions
    
    Performance Note:
    ----------------
    Scanning all regions may take time due to API rate limits.
    Use specific region parameter for faster results.
    """
    try:
        # Determine which regions to scan
        if region:
            regions = [region]  # Single region specified
        else:
            # Get all available AWS regions
            ec2_client = get_ec2_client(AWS_REGION)
            regions = [r["RegionName"] for r in ec2_client.describe_regions()["Regions"]]
        
        print(f"🔍 Scanning {len(regions)} region(s) for EC2 instances...")
        
        # Iterate through each region
        for reg in regions:
            ec2 = get_ec2_client(reg)
            response = ec2.describe_instances()
            has_instances = False
            
            # Check each reservation and instance
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    has_instances = True
                    
            # Display results if instances found
            if has_instances:
                print(f"\n🏢 ### EC2 Instances in {reg}: ###")
                for reservation in response["Reservations"]:
                    for instance in reservation["Instances"]:
                        state_emoji = "🟢" if instance['State']['Name'] == 'running' else "🔴"
                        print(f"{state_emoji} ID: {instance['InstanceId']} | "
                              f"State: {instance['State']['Name']}")

    except ClientError as e:
        print(f"❌ Error listing instances: {e}")

def start_instance(instance_id):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                           ▶️  INSTANCE STARTUP CONTROLLER                        │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Starts a stopped EC2 instance and initiates the boot sequence.
    This operation transitions the instance from 'stopped' to 'running' state.
    
    Parameters:
    -----------
    instance_id : str
        The unique identifier of the EC2 instance to start
        Format: 'i-1234567890abcdef0'
    
    Returns:
    --------
    None
        Prints status message indicating start operation initiated
    
    State Transition:
    ----------------
    stopped → pending → running
    
    Example:
    --------
    >>> start_instance('i-1234567890abcdef0')
    ⚡ Instance 'i-1234567890abcdef0' is starting...
    
    Billing Note:
    -------------
    Instance will incur charges once it reaches 'running' state.
    """
    try:
        # Send start command to AWS
        get_ec2_client(AWS_REGION).start_instances(InstanceIds=[instance_id])
        print(f"⚡ Instance '{instance_id}' is starting...")
    except ClientError as e:
        print(f"❌ Error starting instance: {e}")


def stop_instance(instance_id):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                            ⏸️  INSTANCE SHUTDOWN CONTROLLER                      │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Gracefully shuts down a running EC2 instance while preserving EBS volumes.
    This operation transitions the instance from 'running' to 'stopped' state.
    
    Parameters:
    -----------
    instance_id : str
        The unique identifier of the EC2 instance to stop
        Format: 'i-1234567890abcdef0'
    
    Returns:
    --------
    None
        Prints status message indicating stop operation initiated
    
    State Transition:
    ----------------
    running → stopping → stopped
    
    Example:
    --------
    >>> stop_instance('i-1234567890abcdef0')
    🛑 Instance 'i-1234567890abcdef0' is stopping...
    
    Data Safety:
    ------------
    EBS root volumes are preserved. Instance store volumes are lost.
    Always ensure applications handle graceful shutdown.
    """
    try:
        # Send stop command to AWS
        get_ec2_client(AWS_REGION).stop_instances(InstanceIds=[instance_id])
        print(f"🛑 Instance '{instance_id}' is stopping...")
    except ClientError as e:
        print(f"❌ Error stopping instance: {e}")


def terminate_instance(instance_id):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        💥 INSTANCE TERMINATION WITH SAFETY                      │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Permanently destroys an EC2 instance with user confirmation for safety.
    This is an irreversible operation that deletes the instance and its instance store.
    
    ⚠️  WARNING: This operation is PERMANENT and IRREVERSIBLE! ⚠️
    
    Parameters:
    -----------
    instance_id : str
        The unique identifier of the EC2 instance to terminate
        Format: 'i-1234567890abcdef0'
    
    Returns:
    --------
    None
        Prints status message or abortion notice
    
    Safety Features:
    ---------------
    - Requires explicit user confirmation ('yes')
    - Case-insensitive confirmation check
    - Aborts on any input other than 'yes'
    
    State Transition:
    ----------------
    any_state → shutting-down → terminated
    
    Example:
    --------
    >>> terminate_instance('i-1234567890abcdef0')
    Are you sure you want to terminate instance 'i-1234567890abcdef0'? (yes/no): yes
    💥 Instance 'i-1234567890abcdef0' is terminating...
    
    Data Loss Warning:
    -----------------
    - Instance store volumes are permanently lost
    - EBS root volume fate depends on DeleteOnTermination setting
    - All unsaved data will be lost
    """
    # Safety confirmation prompt
    confirm = input(f"⚠️  Are you sure you want to terminate instance '{instance_id}'? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("🚫 Aborting termination - Instance preserved.")
        return
        
    try:
        # Execute termination command
        get_ec2_client(AWS_REGION).terminate_instances(InstanceIds=[instance_id])
        print(f"💥 Instance '{instance_id}' is terminating...")
    except ClientError as e:
        print(f"❌ Error terminating instance: {e}")


def get_ec2_instance_details(instance_id):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       📋 COMPREHENSIVE INSTANCE INSPECTOR                       │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Retrieves and formats detailed information about a specific EC2 instance.
    This function provides a complete overview of instance configuration, networking,
    and security settings in a human-readable format.
    
    Parameters:
    -----------
    instance_id : str
        The unique identifier of the EC2 instance to inspect
        Format: 'i-1234567890abcdef0'
    
    Returns:
    --------
    dict or None
        Dictionary containing instance details on success, None on failure
        
    Dictionary Keys:
    ---------------
    - Instance ID: Unique instance identifier
    - State: Current operational state
    - Public IP: Internet-facing IP address (if assigned)
    - Private IP: VPC internal IP address
    - Security Groups: List of attached security group names
    - Instance Type: Hardware specification
    - Availability Zone: Physical location within region
    
    Example:
    --------
    >>> details = get_ec2_instance_details('i-1234567890abcdef0')
    >>> if details:
    ...     print(f"Instance Type: {details['Instance Type']}")
    
    Use Cases:
    ----------
    - Troubleshooting connectivity issues
    - Security audits and compliance checks
    - Infrastructure documentation
    - Automated monitoring and alerting
    """
    try:
        # Fetch instance information from AWS
        response = get_ec2_client(AWS_REGION).describe_instances(InstanceIds=[instance_id])
        instance = response["Reservations"][0]["Instances"][0]

        # Extract and organize key instance details
        ec2_details = {
            "Instance ID": instance["InstanceId"],
            "State": instance["State"]["Name"],
            "Public IP": instance.get("PublicIpAddress", "N/A"),
            "Private IP": instance.get("PrivateIpAddress", "N/A"),
            "Security Groups": [sg["GroupName"] for sg in instance["SecurityGroups"]],
            "Instance Type": instance["InstanceType"],
            "Availability Zone": instance["Placement"]["AvailabilityZone"]
        }

        # Display formatted results
        print("📋 EC2 Instance Details Retrieved:")
        print("═" * 50)
        for key, value in ec2_details.items():
            # Add appropriate emoji for visual clarity
            emoji = "🆔" if "ID" in key else "🔄" if "State" in key else "🌐" if "IP" in key else "🔒" if "Security" in key else "⚙️" if "Type" in key else "📍"
            print(f"{emoji} {key}: {value}")

        return ec2_details

    except Exception as e:
        print(f"❌ Failed to fetch EC2 details: {e}")
        return None


def search_high_ram_instances(region=None, memory_threshold=8.0):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      🧠 HIGH MEMORY INSTANCE ANALYZER                           │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Identifies EC2 instances with high memory specifications based on instance types.
    This function helps in resource optimization, cost management, and capacity planning
    by finding memory-intensive instances across your infrastructure.
    
    Parameters:
    -----------
    region : str, optional
        Specific AWS region to search (default: None)
        If None, searches all available regions
    
    memory_threshold : float, optional
        Minimum memory in GB to be considered high RAM (default: 8.0)
        Common thresholds: 4GB (small), 8GB (medium), 16GB (large), 32GB+ (enterprise)
    
    Returns:
    --------
    list
        List of dictionaries containing high-RAM instance details:
        - InstanceId: Unique instance identifier
        - InstanceType: Hardware specification
        - Memory_GB: RAM amount in gigabytes
        - State: Current operational state
        - Region: AWS region location
        - PublicIP/PrivateIP: Network addresses
    
    Instance Types Covered:
    ----------------------
    - T-Series: t2.*, t3.* (Burstable performance)
    - M-Series: m5.* (General purpose)
    - C-Series: c5.* (Compute optimized)
    - R-Series: r5.* (Memory optimized)
    - And more...
    
    Example:
    --------
    >>> high_mem_instances = search_high_ram_instances(memory_threshold=16.0)
    >>> print(f"Found {len(high_mem_instances)} high-memory instances")
    
    Use Cases:
    ----------
    - Cost optimization analysis
    - Resource rightsizing initiatives  
    - Compliance and governance reporting
    - Capacity planning and forecasting
    """
    try:
        if region:
            regions = [region]
        else:
            ec2_client = get_ec2_client(AWS_REGION)
            regions = [r["RegionName"] for r in ec2_client.describe_regions()["Regions"]]
        
        # Common instance types with their memory in GB
        instance_memory = {
            't2.micro': 1, 't2.small': 2, 't2.medium': 4, 't2.large': 8, 't2.xlarge': 16, 't2.2xlarge': 32,
            't3.micro': 1, 't3.small': 2, 't3.medium': 4, 't3.large': 8, 't3.xlarge': 16, 't3.2xlarge': 32,
            'm5.large': 8, 'm5.xlarge': 16, 'm5.2xlarge': 32, 'm5.4xlarge': 64, 'm5.12xlarge': 192, 'm5.24xlarge': 384,
            'c5.large': 4, 'c5.xlarge': 8, 'c5.2xlarge': 16, 'c5.4xlarge': 32, 'c5.9xlarge': 72, 'c5.18xlarge': 144,
            'r5.large': 16, 'r5.xlarge': 32, 'r5.2xlarge': 64, 'r5.4xlarge': 128, 'r5.12xlarge': 384, 'r5.24xlarge': 768
        }
        
        high_ram_instances = []
        
        for reg in regions:
            ec2 = get_ec2_client(reg)
            response = ec2.describe_instances()
            
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance["State"]["Name"] in ["running", "stopped"]:
                        instance_type = instance["InstanceType"]
                        memory_gb = instance_memory.get(instance_type, 0)
                        
                        if memory_gb >= memory_threshold:
                            high_ram_instances.append({
                                "InstanceId": instance["InstanceId"],
                                "InstanceType": instance_type,
                                "Memory_GB": memory_gb,
                                "State": instance["State"]["Name"],
                                "Region": reg,
                                "PublicIP": instance.get("PublicIpAddress", "N/A"),
                                "PrivateIP": instance.get("PrivateIpAddress", "N/A")
                            })
        
        # Display results with beautiful formatting
        if high_ram_instances:
            print(f"\n🧠 ### High Memory Instances (>= {memory_threshold}GB): ###")
            print("═" * 80)
            for inst in high_ram_instances:
                state_emoji = "🟢" if inst['State'] == 'running' else "🔴"
                print(f"{state_emoji} ID: {inst['InstanceId']} | Type: {inst['InstanceType']} | "
                      f"💾 RAM: {inst['Memory_GB']}GB | State: {inst['State']} | 🌍 Region: {inst['Region']}")
        else:
            print(f"🔍 No instances found with RAM >= {memory_threshold}GB")
            
        return high_ram_instances
        
    except ClientError as e:
        print(f"Error searching high RAM instances: {e}")
        return []


def search_high_cpu_instances(region=None, cpu_threshold=4):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                       ⚡ HIGH PERFORMANCE CPU DETECTOR                          │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Discovers EC2 instances with high CPU specifications for compute-intensive workloads.
    This function assists in identifying instances suitable for CPU-bound applications,
    parallel processing, and high-performance computing scenarios.
    
    Parameters:
    -----------
    region : str, optional
        Specific AWS region to search (default: None)
        If None, searches all available regions for comprehensive coverage
    
    cpu_threshold : int, optional
        Minimum number of vCPUs to be considered high CPU (default: 4)
        Common thresholds: 2 (basic), 4 (standard), 8 (high), 16+ (enterprise)
    
    Returns:
    --------
    list
        List of dictionaries containing high-CPU instance details:
        - InstanceId: Unique instance identifier
        - InstanceType: Hardware specification
        - vCPUs: Virtual CPU core count
        - State: Current operational state
        - Region: AWS region location
        - PublicIP/PrivateIP: Network addresses
    
    CPU Categories:
    ---------------
    - Burstable: t2.*, t3.* (Variable performance)
    - General Purpose: m5.* (Balanced compute/memory)
    - Compute Optimized: c5.* (High-performance processors)
    - Memory Optimized: r5.* (High CPU with more memory)
    
    Example:
    --------
    >>> cpu_instances = search_high_cpu_instances(cpu_threshold=8)
    >>> for inst in cpu_instances:
    ...     print(f"High CPU: {inst['InstanceType']} with {inst['vCPUs']} cores")
    
    Use Cases:
    ----------
    - Scientific computing workloads
    - Video processing and encoding
    - Machine learning training
    - Parallel batch processing
    - Web servers under high load
    """
    try:
        if region:
            regions = [region]
        else:
            ec2_client = get_ec2_client(AWS_REGION)
            regions = [r["RegionName"] for r in ec2_client.describe_regions()["Regions"]]
        
        # Common instance types with their vCPU count
        instance_vcpus = {
            't2.micro': 1, 't2.small': 1, 't2.medium': 2, 't2.large': 2, 't2.xlarge': 4, 't2.2xlarge': 8,
            't3.micro': 2, 't3.small': 2, 't3.medium': 2, 't3.large': 2, 't3.xlarge': 4, 't3.2xlarge': 8,
            'm5.large': 2, 'm5.xlarge': 4, 'm5.2xlarge': 8, 'm5.4xlarge': 16, 'm5.12xlarge': 48, 'm5.24xlarge': 96,
            'c5.large': 2, 'c5.xlarge': 4, 'c5.2xlarge': 8, 'c5.4xlarge': 16, 'c5.9xlarge': 36, 'c5.18xlarge': 72,
            'r5.large': 2, 'r5.xlarge': 4, 'r5.2xlarge': 8, 'r5.4xlarge': 16, 'r5.12xlarge': 48, 'r5.24xlarge': 96
        }
        
        high_cpu_instances = []
        
        for reg in regions:
            ec2 = get_ec2_client(reg)
            response = ec2.describe_instances()
            
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance["State"]["Name"] in ["running", "stopped"]:
                        instance_type = instance["InstanceType"]
                        vcpus = instance_vcpus.get(instance_type, 0)
                        
                        if vcpus >= cpu_threshold:
                            high_cpu_instances.append({
                                "InstanceId": instance["InstanceId"],
                                "InstanceType": instance_type,
                                "vCPUs": vcpus,
                                "State": instance["State"]["Name"],
                                "Region": reg,
                                "PublicIP": instance.get("PublicIpAddress", "N/A"),
                                "PrivateIP": instance.get("PrivateIpAddress", "N/A")
                            })
        
        # Display results with enhanced formatting
        if high_cpu_instances:
            print(f"\n⚡ ### High Performance CPU Instances (>= {cpu_threshold} vCPUs): ###")
            print("═" * 85)
            for inst in high_cpu_instances:
                state_emoji = "🟢" if inst['State'] == 'running' else "🔴"
                print(f"{state_emoji} ID: {inst['InstanceId']} | Type: {inst['InstanceType']} | "
                      f"🔥 vCPUs: {inst['vCPUs']} | State: {inst['State']} | 🌍 Region: {inst['Region']}")
        else:
            print(f"🔍 No instances found with vCPUs >= {cpu_threshold}")
            
        return high_cpu_instances
        
    except ClientError as e:
        print(f"Error searching high CPU instances: {e}")
        return []


def search_instances_by_security_group(security_group_id=None, security_group_name=None, region=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                     🔒 SECURITY GROUP ASSOCIATION TRACKER                       │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Identifies all EC2 instances associated with a specific security group for
    security auditing, compliance checking, and network troubleshooting purposes.
    
    Security groups act as virtual firewalls controlling traffic to instances.
    This function helps maintain security posture and track group memberships.
    
    Parameters:
    -----------
    security_group_id : str, optional
        Security group identifier (e.g., 'sg-1234567890abcdef0')
        Takes precedence if both ID and name are provided
    
    security_group_name : str, optional
        Security group name (e.g., 'default', 'web-servers', 'database-tier')
        Used when ID is not specified
    
    region : str, optional
        Specific AWS region to search (default: None)
        If None, searches all available regions
    
    Returns:
    --------
    list
        List of dictionaries containing instance and security group details:
        - InstanceId: Unique instance identifier
        - InstanceType: Hardware specification
        - State: Current operational state
        - Region: AWS region location
        - SecurityGroups: All attached security groups with names and IDs
        - PublicIP/PrivateIP: Network addresses
    
    Security Considerations:
    -----------------------
    - Review instances regularly for proper security group assignment
    - Ensure least-privilege principle in security group rules
    - Monitor for instances with overly permissive groups
    - Validate security group changes don't affect critical services
    
    Example:
    --------
    >>> # Search by security group name
    >>> instances = search_instances_by_security_group(security_group_name='web-servers')
    >>> 
    >>> # Search by security group ID
    >>> instances = search_instances_by_security_group(security_group_id='sg-12345678')
    
    Use Cases:
    ----------
    - Security compliance audits
    - Impact analysis before security group changes
    - Troubleshooting network connectivity issues
    - Documentation of security architecture
    - Incident response and forensics
    """
    if not security_group_id and not security_group_name:
        print("Error: Either security_group_id or security_group_name must be provided")
        return []
        
    try:
        if region:
            regions = [region]
        else:
            ec2_client = get_ec2_client(AWS_REGION)
            regions = [r["RegionName"] for r in ec2_client.describe_regions()["Regions"]]
        
        instances_with_sg = []
        
        for reg in regions:
            ec2 = get_ec2_client(reg)
            response = ec2.describe_instances()
            
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance["State"]["Name"] in ["running", "stopped", "pending"]:
                        security_groups = instance["SecurityGroups"]
                        
                        # Check if instance uses the specified security group
                        sg_match = False
                        for sg in security_groups:
                            if (security_group_id and sg["GroupId"] == security_group_id) or \
                               (security_group_name and sg["GroupName"] == security_group_name):
                                sg_match = True
                                break
                        
                        if sg_match:
                            instances_with_sg.append({
                                "InstanceId": instance["InstanceId"],
                                "InstanceType": instance["InstanceType"],
                                "State": instance["State"]["Name"],
                                "Region": reg,
                                "SecurityGroups": [f"{sg['GroupName']} ({sg['GroupId']})" for sg in security_groups],
                                "PublicIP": instance.get("PublicIpAddress", "N/A"),
                                "PrivateIP": instance.get("PrivateIpAddress", "N/A")
                            })
        
        # Display results with comprehensive formatting
        search_term = security_group_id if security_group_id else security_group_name
        if instances_with_sg:
            print(f"\n🔒 ### Instances using Security Group '{search_term}': ###")
            print("═" * 90)
            for inst in instances_with_sg:
                state_emoji = "🟢" if inst['State'] == 'running' else "🔴"
                print(f"{state_emoji} ID: {inst['InstanceId']} | Type: {inst['InstanceType']} | "
                      f"State: {inst['State']} | 🌍 Region: {inst['Region']}")
                print(f"   🛡️  Security Groups: {', '.join(inst['SecurityGroups'])}")
        else:
            print(f"🔍 No instances found using security group '{search_term}'")
            
        return instances_with_sg
        
    except ClientError as e:
        print(f"Error searching instances by security group: {e}")
        return []


def search_instances_with_memory_issues(region=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                    🚨 MEMORY HEALTH & PERFORMANCE ANALYZER                      │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Proactively identifies EC2 instances with potential memory-related issues to
    prevent performance degradation, application failures, and system instability.
    
    This comprehensive analysis helps maintain optimal system performance and
    prevents memory-related outages before they impact production workloads.
    
    Detection Criteria:
    ------------------
    🔍 Low Memory Instance Types:
        - t1.micro, t2.nano, t2.micro, t3.nano, t3.micro
        - Instances with < 1GB RAM that may struggle with modern workloads
    
    🔍 Legacy Generation Instances:
        - Previous generation instances (t1.*, m1.*, c1.*, m2.*)
        - May have memory architecture limitations
    
    🔍 Long-Running Small Instances:
        - t2.micro instances running > 7 days
        - Potential memory leaks in applications
        - Accumulated memory fragmentation
    
    Parameters:
    -----------
    region : str, optional
        Specific AWS region to analyze (default: None)
        If None, performs comprehensive multi-region analysis
    
    Returns:
    --------
    list
        List of dictionaries containing problematic instances:
        - InstanceId: Unique instance identifier
        - InstanceType: Hardware specification
        - State: Current operational state
        - Region: AWS region location
        - Issues: List of identified memory concerns
        - LaunchTime: Instance startup timestamp
        - PublicIP/PrivateIP: Network addresses
    
    Recommended Actions:
    -------------------
    - Upgrade to newer generation instances
    - Increase instance size for memory-constrained workloads
    - Implement application memory monitoring
    - Schedule regular instance restarts for long-running small instances
    - Review application memory usage patterns
    
    Example:
    --------
    >>> problematic_instances = search_instances_with_memory_issues()
    >>> for inst in problematic_instances:
    ...     print(f"⚠️  {inst['InstanceId']}: {', '.join(inst['Issues'])}")
    
    Monitoring Integration:
    ----------------------
    Consider integrating with:
    - CloudWatch memory metrics
    - Application performance monitoring (APM)
    - Custom memory usage dashboards
    - Automated alerting systems
    """
    try:
        if region:
            regions = [region]
        else:
            ec2_client = get_ec2_client(AWS_REGION)
            regions = [r["RegionName"] for r in ec2_client.describe_regions()["Regions"]]
        
        # Define problematic configurations
        low_memory_types = ['t1.micro', 't2.nano', 't2.micro', 't3.nano', 't3.micro']
        old_generation_types = ['t1.micro', 'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge', 
                              'c1.medium', 'c1.xlarge', 'm2.xlarge', 'm2.2xlarge', 'm2.4xlarge']
        
        instances_with_issues = []
        
        for reg in regions:
            ec2 = get_ec2_client(reg)
            
            # Get CloudWatch client for memory metrics (if available)
            try:
                cloudwatch = boto3.client(
                    "cloudwatch",
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY,
                    region_name=reg
                )
            except:
                cloudwatch = None
            
            response = ec2.describe_instances()
            
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance["State"]["Name"] in ["running", "stopped"]:
                        instance_type = instance["InstanceType"]
                        instance_id = instance["InstanceId"]
                        
                        issues = []
                        
                        # Check for low memory instance types
                        if instance_type in low_memory_types:
                            issues.append("Low memory instance type")
                        
                        # Check for old generation instances
                        if instance_type in old_generation_types:
                            issues.append("Old generation instance type")
                        
                        # Check for small instances running for long time (potential memory leak)
                        launch_time = instance.get("LaunchTime")
                        if launch_time and instance_type.startswith('t2.micro'):
                            # If instance has been running for more than 7 days, it might have memory issues
                            from datetime import datetime, timezone                            
                            days_running = (datetime.now(timezone.utc) - launch_time).days
                            if days_running > 7:
                                issues.append(f"Small instance running for {days_running} days (potential memory leak)")
                        
                        if issues:
                            instances_with_issues.append({
                                "InstanceId": instance_id,
                                "InstanceType": instance_type,
                                "State": instance["State"]["Name"],
                                "Region": reg,
                                "Issues": issues,
                                "LaunchTime": instance.get("LaunchTime", "N/A"),
                                "PublicIP": instance.get("PublicIpAddress", "N/A"),
                                "PrivateIP": instance.get("PrivateIpAddress", "N/A")
                            })
        
        # Display results with comprehensive health indicators
        if instances_with_issues:
            print("\n🚨 ### Instances with Potential Memory Issues: ###")
            print("═" * 95)
            for inst in instances_with_issues:
                state_emoji = "🟢" if inst['State'] == 'running' else "🔴"
                severity = "🔥" if len(inst['Issues']) > 1 else "⚠️"
                
                print(f"{severity} {state_emoji} ID: {inst['InstanceId']} | Type: {inst['InstanceType']} | "
                      f"State: {inst['State']} | 🌍 Region: {inst['Region']}")
                print(f"     📋 Issues: {', '.join(inst['Issues'])}")
                if inst['LaunchTime'] != "N/A":
                    print(f"     ⏰ Launch Time: {inst['LaunchTime']}")
                print()  # Add spacing between instances
        else:
            print("✅ No instances found with obvious memory issues - System health looks good!")
            
        return instances_with_issues
        
    except ClientError as e:
        print(f"Error searching instances with memory issues: {e}")
        return []
    

if __name__ == "__main__":
    AMI_ID = "ami-00bb6a80f01f03502"
    INSTANCE_TYPE = "t2.micro"
    KEY_NAME = "fsd_feb15"

    #instance_id = "i-0c29c13557e3d4a18"
    # instance_id = create_instance(AMI_ID, INSTANCE_TYPE, KEY_NAME)
    list_instances_by_region()
    # list_instances_by_region("us-west-2")
    # start_instance(instance_id)
    # stop_instance(instance_id)
    # terminate_instance(instance_id)
    # get_ec2_instance_details(instance_id)
    
    # ═══════════════════════════════════════════════════════════════════════════════════
    #                           🔍 ADVANCED SEARCH EXAMPLES
    # ═══════════════════════════════════════════════════════════════════════════════════
    print("\n" + "🌟 " + "="*70 + " 🌟")
    print("           🔍 ADVANCED EC2 INSTANCE SEARCH & ANALYSIS SUITE")
    print("🌟 " + "="*70 + " 🌟")
    
    # 🧠 1. High Memory Instance Discovery
    # Uncomment to find memory-intensive instances (useful for cost optimization)
    # search_high_ram_instances(memory_threshold=8.0)
    
    # ⚡ 2. High Performance CPU Detection  
    # Uncomment to identify compute-intensive instances (great for performance analysis)
    # search_high_cpu_instances(cpu_threshold=4)
    
    # 🔒 3. Security Group Association Analysis
    # Uncomment to audit security group memberships (essential for security compliance)
    # search_instances_by_security_group(security_group_name="default")
    # search_instances_by_security_group(security_group_id="sg-xxxxxxxxx")
    
    # 🚨 4. Memory Health & Performance Check
    # Uncomment to identify potential memory issues (proactive health monitoring)
    # search_instances_with_memory_issues()
    
    print("\n💡 Tip: Uncomment the methods above to run specific searches!")
    print("🎯 Each method supports region-specific or multi-region analysis.")
    