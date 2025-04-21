# GenAI-Blog-generator

Below is the complete documentation for building a generative AI blog generation application on AWS, structured to guide you through the entire process from setup to testing. 

---

# Documentation: Building a Generative AI Blog Generation Application on AWS with Bedrock and Lambda

This guide provides a step-by-step walkthrough for developing an end-to-end generative AI application on Amazon Web Services (AWS). The application generates blogs using Amazon Bedrock’s foundation models (specifically, Llama 3 8B Instruct) and AWS Lambda, triggered via Amazon API Gateway, with the output stored in Amazon S3.

## Prerequisites

Before starting, ensure you have the following:

- **AWS Account**: An active AWS account with administrative permissions or sufficient privileges to create and manage services like Lambda, API Gateway, S3, and Bedrock.
- **Basic Knowledge**: Familiarity with AWS services (Lambda, API Gateway, S3, Bedrock), Python programming, and API testing tools like Postman.
- **Tools**:
  - Access to the **AWS Management Console**.
  - A code editor such as **Visual Studio Code (VS Code)**.
  - **Postman** installed for API testing.
  - **Python 3.12** installed locally for development.

## Architecture Overview

The application follows this workflow:

1. A user sends a **POST request** via Postman to an API endpoint created with Amazon API Gateway.
2. The API Gateway triggers an **AWS Lambda function**.
3. The Lambda function uses **Amazon Bedrock** to generate a blog with the Llama 3 8B Instruct model.
4. The generated blog is saved as a text file in an **Amazon S3 bucket** with a timestamp.

## Step-by-Step Implementation

### Step 1: Set Up AWS Account and Bedrock Access

1. **Log in to AWS Management Console**:
   - Open your browser and navigate to the [AWS Management Console](https://aws.amazon.com/console/).

2. **Access Amazon Bedrock**:
   - In the console search bar, type "Bedrock" and select it.
   - Choose a region (e.g., **US East 1**) where the Llama 3 8B Instruct model is available. Model availability varies by region.

3. **Request Model Access**:
   - In the Bedrock dashboard, go to **Model Access** > **Manage Model Access**.
   - Find and select **Llama 3 8B Instruct** (model ID: `meta.llama3-8b-instruct-v1:0`).
   - Click **Save Changes** to request access. Approval is typically instant for Llama models, but some models (e.g., Anthropic Claude) may require a use case justification.
   - Confirm access is granted by checking the model status in the console.

**Note**: You must have access to the Llama 3 8B Instruct model before proceeding, as it’s critical for blog generation.

---

### Step 2: Create an AWS Lambda Function

1. **Navigate to AWS Lambda**:
   - In the AWS Console, search for "Lambda" and click **Create Function**.

2. **Configure the Lambda Function**:
   - Select **Author from Scratch**.
   - Set the function name to `bedrockapp`.
   - Choose **Python 3.12** as the runtime.
   - Use the default execution role for now (you’ll update permissions later).
   - Click **Create Function**.

3. **Set Timeout**:
   - In the Lambda function’s **Configuration** tab, under **General Configuration**, click **Edit**.
   - Set the timeout to **3 minutes** to allow sufficient time for Bedrock processing.
   - Save the changes.

---

### Step 3: Write the Lambda Function Code

1. **Set Up Local Development Environment**:
   - Open VS Code and create a new project directory (e.g., `aws-blog-gen`).
   - Install Python dependencies locally using a virtual environment or Conda. For simplicity, use a basic virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```
   - Create a `requirements.txt` file with:
     ```
     boto3
     ```
   - Install the dependency:
     ```bash
     pip install -r requirements.txt
     ```

2. **Create the Lambda Code**:
   - In your VS Code, create a file named `app.py`.
   - Add the following Python code: [View app.py](./app.py)

3. **Code Explanation**:
   - **`generate_blog_using_bedrock`**: Calls Amazon Bedrock with a prompt to generate a 200-word blog based on the user-provided topic.
   - **`save_blog_details_in_s3`**: Stores the blog content in an S3 bucket as a text file, using a timestamp in the filename.
   - **`lambda_handler`**: The main entry point for Lambda, processes the API request, generates the blog, and saves it to S3.
   - **Dependencies**: Uses `boto3` (AWS SDK for Python) for interacting with AWS services and `json` for handling API payloads.

4. **Deploy the Code to Lambda**:
   - Copy the entire contents of `app.py`.
   - In the Lambda Console, go to the **Code** tab, paste the code into `lambda_function.py`, and click **Deploy**.

---

### Step 4: Update Boto3 in Lambda with a Layer

1. **Purpose**:
   - The default `boto3` version in Lambda may not support the latest Bedrock features. A custom layer ensures compatibility with Llama 3 8B Instruct.

2. **Create a Custom Lambda Layer**:
   - In your local project directory, create a folder named `python`:
     ```bash
     mkdir python
     ```
   - Install the latest `boto3` into this folder:
     ```bash
     pip install boto3 -t python/
     ```
   - Zip the folder:
     ```bash
     zip -r boto3_layer.zip python
     ```

3. **Upload the Layer to AWS**:
   - In the AWS Lambda Console, go to **Layers** > **Create Layer**.
   - Name the layer `boto3_updated_layer`.
   - Upload `boto3_layer.zip`.
   - Select compatible runtimes: **Python 3.12, 3.11, 3.10**.
   - Click **Create**.

4. **Add the Layer to Lambda**:
   - In the `bedrockapp` Lambda function, scroll to **Layers** > **Add a Layer**.
   - Choose **Custom Layers**, select `boto3_updated_layer` (version 1), and click **Add**.
   - Confirm the layer appears under the **Layers** section.

---

### Step 5: Create an Amazon S3 Bucket

1. **Navigate to S3**:
   - In the AWS Console, search for "S3" and click **Create Bucket**.

2. **Configure the Bucket**:
   - Name the bucket `YOUR-BUCKET-NAME` (bucket names must be globally unique; append a random string if needed, e.g., `awsbedrockblog-123`).
   - Set the region to **US East 1** (or match your Lambda region).
   - Keep default settings (e.g., block public access).
   - Click **Create Bucket**.

3. **Update Lambda Code**:
   - If you used a different bucket name, update the `s3_bucket` variable in `app.py` (e.g., `s3_bucket = 'awsbedrockblog-123'`) and redeploy the Lambda function.

---

### Step 6: Set Up Amazon API Gateway

1. **Create an API**:
   - In the AWS Console, search for "API Gateway" and click **Create API**.
   - Choose **HTTP API** > **Build**.
   - Name the API `Bedrockdemoapi`.
   - Click **Review and Create**, then **Create**.

2. **Add a Route**:
   - Go to **Routes** > **Create**.
   - Set the method to **POST** and the path to `/blog_generation`.
   - Click **Create**.

3. **Integrate with Lambda**:
   - Select the `/blog_generation` route, click **Attach Integration**.
   - Choose **Lambda Function**, select `bedrockapp`, and click **Create**.

4. **Create a Stage**:
   - Go to **Stages** > **Create Stage**.
   - Name the stage `dev`.
   - Click **Create**, then deploy the API to the `dev` stage by selecting **Deploy**.

5. **Get the API URL**:
   - In the **Stages** tab, under `dev`, copy the **Invoke URL** (e.g., `https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/blog_generation`).

---

### Step 7: Update Lambda Permissions

1. **Check Permissions**:
   - If Lambda fails with errors like "not authorized to invoke model," the execution role needs additional permissions.

2. **Update IAM Role**:
   - In the Lambda Console, go to **Configuration** > **Permissions**.
   - Click the role name (e.g., `bedrockapp-role-xxx`).
   - In the IAM Console, select **Add Permissions** > **Attach Policies**.
   - Add these policies:
     - `AmazonBedrockFullAccess` (for Bedrock access).
     - `AmazonS3FullAccess` (for S3 access).
   - Click **Add Permissions**.

3. **Verify**:
   - Return to Lambda and test the function to ensure no permission errors remain.

**Security Note**: For testing, broad permissions simplify setup. For production, use least privilege principles (e.g., custom policies limiting access to specific resources).

---

### Step 8: Test the Application with Postman

1. **Set Up Postman**:
   - Open Postman and create a new **POST** request.
   - Paste the API Gateway URL (e.g., `https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/blog_generation`).

2. **Configure the Request**:
   - Go to the **Body** tab, select **Raw**, and set the format to **JSON**.
   - Enter this payload:
     ```json
     {
         "blog_topic": "Machine Learning and Generative AI"
     }
     ```

3. **Send the Request**:
   - Click **Send** and wait for the response.
   - Expected output:
     ```json
     {
         "message": "Blog generation completed"
     }
     ```

4. **Troubleshoot**:
   - **404 Error**: Verify the URL includes `/blog_generation` and matches the stage.
   - **500 Error**: Check **CloudWatch Logs** (Lambda > **Monitor** > **View CloudWatch Logs**) for details (e.g., permission issues, Bedrock failures).

---

### Step 9: Verify Output in S3

1. **Check the S3 Bucket**:
   - In the AWS Console, go to S3 > `YOUR-BUCKET-NAME`.
   - Open the `blog_output` folder.
   - Look for a file like `blog_<timestamp>.txt` (e.g., `blog_14_30_25.txt`).

2. **Inspect the Content**:
   - Download the file and open it to confirm the blog content (approximately 200 words on the requested topic).

3. **Sample Output**:
   - Example: "Machine Learning and Generative AI are transforming industries by enabling machines to create content..."

---

### Step 10: Monitor and Debug

1. **CloudWatch Logs**:
   - Check logs in Lambda > **Monitor** > **View CloudWatch Logs** for debugging.
   - Look for success messages or errors.

2. **Common Issues**:
   - **Permission Errors**: Ensure IAM role has Bedrock and S3 access.
   - **Timeout**: Increase Lambda timeout if Bedrock processing exceeds 3 minutes.
   - **Model Access**: Confirm Llama 3 8B Instruct is available in your region.
   - **API Errors**: Verify route and stage deployment in API Gateway.

---

## Best Practices

- **Security**:
  - Use least privilege IAM roles instead of full-access policies.
  - Enable API Gateway authentication (e.g., API keys, IAM, or Cognito).
  - Encrypt S3 buckets and enable access logging.

- **Cost Management**:
  - Monitor Bedrock and Lambda usage (billed per request).
  - Delete unused resources after testing.

- **Code Management**:
  - Use a version control system (e.g., Git) for code.
  - Consider AWS SAM or CloudFormation for infrastructure as code.

- **Scalability**:
  - Lambda scales automatically with API Gateway traffic.
  - Use Bedrock’s streaming features for larger outputs if needed.

---

## Conclusion

This documentation outlines how to build a generative AI blog generation application using AWS Bedrock, Lambda, API Gateway, and S3. By following these steps, you can generate blogs on demand and store them in S3, triggered via an API. The setup is flexible for enhancements like integrating other models or adding a front-end interface.

For further exploration:
- Replace Postman with a web interface.
