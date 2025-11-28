import os
from openai import AzureOpenAI
from dotenv import load_dotenv

def test_azure_connection():
    # Load environment variables
    load_dotenv()
    
    # Azure Configuration
    endpoint = "https://bionicadvisor.openai.azure.com/"
    model_name = "gpt-35-turbo"
    deployment = "gpt-35-turbo"
    api_version = "2024-12-01-preview"
    
    print(f"\nTesting Azure OpenAI Configuration:")
    print(f"Endpoint: {endpoint}")
    print(f"Model: {model_name}")
    print(f"Deployment: {deployment}")
    print(f"API Version: {api_version}")
    
    try:
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        
        # Test with a simple query
        print("\nSending test request to Azure OpenAI...")
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "Say 'Hello, this is a test!' if you can read this message.",
                }
            ],
            max_tokens=4096,
            temperature=1.0,
            top_p=1.0,
            model=deployment
        )
        
        print("\nResponse received:")
        print(response.choices[0].message.content)
        
        print("\n✅ Test successful! Azure OpenAI API is working correctly.")
        return True
        
    except Exception as e:
        print("\n❌ Test failed! Error:")
        print(str(e))
        return False

if __name__ == "__main__":
    test_azure_connection() 