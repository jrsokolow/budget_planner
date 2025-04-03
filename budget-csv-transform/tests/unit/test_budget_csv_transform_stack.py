import aws_cdk as core
import aws_cdk.assertions as assertions

from budget_csv_transform.budget_csv_transform_stack import BudgetCsvTransformStack

# example tests. To run these tests, uncomment this file along with the example
# resource in budget_csv_transform/budget_csv_transform_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BudgetCsvTransformStack(app, "budget-csv-transform")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
