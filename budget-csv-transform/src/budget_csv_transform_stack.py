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

        # 🔐 Secret for RDS credentials
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

        # 🌐 VPC
        vpc = ec2.Vpc(self, f"BudgetVpc-{stage}", max_azs=2)

        # 🗄️ RDS PostgreSQL
        rds_instance = rds.DatabaseInstance(
            self, f"BudgetPostgres-{stage}",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            credentials=rds.Credentials.from_secret(db_credentials_secret),
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=100,
            publicly_accessible=False,
            vpc_subnets={"subnet_type": ec2.SubnetType.PRIVATE_WITH_EGRESS},
            removal_policy=RemovalPolicy.DESTROY,
            delete_automated_backups=True,
            database_name="postgres"
        )

        # 🪣 CREATE new S3 bucket (instead of importing)
        bucket = s3.Bucket(
            self, f"CsvUploadBucket-{stage}",
            bucket_name=f"budget-csv-uploads-{stage}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # 🧠 Lambda function (CSV → RDS)
        lambda_fn = _lambda.Function(
            self, f"CsvToRdsLambda-{stage}",
            function_name=f"csv-to-rds-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.main",
            code=_lambda.Code.from_asset("src/lambda/csv_to_rds"),
            timeout=Duration.minutes(5),
            memory_size=512,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "SECRET_ARN": db_credentials_secret.secret_arn,
                "DB_NAME": "postgres",
                "RDS_ENDPOINT": rds_instance.db_instance_endpoint_address,
                "RDS_PORT": str(rds_instance.db_instance_endpoint_port),
            },
            vpc=vpc,
            security_groups=[rds_instance.connections.security_groups[0]],
            layers=[
                _lambda.LayerVersion.from_layer_version_arn(
                    self, "Psycopg2Layer",
                    "arn:aws:lambda:eu-central-1:769729745008:layer:psycopg2-layer:1"
                )
            ],
        )

        # ✅ Permissions
        bucket.grant_read(lambda_fn)
        db_credentials_secret.grant_read(lambda_fn)

        lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["rds-db:connect"],
            resources=["*"]
        ))

        # 📦 Trigger Lambda on new .csv files in the bucket
        lambda_fn.add_event_source(
            S3EventSource(
                bucket,
                events=[EventType.OBJECT_CREATED],
                filters=[NotificationKeyFilter(suffix=".csv")]
            )
        )
