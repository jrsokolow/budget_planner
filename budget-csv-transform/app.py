#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Environment

from src.budget_csv_transform_stack import BudgetCsvTransformStack

app = cdk.App()

env = Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])

BudgetCsvTransformStack(app, "BudgetCsvTransformStack-Test", stage="test", env=env)

BudgetCsvTransformStack(app, "BudgetCsvTransformStack-Prod", stage="prod", env=env)

app.synth()
