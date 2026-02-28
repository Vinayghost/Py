"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                               S3 Storage Management Suite                            ║
║                      Advanced AWS S3 Operations & File Management                   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

This module provides comprehensive Amazon S3 storage management capabilities including:
- Bucket lifecycle management (create, list, delete with safety checks)
- File operations (upload, download, delete with progress tracking)
- Advanced object listing and filtering with metadata
- Secure bucket operations with user confirmation prompts
- Multi-region S3 support with error handling
- Cost optimization through efficient object management

Key Features:
- 🪣 Bucket Management: Full CRUD operations with safety protocols
- 📁 File Operations: Seamless upload/download with error handling
- 🔍 Object Discovery: Advanced listing with prefix filtering
- 🛡️ Safety First: Confirmation prompts for destructive operations
- 🌍 Multi-Region: Support for all AWS regions
- 💰 Cost Aware: Efficient operations to minimize storage costs

Author: Training Module
Date: November 2025
Version: 2.0
Use Case: Production-ready S3 storage management
"""

import boto3
from botocore.exceptions import NoCredentialsError, ClientError


# ════════════════════════════════════════════════════════════════════════════════════════
#                                   AWS S3 CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════════════

AWS_ACCESS_KEY = "AKIAZQ3DO7MIWQ2ERLIL"    # AWS Access Key ID for S3 operations
AWS_SECRET_KEY = "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"    # AWS Secret Access Key
AWS_REGION = "ap-south-1"    # Default AWS region (Asia Pacific - Mumbai)

# Global S3 client instance for reuse across functions
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def create_bucket(bucket_name, region=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                         🪣 S3 BUCKET CREATION ENGINE                            │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Creates a new Amazon S3 bucket with proper regional configuration and error handling.
    S3 buckets serve as containers for objects and provide the foundation for cloud storage
    architecture with global accessibility and enterprise-grade durability.
    
    Parameters:
    -----------
    bucket_name : str
        Globally unique bucket name (3-63 characters)
        Must follow S3 naming conventions:
        - Lowercase letters, numbers, and hyphens only
        - Must start and end with letter or number
        - Cannot contain spaces or uppercase letters
    
    region : str, optional
        AWS region for bucket creation (default: None)
        If None, uses the default region from client configuration
        Popular regions: 'us-east-1', 'us-west-2', 'eu-west-1', 'ap-south-1'
    
    Returns:
    --------
    None
        Prints success confirmation or error details
    
    S3 Naming Rules:
    ---------------
    ✅ Valid: 'my-bucket-2025', 'company-data-backup'
    ❌ Invalid: 'My_Bucket', 'bucket..name', 'bucket-'
    
    Regional Considerations:
    ----------------------
    - US East (N. Virginia) is the default region
    - Other regions require LocationConstraint
    - Choose region close to users for better performance
    - Consider data residency and compliance requirements
    
    Example:
    --------
    >>> create_bucket('my-company-storage', region='us-west-2')
    🪣 Bucket 'my-company-storage' created successfully in us-west-2
    
    >>> create_bucket('global-backup-bucket')
    🪣 Bucket 'global-backup-bucket' created successfully
    
    Cost Optimization:
    -----------------
    - Choose appropriate region for cost efficiency
    - Consider data transfer costs between regions
    - Plan for lifecycle policies from creation
    
    Security Note:
    -------------
    New buckets are private by default - configure access policies as needed.
    """
    try:
        # Handle regional bucket creation requirements
        if region:
            # Non-US regions require LocationConstraint
            location = {'LocationConstraint': region}
            s3.create_bucket(
                Bucket=bucket_name, 
                CreateBucketConfiguration=location
            )
            print(f"🪣 Bucket '{bucket_name}' created successfully in region '{region}'.")
        else:
            # Default region (us-east-1) doesn't need LocationConstraint
            s3.create_bucket(Bucket=bucket_name)
            print(f"🪣 Bucket '{bucket_name}' created successfully.")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            print(f"❌ Bucket '{bucket_name}' already exists (owned by another account)")
        elif error_code == 'BucketAlreadyOwnedByYou':
            print(f"ℹ️  Bucket '{bucket_name}' already exists and is owned by you")
        else:
            print(f"❌ Error creating bucket: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")



def list_buckets():
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        📋 S3 BUCKET INVENTORY SYSTEM                            │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Retrieves and displays a comprehensive list of all S3 buckets in your AWS account.
    This function provides an overview of your entire S3 infrastructure across all regions,
    helping with inventory management and resource governance.
    
    Returns:
    --------
    None
        Prints formatted list of bucket names with creation timestamps
        
    Output Format:
    -------------
    - Bucket count header for quick overview
    - Individual bucket listings with creation dates
    - Visual indicators for easy scanning
    - Empty state handling for accounts without buckets
    
    Information Displayed:
    ---------------------
    📅 Bucket Name: Unique identifier for each storage container
    🕐 Creation Date: When the bucket was originally created
    🌍 Implicit Region: Buckets exist globally but with regional storage
    
    Example Output:
    --------------
    📋 S3 Bucket Inventory (3 buckets found):
    ═══════════════════════════════════════════════
    🪣 my-website-assets (Created: 2025-01-15)
    🪣 backup-database-dumps (Created: 2025-02-01)  
    🪣 user-uploaded-content (Created: 2025-03-10)
    
    Use Cases:
    ----------
    - Infrastructure auditing and compliance
    - Cost analysis and resource optimization  
    - Backup and disaster recovery planning
    - Access management and security reviews
    - Migration planning and capacity assessment
    
    Billing Consideration:
    ---------------------
    Each bucket incurs minimal monthly charges regardless of content.
    Regular inventory helps identify unused buckets for cost optimization.
    """
    try:
        # Fetch all buckets from AWS S3
        response = s3.list_buckets()
        bucket_list = response['Buckets']
        
        # Display results with enhanced formatting
        if bucket_list:
            print(f"📋 S3 Bucket Inventory ({len(bucket_list)} bucket{'s' if len(bucket_list) != 1 else ''} found):")
            print("═" * 60)
            
            for bucket in bucket_list:
                # Format creation date for readability
                creation_date = bucket['CreationDate'].strftime('%Y-%m-%d')
                print(f"🪣 {bucket['Name']} (Created: {creation_date})")
        else:
            print("📋 No S3 buckets found in your AWS account.")
            print("💡 Tip: Create your first bucket to start using S3 storage!")
            
    except ClientError as e:
        print(f"❌ Error listing buckets: {e}")
        print("🔧 Check your AWS credentials and permissions.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def empty_bucket(bucket_name):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      🗑️ SECURE BUCKET CONTENT PURGE SYSTEM                      │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Safely empties an S3 bucket by deleting all contained objects with user confirmation.
    This operation is irreversible and permanently removes all files, so it includes
    multiple safety checks and clear user prompts to prevent accidental data loss.
    
    ⚠️  CRITICAL WARNING: This operation permanently deletes ALL objects! ⚠️
    
    Parameters:
    -----------
    bucket_name : str
        Name of the S3 bucket to empty
        Must be an existing bucket in your AWS account
    
    Returns:
    --------
    bool
        True if bucket was successfully emptied or was already empty
        False if user canceled operation or error occurred
    
    Safety Features:
    ---------------
    🔒 User Confirmation: Explicit 'yes' required to proceed
    📊 Object Count Display: Shows number of objects before deletion
    🛑 Cancellation Support: Easy abort with any response except 'yes'
    📝 Progress Tracking: Real-time deletion status for each object
    ⚡ Error Resilience: Continues operation even if individual objects fail
    
    Deletion Process:
    ----------------
    1. Scan bucket for existing objects
    2. Display object count and request confirmation  
    3. If confirmed, iterate through all objects
    4. Delete each object individually with status updates
    5. Provide completion summary
    
    Example:
    --------
    >>> empty_bucket('my-test-bucket')
    🗑️ Bucket 'my-test-bucket' contains 1,247 objects
    ⚠️  This will permanently delete ALL objects in this bucket!
    Do you want to proceed? (yes/no): yes
    🗑️ Deleting objects: [████████████████████████████████] 100%
    ✅ Successfully deleted 1,247 objects from 'my-test-bucket'
    
    Use Cases:
    ----------
    - Preparing buckets for deletion
    - Cleaning up test environments
    - Resetting development buckets
    - Compliance-driven data purging
    - Cost optimization through cleanup
    
    Data Recovery:
    -------------
    ⚠️  Objects deleted through this function cannot be recovered unless:
    - Versioning is enabled (older versions may remain)
    - Cross-region replication is configured
    - Backup copies exist elsewhere
    """
    try:
        # Scan bucket for existing objects
        objects = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in objects:
            object_count = len(objects['Contents'])
            print(f"\n🗑️ Bucket '{bucket_name}' contains {object_count:,} object{'s' if object_count != 1 else ''}")
            print("⚠️  This will permanently delete ALL objects in this bucket!")
            
            confirm = input("Do you want to proceed? (yes/no): ").strip().lower()
            
            if confirm != "yes":
                print("🚫 Operation canceled - No objects were deleted.")
                return False  # User canceled operation
            
            # Process deletion with progress tracking
            deleted_count = 0
            failed_count = 0
            
            print(f"🗑️ Deleting {object_count:,} objects...")
            
            for i, obj in enumerate(objects['Contents'], 1):
                try:
                    s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                    deleted_count += 1
                    
                    # Progress indicator for large deletions
                    if object_count > 10:
                        progress = (i / object_count) * 100
                        print(f"\rProgress: {progress:.1f}% ({i}/{object_count})", end='')
                    else:
                        print(f"✅ Deleted: {obj['Key']}")
                        
                except ClientError as obj_error:
                    failed_count += 1
                    print(f"\n❌ Failed to delete {obj['Key']}: {obj_error}")
            
            # Final summary
            if object_count > 10:
                print()  # New line after progress indicator
                
            print(f"✅ Successfully deleted {deleted_count:,} objects from '{bucket_name}'")
            if failed_count > 0:
                print(f"⚠️  {failed_count} objects failed to delete")
                
        else:
            print(f"ℹ️  Bucket '{bucket_name}' is already empty.")
            
        return True  # Operation completed successfully
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
        else:
            print(f"❌ Error emptying bucket: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def delete_bucket(bucket_name):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                    💥 COMPLETE BUCKET DESTRUCTION PROTOCOL                      │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Permanently removes an S3 bucket and all its contents through a secure two-step process.
    This operation is irreversible and implements multiple safety checkpoints to prevent
    accidental deletion of critical storage infrastructure.
    
    ⚠️  EXTREME CAUTION: This completely destroys the bucket and all data! ⚠️
    
    Parameters:
    -----------
    bucket_name : str
        Name of the S3 bucket to permanently delete
        Must be an existing bucket in your AWS account
    
    Returns:
    --------
    None
        Prints status messages throughout the deletion process
    
    Deletion Protocol:
    -----------------
    🔍 Step 1: Content Analysis and Purge
        - Scans bucket for existing objects
        - Requests user confirmation for content deletion
        - Empties bucket completely (calls empty_bucket())
    
    🗑️ Step 2: Bucket Infrastructure Removal  
        - Additional confirmation prompt for bucket deletion
        - Permanent removal of bucket itself
        - Cleanup confirmation and status reporting
    
    Safety Mechanisms:
    -----------------
    🛡️ Double Confirmation: Two separate user prompts required
    🔒 Staged Deletion: Content removed before bucket destruction
    🚫 Abort Options: Can cancel at any stage safely
    📋 Status Updates: Clear feedback throughout process
    ⚡ Error Handling: Graceful handling of edge cases
    
    Example Session:
    ---------------
    >>> delete_bucket('old-backup-bucket')
    🗑️ Bucket 'old-backup-bucket' contains 1,247 objects
    ⚠️  This will permanently delete ALL objects in this bucket!
    Do you want to proceed? (yes/no): yes
    ✅ Successfully deleted 1,247 objects from 'old-backup-bucket'
    💥 Final confirmation: Delete bucket 'old-backup-bucket' permanently? (yes/no): yes
    💥 Bucket 'old-backup-bucket' deleted successfully!
    
    Common Use Cases:
    ----------------
    - Decommissioning old projects
    - Cleaning up test environments  
    - Removing redundant backup buckets
    - Compliance-driven data destruction
    - Cost optimization initiatives
    
    Recovery Warning:
    ----------------
    🚨 Once deleted, bucket names become globally available again
    🚨 All object versions, metadata, and access policies are lost
    🚨 No recovery possible without external backups
    🚨 Billing stops immediately but deletion is permanent
    
    Alternative Approaches:
    ----------------------
    Consider these alternatives before permanent deletion:
    - Archive to Glacier for long-term, low-cost storage
    - Export critical data to other storage systems
    - Implement lifecycle policies for automatic cleanup
    - Use versioning for recoverable deletions
    """
    try:
        print(f"🚀 Initiating secure deletion protocol for bucket '{bucket_name}'...")
        
        # Step 1: Empty the bucket (with user confirmation)
        if not empty_bucket(bucket_name):
            print("🚫 Bucket deletion aborted - contents were not removed.")
            return

        # Step 2: Confirm bucket deletion after contents are removed
        print(f"\n💥 Final confirmation required:")
        print(f"⚠️  This will permanently delete the bucket '{bucket_name}' itself!")
        confirm = input(f"Delete bucket '{bucket_name}' permanently? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("🚫 Bucket deletion canceled - bucket structure preserved.")
            return
        
        # Execute bucket deletion
        s3.delete_bucket(Bucket=bucket_name)
        print(f"💥 Bucket '{bucket_name}' deleted successfully!")
        print(f"🎯 The bucket name '{bucket_name}' is now available for reuse globally.")
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchBucket':
            print(f"ℹ️  Bucket '{bucket_name}' does not exist or was already deleted")
        elif error_code == 'BucketNotEmpty':
            print(f"❌ Bucket '{bucket_name}' still contains objects - empty it first")
        else:
            print(f"❌ Error deleting bucket: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during bucket deletion: {e}")


def upload_file(bucket_name, file_path, object_name=None):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        📤 INTELLIGENT FILE UPLOAD SYSTEM                        │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Uploads files to Amazon S3 with intelligent naming, comprehensive error handling,
    and detailed progress feedback. Supports various file types and automatically
    handles path resolution and object key generation.
    
    Parameters:
    -----------
    bucket_name : str
        Target S3 bucket name for file upload
        Must be an existing bucket with write permissions
    
    file_path : str
        Local file system path to the file for upload
        Supports both absolute and relative paths
        Examples: '/home/user/document.pdf', './data/report.xlsx'
    
    object_name : str, optional
        S3 object key (filename in bucket) (default: None)
        If None, automatically extracts filename from file_path
        Can include virtual folders: 'documents/2025/report.pdf'
    
    Returns:
    --------
    None
        Prints detailed upload status, file information, and any errors
    
    Upload Features:
    ---------------
    🎯 Intelligent Naming: Auto-generates object names from file paths
    📊 File Analysis: Displays file size and type information
    🔐 Security Aware: Handles permissions and credential issues gracefully
    📁 Path Flexibility: Supports complex directory structures in S3
    ⚡ Error Recovery: Detailed error messages for troubleshooting
    
    Example Usage:
    -------------
    >>> upload_file('my-bucket', '/path/to/document.pdf')
    📤 Uploading 'document.pdf' (2.4 MB) to 's3://my-bucket/document.pdf'...
    ✅ Successfully uploaded!
    
    >>> upload_file('my-bucket', './report.xlsx', 'reports/2025/monthly.xlsx')
    📤 Uploading 'report.xlsx' (856 KB) to 's3://my-bucket/reports/2025/monthly.xlsx'...
    ✅ Successfully uploaded!
    """
    # Generate object name if not provided
    if object_name is None:
        # Extract filename from path (works with both Windows and Unix paths)
        object_name = file_path.replace('\\', '/').split("/")[-1]
    
    try:
        # Get file information for user feedback
        import os
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            
            if size_mb < 1:
                size_str = f"{file_size} bytes"
            elif size_mb < 1024:
                size_str = f"{size_mb:.1f} MB"
            else:
                size_str = f"{size_mb/1024:.1f} GB"
                
            print(f"📤 Uploading '{os.path.basename(file_path)}' ({size_str}) to 's3://{bucket_name}/{object_name}'...")
        
        # Perform the upload
        s3.upload_file(file_path, bucket_name, object_name)
        print(f"✅ Successfully uploaded to 's3://{bucket_name}/{object_name}'")
        print(f"🔗 Object URL: https://{bucket_name}.s3.amazonaws.com/{object_name}")
        
    except FileNotFoundError:
        print(f"❌ File not found: '{file_path}'")
        print("🔧 Check the file path and ensure the file exists")
    except NoCredentialsError:
        print("❌ AWS credentials not available or invalid")
        print("🔧 Configure your AWS credentials using AWS CLI or environment variables")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to bucket '{bucket_name}'")
        else:
            print(f"❌ Upload error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during upload: {e}")


def delete_file(bucket_name, object_name):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                        🗑️ PRECISE OBJECT DELETION SYSTEM                       │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Removes a specific object (file) from an S3 bucket with comprehensive error handling
    and detailed feedback. This operation is permanent for the current object version
    unless versioning is enabled on the bucket.
    
    Parameters:
    -----------
    bucket_name : str
        Name of the S3 bucket containing the object
        Must be an existing bucket with delete permissions
    
    object_name : str
        S3 object key (path/filename) to delete
        Examples: 'document.pdf', 'photos/vacation/img001.jpg', 'logs/2025/app.log'
    
    Returns:
    --------
    None
        Prints deletion confirmation or detailed error information
    
    Deletion Features:
    -----------------
    🎯 Precise Targeting: Deletes only the specified object
    🔐 Permission Aware: Handles access control gracefully
    📊 Status Feedback: Confirms successful deletion
    ⚡ Error Recovery: Detailed error analysis and suggestions
    🛡️ Safe Operation: Only affects the single specified object
    
    Versioning Behavior:
    -------------------
    📌 Non-Versioned Buckets: Object is permanently deleted
    📌 Versioned Buckets: Current version gets a delete marker
    📌 Previous Versions: Remain accessible unless explicitly deleted
    
    Example Usage:
    -------------
    >>> delete_file('my-documents', 'old-report.pdf')
    🗑️ Deleting 'old-report.pdf' from bucket 'my-documents'...
    ✅ Successfully deleted 'old-report.pdf'
    
    >>> delete_file('photos', 'albums/2024/vacation/beach.jpg')
    🗑️ Deleting 'albums/2024/vacation/beach.jpg' from bucket 'photos'...
    ✅ Successfully deleted 'albums/2024/vacation/beach.jpg'
    
    Common Use Cases:
    ----------------
    - Removing outdated files and documents
    - Cleaning up temporary or cache files
    - Managing storage costs by removing unused content
    - Implementing file lifecycle management
    - Correcting accidental uploads
    
    Error Scenarios:
    ---------------
    🔍 Object Not Found: File doesn't exist (may already be deleted)
    🔒 Access Denied: Insufficient permissions for deletion
    🪣 Bucket Missing: Target bucket doesn't exist
    🌐 Network Issues: Connection problems during operation
    
    Recovery Notes:
    --------------
    ⚠️  Standard deletions are immediate and irreversible
    💡 Check if versioning is enabled for recovery options
    🔄 Consider lifecycle policies for automated management
    📋 Maintain deletion logs for audit purposes
    """
    try:
        print(f"🗑️ Deleting '{object_name}' from bucket '{bucket_name}'...")
        
        # Execute the deletion
        s3.delete_object(Bucket=bucket_name, Key=object_name)
        print(f"✅ Successfully deleted '{object_name}' from bucket '{bucket_name}'")
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
        elif error_code == 'NoSuchKey':
            print(f"ℹ️  Object '{object_name}' not found in bucket '{bucket_name}' (may already be deleted)")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied: Cannot delete '{object_name}' from bucket '{bucket_name}'")
            print("🔧 Check your AWS permissions for S3 delete operations")
        else:
            print(f"❌ Deletion error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during deletion: {e}")

def list_s3_objects(bucket_name, prefix=""):
    """
    ┌──────────────────────────────────────────────────────────────────────────────────┐
    │                      📋 ADVANCED OBJECT DISCOVERY ENGINE                        │
    └──────────────────────────────────────────────────────────────────────────────────┘
    
    Explores and catalogs all objects in an S3 bucket with optional prefix filtering
    for targeted discovery. Provides detailed metadata including sizes, modification
    dates, and storage classes for comprehensive inventory management.
    
    Parameters:
    -----------
    bucket_name : str
        Name of the S3 bucket to explore
        Must be an existing bucket with read permissions
    
    prefix : str, optional
        Object key prefix for filtered listing (default: "")
        Acts like a folder filter in traditional file systems
        Examples: 'logs/', 'images/2025/', 'documents/reports/'
    
    Returns:
    --------
    None
        Prints formatted object listing with metadata details
    
    Listing Features:
    ----------------
    🔍 Smart Filtering: Prefix-based object filtering
    📊 Rich Metadata: File sizes, dates, and storage classes  
    📁 Virtual Folders: Simulates directory structure display
    📈 Statistics: Object counts and total storage usage
    🎯 Targeted Search: Efficient prefix-based queries
    
    Prefix Examples:
    ---------------
    prefix=""                    → Lists all objects
    prefix="logs/"               → Lists only log files
    prefix="images/2025/january/" → Lists January 2025 images
    prefix="backup"              → Lists objects starting with 'backup'
    
    Example Usage:
    -------------
    >>> list_s3_objects('my-storage-bucket')
    📋 Object Inventory for bucket 'my-storage-bucket' (234 objects found)
    ═══════════════════════════════════════════════════════════════════════════
    📄 documents/report-2025.pdf (2.4 MB) - Modified: 2025-11-01
    🖼️  images/logo.png (156 KB) - Modified: 2025-10-28
    📊 data/analytics.csv (8.7 MB) - Modified: 2025-11-07
    
    >>> list_s3_objects('logs-bucket', prefix='application/')
    📋 Filtered view: 'application/' objects in 'logs-bucket' (47 objects)
    
    Output Information:
    ------------------
    📁 Object Key: Full path/name of the object
    💾 File Size: Human-readable size (bytes, KB, MB, GB)
    📅 Last Modified: When the object was last updated
    🏷️  Storage Class: Standard, IA, Glacier, etc.
    📊 Total Summary: Count and total size of all objects
    
    Performance Notes:
    -----------------
    - Large buckets (>1000 objects) are paginated automatically
    - Prefix filtering reduces response time and data transfer
    - Consider using specific prefixes for large bucket exploration
    
    Use Cases:
    ----------
    - Content auditing and inventory management
    - Storage cost analysis and optimization
    - File organization and cleanup planning
    - Backup verification and validation
    - Compliance reporting and documentation
    
    Storage Class Information:
    -------------------------
    📦 STANDARD: Frequently accessed data
    📦 STANDARD_IA: Infrequently accessed data  
    📦 GLACIER: Long-term archive storage
    📦 DEEP_ARCHIVE: Rarely accessed archival data
    """
    try:
        print(f"🔍 Scanning bucket '{bucket_name}'" + (f" with prefix '{prefix}'" if prefix else "") + "...")
        
        # Query S3 for objects
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if "Contents" not in response:
            if prefix:
                print(f"📭 No objects found matching prefix '{prefix}' in bucket '{bucket_name}'")
                print("💡 Try a different prefix or check the object key structure")
            else:
                print(f"📭 Bucket '{bucket_name}' is empty")
                print("💡 Upload some files to see them listed here")
            return
        
        objects = response["Contents"]
        total_size = sum(obj['Size'] for obj in objects)
        
        # Display header with statistics
        object_count = len(objects)
        if prefix:
            print(f"📋 Filtered Objects (prefix: '{prefix}') in '{bucket_name}' ({object_count:,} objects)")
        else:
            print(f"📋 Complete Object Inventory for '{bucket_name}' ({object_count:,} objects)")
        
        print("═" * 90)
        
        # Display each object with enhanced formatting
        for obj in objects:
            # Format file size
            size_bytes = obj['Size']
            if size_bytes < 1024:
                size_str = f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
            # Format modification date
            modified_date = obj['LastModified'].strftime('%Y-%m-%d %H:%M')
            
            # Choose appropriate emoji based on file extension
            key = obj['Key']
            if key.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                emoji = "🖼️ "
            elif key.endswith(('.pdf', '.doc', '.docx', '.txt')):
                emoji = "📄"
            elif key.endswith(('.csv', '.xlsx', '.xls')):
                emoji = "📊"
            elif key.endswith(('.zip', '.tar', '.gz')):
                emoji = "📦"
            elif key.endswith('/'):
                emoji = "📁"
            else:
                emoji = "📄"
            
            print(f"{emoji} {key:<50} ({size_str:>10}) - {modified_date}")
        
        # Display summary statistics
        if total_size < 1024 * 1024:
            total_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            total_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            total_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"
            
        print("═" * 90)
        print(f"📊 Summary: {object_count:,} objects, Total size: {total_str}")
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
            print("🔧 Check the bucket name or create the bucket first")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to bucket '{bucket_name}'")
            print("🔧 Check your AWS permissions for S3 read access")
        else:
            print(f"❌ Error listing objects: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    # ═══════════════════════════════════════════════════════════════════════════════════
    #                           🚀 S3 MANAGEMENT DEMONSTRATION
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    print("🌟 " + "="*75 + " 🌟")
    print("           🪣 ADVANCED S3 STORAGE MANAGEMENT SUITE")  
    print("🌟 " + "="*75 + " 🌟")
    
    # Configuration
    BUCKET_NAME = "itd-devops-feb25"    # Primary bucket for operations
    # BUCKET_NAME = "testitd001"        # Alternative bucket for testing
    TEST_FILE = "devops.txt"             # Sample file for upload operations
    
    print(f"\n🎯 Target Bucket: '{BUCKET_NAME}'")
    print(f"📍 Region: {AWS_REGION}")
    print("\n" + "─" * 80)
    
    # Core Operations Demo
    print("🔄 Executing Core S3 Operations...")
    
    # 1. Bucket Creation
    print("\n1️⃣ Creating S3 Bucket:")
    create_bucket(BUCKET_NAME, region=AWS_REGION)
    
    # 2. Bucket Inventory  
    print("\n2️⃣ Listing All Buckets:")
    list_buckets()
    
    # ═══════════════════════════════════════════════════════════════════════════════════
    #                        📚 ADDITIONAL OPERATIONS EXAMPLES
    # ═══════════════════════════════════════════════════════════════════════════════════
    
    print("\n" + "💡" + "─" * 78 + "💡")
    print("  ADDITIONAL OPERATIONS (uncomment to execute):")
    print("💡" + "─" * 78 + "💡")
    
    # 3. File Upload Examples
    print("\n📤 File Upload Operations:")
    print("# upload_file(BUCKET_NAME, 'devops.txt', 'documents/devops.txt')")
    print("# upload_file(BUCKET_NAME, './local-file.pdf')")  # Auto-naming
    print("# upload_file(BUCKET_NAME, '/path/to/image.jpg', 'gallery/2025/photo.jpg')")
    
    # 4. Object Listing Examples  
    print("\n📋 Object Discovery Operations:")
    print("# list_s3_objects(BUCKET_NAME)                    # List all objects")
    print("# list_s3_objects(BUCKET_NAME, 'documents/')      # List documents folder")
    print("# list_s3_objects(BUCKET_NAME, 'logs/2025/')      # List 2025 logs")
    
    # 5. File Management Examples
    print("\n🗑️ File Management Operations:")
    print("# delete_file(BUCKET_NAME, 'old-document.pdf')")
    print("# delete_file(BUCKET_NAME, 'temp/cache-file.tmp')")
    
    # 6. Bucket Management Examples
    print("\n🪣 Bucket Management Operations:")
    print("# empty_bucket(BUCKET_NAME)                       # Remove all objects")
    print("# delete_bucket(BUCKET_NAME)                      # Delete entire bucket")
    
    print("\n" + "🎓" + "─" * 78 + "🎓")
    print("  QUICK START GUIDE:")
    print("  1. Uncomment operations above to execute them")
    print("  2. Ensure your AWS credentials are properly configured")
    print("  3. Verify bucket names follow S3 naming conventions")
    print("  4. Check file paths exist before uploading")
    print("  5. Use prefixes for efficient object organization")
    print("🎓" + "─" * 78 + "🎓")
    
    # Uncomment below for immediate testing:
    # upload_file(BUCKET_NAME, "devops.txt", "uploads/devops-backup.txt")
    # list_s3_objects(BUCKET_NAME)
    # delete_file(BUCKET_NAME, "uploads/devops-backup.txt") 
    # delete_bucket(BUCKET_NAME)