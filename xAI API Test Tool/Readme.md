# xAI API Test Tool

## Overview

This Python script (`TestxAIAPI.py`) is a simple tool designed to test and verify your connection to the xAI API. It sends a basic chat completion request to the Grok-4 model using the provided API key and checks if the response is successful. This helps ensure that your API key is valid and the endpoint is reachable.

The script is useful for developers integrating with the xAI API, allowing quick validation before building more complex applications.

## Features

- Loads API key from a `.env` file for secure handling.
- Sends a test message to the xAI chat completions endpoint.
- Handles success and error responses with clear output.
- Supports non-streaming responses with zero temperature for deterministic output.

## Prerequisites

- Python 3.6 or higher.
- An xAI API key (obtain from the xAI developer portal).
- Required Python libraries: `requests` and `python-dotenv`.

## Installation

1. Clone or download this repository/script.
2. Install the required dependencies using pip:

   ```
   pip install requests python-dotenv
   ```

3. Create a `.env` file in the same directory as the script with the following content:

   ```
   XAI_API_KEY=your_api_key_here
   ```

   Replace `your_api_key_here` with your actual xAI API key.

## Usage

Run the script from the command line:

```
python TestxAIAPI.py
```

The script will:
- Load the API key from `.env`.
- Send a test request to the xAI API.
- Print the status code and response details.

### Example Output (Success)

```
✓ API Key loaded: sk-...

Testing xAI API connection...
Endpoint: https://api.x.ai/v1/chat/completions
Model: grok-4

Status Code: 200
✅ SUCCESS! API is working correctly.

Response:
Hello from xAI API test!

✓ xAI API should work correctly now!
```

### Example Output (Error)

If the API key is invalid or there's a network issue:

```
✓ API Key loaded: sk-...

Testing xAI API connection...
Endpoint: https://api.x.ai/v1/chat/completions
Model: grok-4

Status Code: 401
❌ Error: 401
Response: {"error":{"message":"Invalid API key","type":"invalid_request_error","param":null,"code":null}}
```

## Troubleshooting

- **API Key Not Found**: Ensure the `.env` file exists and contains `XAI_API_KEY=your_key`.
- **Request Failed**: Check your internet connection or firewall settings. The endpoint is `https://api.x.ai/v1/chat/completions`.
- **Dependencies Missing**: Run `pip install requests python-dotenv` if you encounter import errors.
- **Timeout Issues**: The script has a 3600-second timeout; adjust if needed for slower connections.
- For API-specific errors, refer to the xAI API documentation.

## License

This script is provided under the MIT License. Feel free to modify and use it as needed.

## Contributing

If you'd like to improve this tool (e.g., add support for streaming or other models), submit a pull request!
