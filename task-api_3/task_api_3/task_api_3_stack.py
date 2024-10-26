from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)
import aws_cdk as core
from constructs import Construct

class TaskApiGateway(core.Stack):
    def __init__(self, scope: Construct, id: str, task_handler: lambda_.Function, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # Create API Gateway
        api = apigateway.LambdaRestApi(
            self, "TaskApi",
            handler=task_handler,
            proxy=False  # Disable proxy to define individual routes
        )
        # Define /tasks resource
        tasks = api.root.add_resource("tasks")
        # POST /tasks - Create task
        tasks.add_method("POST")  # POST to create task
        # GET /tasks/{taskId} - Get task
        task_item = tasks.add_resource("{taskId}")
        task_item.add_method("GET")  # GET to retrieve a task
        # PUT /tasks/{taskId} - Update task
        task_item.add_method("PUT")  # PUT to update a task
        # DELETE /tasks/{taskId} - Delete task
        task_item.add_method("DELETE")  # DELETE to delete a task
        # Optionally enable CORS
        self.enable_cors(tasks)
        self.enable_cors(task_item)

    def enable_cors(self, resource: apigateway.Resource):
        """Enable CORS for a given resource."""
        resource.add_method(
            "OPTIONS",
            apigateway.MockIntegration(  # Integration type for CORS
                integration_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Headers': "'Content-Type'",
                        'method.response.header.Access-Control-Allow-Origin': "'*'",
                        'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET,POST,PUT,DELETE'"
                    }
                }],
                passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
                request_templates={"application/json": "{\"statusCode\": 200}"}
            ),
            method_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Origin': True,
                    'method.response.header.Access-Control-Allow-Methods': True
                }
            }]
        )


class TaskLambdaFunctions(core.Stack):
    def __init__(self, scope: Construct, id: str, table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # Create Lambda for task handling
        task_handler = lambda_.Function(
            self, "TaskHandler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="task_handler.lambda_handler",  # Adjust this based on the file structure
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "TASKS_TABLE": table.table_name
            }
        )
        # Grant permissions for the Lambda to access the DynamoDB table
        table.grant_read_write_data(task_handler)


class TasksDynamoDB(core.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # Create the DynamoDB table
        table = dynamodb.Table(
            self, "TasksTable",
            partition_key=dynamodb.Attribute(name="taskId", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST  # on-demand capacity
        )