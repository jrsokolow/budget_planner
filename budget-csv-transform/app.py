#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Environment

from src.budget_csv_transform_stack import BudgetCsvTransformStack

app = cdk.App()

test_env = Environment(account="XXXX", region="eu-west-1")
BudgetCsvTransformStack(app, "BudgetCsvTransformStack-Test", stage="test", env=test_env)
prod_env = Environment(account="XXXX", region="eu-central-1")
BudgetCsvTransformStack(app, "BudgetCsvTransformStack-Prod", stage="prod", env=prod_env)

app.synth()
