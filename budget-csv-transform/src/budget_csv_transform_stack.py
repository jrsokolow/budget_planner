from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    Duration,
    RemovalPolicy
)
from aws_cdk.aws_lambda_event_sources import S3EventSource
from aws_cdk.aws_s3 import NotificationKeyFilter, EventType
from constructs import Construct


class BudgetCsvTransformStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage="dev", **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # 🔐 Secret in AWS Secrets Manager that stores RDS credentials
        db_credentials_secret = secretsmanager.Secret(
            self, f"BudgetRdsCredentials-{stage}",
            secret_name=f"budget-rds-credentials-{stage}",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "budgetadmin"}',
                generate_string_key="password",
                exclude_punctuation=True,
                include_space=False
            )
        )

        # 🌐 VPC with public subnets — no NAT Gateway
        vpc = ec2.Vpc(
            self, f"BudgetVpc-{stage}",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ]
        )

        # 🔌 VPC Interface Endpoint to Secrets Manager — allows Lambda to fetch secrets without NAT
        vpc.add_interface_endpoint(
            "SecretsManagerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # 🚪 Gateway VPC Endpoint for S3 — allows access to S3 buckets without NAT
        vpc.add_gateway_endpoint(
            "S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)]
        )

        # 🔐 Security Group for RDS — allows access from my IP and Lambda
        my_ip = "*****"  # Your external IP address
        rds_sg = ec2.SecurityGroup(
            self, f"RdsSecurityGroup-{stage}",
            vpc=vpc,
            description="Allow PostgreSQL access from my IP and Lambda",
            allow_all_outbound=True
        )
        rds_sg.add_ingress_rule(ec2.Peer.ipv4(my_ip), ec2.Port.tcp(5432), "Access from my IP")

        # 🗄️ RDS PostgreSQL instance
        rds_instance = rds.DatabaseInstance(
            self, f"BudgetPostgres-{stage}",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_15),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            credentials=rds.Credentials.from_secret(db_credentials_secret),
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            publicly_accessible=True,
            vpc_subnets={"subnet_type": ec2.SubnetType.PUBLIC},
            security_groups=[rds_sg],
            removal_policy=RemovalPolicy.DESTROY,
            delete_automated_backups=True,
            database_name="postgres"
        )

        # 🪣 S3 bucket for uploading CSV files
        bucket_name = f"budget-csv-uploads-{stage}"
        bucket = s3.Bucket(
            self, f"CsvUploadBucket-{stage}",
            bucket_name=bucket_name,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # 🧠 Lambda function that processes the CSV and writes to RDS
        lambda_fn = _lambda.Function(
            self, f"CsvToRdsLambda-{stage}",
            function_name=f"csv-to-rds-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.main",
            code=_lambda.Code.from_asset("src/lambda/csv_to_rds"),
            timeout=Duration.minutes(5),
            memory_size=512,
            allow_public_subnet=True,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "SECRET_ARN": db_credentials_secret.secret_arn,
                "DB_NAME": "postgres",
                "RDS_ENDPOINT": rds_instance.db_instance_endpoint_address,
                "RDS_PORT": str(rds_instance.db_instance_endpoint_port),
            },
            vpc=vpc,
            security_groups=[rds_sg],
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "Psycopg2Layer",
                    "arn:aws:lambda:eu-central-1:769729745008:layer:psycopg2-layer:1"
                )
            ],
        )

        # ➕ Lambda allowed to access RDS via security group
        rds_sg.add_ingress_rule(
            lambda_fn.connections.security_groups[0],
            ec2.Port.tcp(5432),
            "Allow Lambda to access RDS"
        )

        # ✅ IAM permissions for Lambda
        bucket.grant_read(lambda_fn)
        db_credentials_secret.grant_read(lambda_fn)

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["rds-db:connect"],
            resources=["*"]
        ))

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[f"arn:aws:s3:::{bucket_name}/*"]
        ))

        # 📦 S3 trigger — Lambda is triggered when a new CSV file is uploaded to the bucket
        lambda_fn.add_event_source(
            S3EventSource(
                bucket,
                events=[EventType.OBJECT_CREATED],
                filters=[NotificationKeyFilter(suffix=".csv")]
            )
        )
