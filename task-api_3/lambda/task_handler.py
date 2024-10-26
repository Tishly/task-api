import json
import os
import uuid
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TASKS_TABLE')

if not table_name:
    raise ValueError("TASKS_TABLE environment variable is not set")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    http_method = event['httpMethod']
    path = event['path']
    if http_method == 'POST' and path == '/task':
        return create_task(json.loads(event['body']))
    elif http_method == 'GET' and path == '/task':
        return get_task(event.get('queryStringParameters', {}).get('taskId'))
    elif http_method == 'PUT' and path == '/task':
        return update_task(json.loads(event['body']))
    elif http_method == 'DELETE' and path == '/task':
        return delete_task(event.get('queryStringParameters', {}).get('taskId'))
    else:
        return {"statusCode": 400, "body": json.dumps({"message": "Unsupported route"})}
    
def create_task(task):
    required_fields = ['taskId', 'title', 'description', 'status']
    if not all(field in task for field in required_fields):
        return {"statusCode": 400, "body": json.dumps({"message": "Missing required fields"})}
    task['taskId'] = str(uuid.uuid4())
    table.put_item(Item=task)
    return {"statusCode": 200, "body": json.dumps({"message": "Task created"})}

def get_task(task_id):
    if not task_id:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing taskId query parameter"})}
    response = table.get_item(Key={'taskId': task_id})
    if 'Item' in response:
        return {"statusCode": 200, "body": json.dumps(response['Item'])}
    else:
        return {"statusCode": 404, "body": json.dumps({"message": "Task not found"})}
    
def update_task(task):
    required_fields = ['taskId', 'title', 'description', 'status']
    if not all(field in task for field in required_fields):
        return {"statusCode": 400, "body": json.dumps({"message": "Missing required fields"})}
    table.update_item(
        Key={'taskId': task['taskId']},
        UpdateExpression="SET #title = :title, #description = :description, #status = :status",
        ExpressionAttributeNames={
            '#title': 'title',
            '#description': 'description',
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':title': task['title'],
            ':description': task['description'],
            ':status': task['status']
        },
        ConditionExpression="attribute_exists(taskId)"  # Ensure the task exists
    )
    return {"statusCode": 200, "body": json.dumps({"message": "Task updated"})}

def delete_task(task_id):
    if not task_id:
        return {"statusCode": 400, "body": json.dumps({"message": "Missing taskId query parameter"})}
    table.delete_item(Key={'taskId': task_id})
    return {"statusCode": 200, "body": json.dumps({"message": "Task deleted"})}