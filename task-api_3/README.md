# Task API - Serverless CRUD API using AWS CDK, Lambda, API Gateway, and DynamoDB

This project creates a serverless CRUD API for managing "Tasks" using AWS CDK, Lambda (Python), API Gateway, and DynamoDB.

## Prerequisites

- **AWS CLI**: [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS CDK**: [Install AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
- **Node.js**: [Install Node.js](https://nodejs.org/en/download/)
- **Python**: [Install Python](https://www.python.org/downloads/) Ensure Python is installed and configured. Version 3.8 was used for this project.

1. ## 🚀 Deployment using AWS CDK

```bash
   # If you DONT have cdk installed
   npm install -g aws-cdk
   # If this is first time you are using cdk then, run cdk bootstrap
   # cdk bootstrap

   # Make sure you in root directory and create your virtual environment
   python3 -m venv .env
   source .env/bin/activate

   # Install all required dependencies
   pip install -r requirements.txt

   # Synthesize the template and deploy it
   cdk synth
   cdk deploy
```

## Test the API

Once deployed, you can test the API using tools like curl, Postman, or similar. Replace '{API_URL}' with the actual API Gateway URL provided after deployment.

### Create Task (POST /task)

````bash
curl -X POST {API_URL}/task -H "Content-Type: application/json" -d '{
    "taskId": "1",
    "title": "Task 1",
    "description": "This is the first task",
    "status": "pending"
}'
````

### Get Task (GET /task)
```bash
curl -X GET "{API_URL}/task?taskId=1"
```
### Update Task (PUT /task)
```bash
curl -X PUT {API_URL}/task -H "Content-Type: application/json" -d '{
    "taskId": "1",
    "title": "Updated Task 1",
    "description": "This task has been updated",
    "status": "completed"
}'
```

### Delete Task (DELETE /task)
```bash
curl -X DELETE "{API_URL}/task?taskId=1"
```
### Clean Up Resources
To delete the stack and clean up AWS resources:

```bash
cdk destroy
```

## Notes 

- The removalPolicy for the DynamoDB table is set to DESTROY, which means the table will be deleted when the stack is destroyed. For production environment, it is recommended to change this to RETAIN.

- Make sure you have the correct permissions for deploying and managing resources in your AWS account.


### Final Steps/Summary:
1. **Install dependencies** using `npm install`.
2. **Deploy the stack** using `cdk deploy`.
3. **Test the API** using `curl` or Postman with the provided API Gateway URL.
4. **Clean up resources** using `cdk destroy`.

