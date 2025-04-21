import json
import boto3
from botocore.config import Config
from datetime import datetime

def generate_blog_using_bedrock(blog_topic: str) -> str:
    """
    Generate a blog using Amazon Bedrock's Llama 3 8B Instruct model.
    """
    try:
        # Define the prompt for Llama 3
        prompt = f"""
        Write a 200-word blog on the topic: {blog_topic}
        """
        # Configure body for Bedrock API
        body = {
            "prompt": prompt,
            "max_gen_length": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
        # Set up Bedrock client
        config = Config(read_timeout=300, retries={'max_attempts': 3})
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1', config=config)
        # Invoke the model
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId='meta.llama3-8b-instruct-v1:0',
            contentType='application/json',
            accept='application/json'
        )
        # Process response
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        blog_details = response_data['generation']
        print(f"Generated blog: {blog_details}")
        return blog_details
    except Exception as e:
        print(f"Error generating blog: {e}")
        return ""

def save_blog_details_in_s3(s3_key: str, s3_bucket: str, blog_content: str):
    """
    Save the generated blog to an S3 bucket.
    """
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=blog_content)
        print(f"Blog saved to S3: {s3_bucket}/{s3_key}")
    except Exception as e:
        print(f"Error saving to S3: {e}")

def lambda_handler(event, context):
    """
    Lambda handler to process API Gateway POST requests.
    """
    try:
        # Parse the event body
        body = json.loads(event['body'])
        blog_topic = body.get('blog_topic', '')
        if not blog_topic:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Blog topic is required'})
            }
        # Generate blog
        generated_blog = generate_blog_using_bedrock(blog_topic)
        if generated_blog:
            # Create S3 key with timestamp
            current_time = datetime.now().strftime('%H_%M_%S')
            s3_key = f"blog_output/blog_{current_time}.txt"
            s3_bucket = 'YOUR-BUCKET-NAME'  # Replace with your bucket name
            # Save to S3
            save_blog_details_in_s3(s3_key, s3_bucket, generated_blog)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Blog generation completed'})
            }
        else:
            print("No blog was generated")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Blog generation failed'})
            }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
