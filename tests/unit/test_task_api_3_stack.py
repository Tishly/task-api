import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_cdk import aws_dynamodb as dynamodb, aws_lambda as lambda_
from task_api_3.task_api_3_stack import TaskApiGateway, TaskLambdaFunctions, TasksDynamoDB

def test_dynamodb_table():
    app = core.App()
    stack = TasksDynamoDB(app, "TasksDynamoDB")
    template = assertions.Template.from_stack(stack)

    # Check if the DynamoDB table has been created with the correct properties
    template.resource_count_is("AWS::DynamoDB::Table", 1)
    template.has_resource_properties("AWS::DynamoDB::Table", {
        "BillingMode": "PAY_PER_REQUEST",
        "KeySchema": [{"AttributeName": "taskId", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "taskId", "AttributeType": "S"}]
    })

def test_lambda_function():
    app = core.App()
    stack = TasksDynamoDB(app, "TasksDynamoDB")
    dynamo_table = dynamodb.Table.from_table_arn(stack, "ImportedTable", "arn:aws:dynamodb:region:account-id:table/TasksTable")
    lambda_stack = TaskLambdaFunctions(app, "TaskLambdaFunctions", table=dynamo_table)
    template = assertions.Template.from_stack(lambda_stack)

    # Check if the Lambda function is created with correct properties
    template.resource_count_is("AWS::Lambda::Function", 1)
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "task_handler.lambda_handler",
        "Runtime": "python3.8",
        "Environment": {
            "Variables": {
                "TASKS_TABLE": {"Ref": "ImportedTable"}
            }
        }
    })

def test_api_gateway():
    app = core.App()
    stack = TaskLambdaFunctions(app, "TaskLambdaFunctions", table=dynamodb.Table.from_table_arn(app, "ImportedTable", "arn:aws:dynamodb:region:account-id:table/TasksTable"))
    task_handler = lambda_.Function(stack, "DummyHandler", runtime=lambda_.Runtime.PYTHON_3_8, handler="index.handler", code=lambda_.Code.from_inline("def handler(event, context): pass"))
    api_stack = TaskApiGateway(app, "TaskApiGateway", task_handler=task_handler)
    template = assertions.Template.from_stack(api_stack)

    # Check if the API Gateway REST API has been created with the correct methods and CORS settings
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)
    template.has_resource_properties("AWS::ApiGateway::RestApi", {
        "Name": "TaskApi"
    })

    # Check for tasks resource and methods (POST, OPTIONS)
    template.has_resource_properties("AWS::ApiGateway::Resource", {
        "PathPart": "tasks"
    })
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "POST",
        "AuthorizationType": "NONE"
    })

    # Check for task item resource and methods (GET, PUT, DELETE, OPTIONS)
    template.has_resource_properties("AWS::ApiGateway::Resource", {
        "PathPart": "{taskId}"
    })
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "GET",
        "AuthorizationType": "NONE"
    })
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "PUT",
        "AuthorizationType": "NONE"
    })
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "DELETE",
        "AuthorizationType": "NONE"
    })
    # Check for OPTIONS method for CORS on /tasks and /tasks/{taskId}
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "OPTIONS"
    })

def test_cors_enabled():
    app = core.App()
    stack = TaskLambdaFunctions(app, "TaskLambdaFunctions", table=dynamodb.Table.from_table_arn(app, "ImportedTable", "arn:aws:dynamodb:region:account-id:table/TasksTable"))
    task_handler = lambda_.Function(stack, "DummyHandler", runtime=lambda_.Runtime.PYTHON_3_8, handler="index.handler", code=lambda_.Code.from_inline("def handler(event, context): pass"))
    api_stack = TaskApiGateway(app, "TaskApiGateway", task_handler=task_handler)
    template = assertions.Template.from_stack(api_stack)

    # Verify CORS configuration is applied
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "OPTIONS",
        "Integration": {
            "IntegrationResponses": [{
                "StatusCode": "200",
                "ResponseParameters": {
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type'",
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,POST,PUT,DELETE'"
                }
            }]
        }
    })