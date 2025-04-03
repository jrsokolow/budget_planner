from aws_cdk import (
    Stack,
    aws_s3 as s3,                       # S3 – for storing uploaded CSV files
    aws_lambda as _lambda,             # Lambda – to process CSV and load into RDS
    aws_iam as iam,                    # IAM – to manage Lambda permissions
    aws_rds as rds,                    # RDS – PostgreSQL database
    aws_ec2 as ec2,                    # EC2/VPC – private networking
    aws_secretsmanager as secretsmanager,  # Secrets Manager – to store DB credentials
    Duration,                          # For defining Lambda timeout
    RemovalPolicy                      # Determines what happens when stack is destroyed
)
from constructs import Construct  # Base class for CDK constructs

# The main stack class that defines our infrastructure
class BudgetCsvTransformStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # 🔐 Secret in Secrets Manager to store RDS credentials
        db_credentials_secret = secretsmanager.Secret(
            self, "BudgetRdsCredentials",
            secret_name="budget-rds-credentials",  # Name of the secret in AWS console
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "budgetadmin"}',  # static username
                generate_string_key="password",                        # auto-generated password
                exclude_punctuation=True,
                include_space=False
            )
        )

        # 🌐 Create a VPC (Virtual Private Cloud) – isolated network for RDS and Lambda
        vpc = ec2.Vpc(self, "BudgetVpc", max_azs=2)  # Use 2 availability zones

        # 🗄️ Create the PostgreSQL RDS database instance
        rds_instance = rds.DatabaseInstance(
            self, "BudgetPostgres",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15  # PostgreSQL version
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO  # Small, low-cost instance
            ),
            vpc=vpc,
            credentials=rds.Credentials.from_secret(db_credentials_secret),  # Use the secret above
            multi_az=False,                             # No high availability
            allocated_storage=20,                       # Initial storage in GB
            max_allocated_storage=100,                  # Auto-scaling up to 100 GB
            publicly_accessible=False,                  # No public internet access
            vpc_subnets={"subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS},  # Private subnets
            removal_policy=RemovalPolicy.DESTROY,       # Delete DB when stack is destroyed
            delete_automated_backups=True               # Clean up backups on delete
        )

        # 🪣 Create an S3 bucket for CSV uploads
        bucket = s3.Bucket.from_bucket_name(
            self, "ExistingCsvBucket",
            "moje-wydatki"  # 🔁 Replace with the actual bucket name
        )

        # 🧠 Define a Lambda function that will handle CSV → RDS transformation
        lambda_fn = _lambda.Function(
            self, "CsvToRdsLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,              # Python 3.11 runtime
            handler="handler.main",                           # Entry point: handler.py → main()
            code=_lambda.Code.from_asset("src/lambda/csv_to_rds"),  # Path to Lambda source code
            timeout=Duration.minutes(5),                      # Max execution time
            memory_size=512,                                  # Memory in MB
            environment={                                     # Environment variables for the Lambda
                "BUCKET_NAME": bucket.bucket_name,
                "SECRET_ARN": db_credentials_secret.secret_arn,
                "DB_NAME": "postgres",  # Default DB name
                "RDS_ENDPOINT": rds_instance.db_instance_endpoint_address,
                "RDS_PORT": str(rds_instance.db_instance_endpoint_port),
            },
            vpc=vpc,                                           # Lambda runs inside the VPC
            security_groups=[rds_instance.connections.security_groups[0]],  # Allow traffic to RDS
        )

        # ✅ Grant permissions
        bucket.grant_read(lambda_fn)                     # Lambda can read objects from S3
        db_credentials_secret.grant_read(lambda_fn)      # Lambda can read the DB secret

        # Optional but useful: allow Lambda to connect to RDS (e.g. using Data API, etc.)
        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["rds-db:connect"],
            resources=["*"]
        ))
