from dotenv import load_dotenv
import boto3
import os
import logging
import json
from botocore.exceptions import ClientError
import re
import ast
import pprint
load_dotenv()


# Initialize the model, client, and tools
MODEL_NAME = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
# client = boto3.client(service_name='bedrock-runtime')

def calculate(expression):
        # Remove any non-digit or non-operator characters from the expression
        expression = re.sub(r'[^0-9+\-*/().]', '', expression)
        
        try:
            # Do calculation with safer eval
            node = ast.parse(expression, mode='eval')
            result = eval(compile(node, '<string>', 'eval'))
                                
            return str(result)
        except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError):
            return "Error: Invalid expression"
    
def special_format(input, type):   
    try:
        if type.lower() == "integer":
            return "{:d}".format(int(float(input)))
        elif type.lower() == "float" or type.lower() == "double" or type.lower() == "real" or type.lower() == "decimal":
            return "{:.2f}".format(float(input))
        else:
            return str(input)
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, OverflowError) as e:
        return "Error: Invalid conversion - {e}"
        
tools = [
            {
                "name": "calculator",
                "description": "A simple calculator that performs basic arithmetic operations.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate (e.g., '2 + 3 * 4')."
                        }
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "formatter",
                "description": "A simple string formatter that format the input string properly based on the indicated type.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "The input string (e.g., '123', '123.00')."
                        },
                        "type": {
                            "type": "string",
                            "description": "The type of the output (e.g., 'integer', 'float', 'double', 'real', 'decimal')."
                        }
                    },
                    "required": ["input", "type"]
                }
            }
        ]

class Agent:
    # Define the __init__ method to initialize the Agent
    def __init__(self, model_name=None, client=None, custom_tools=None, reasoning_prompt=None):
        self.model_name = model_name if model_name else MODEL_NAME
        self.client = client if client else boto3.client(service_name='bedrock-runtime')
        self.tools = custom_tools if custom_tools else tools
        self.reasoning_prompt = reasoning_prompt if reasoning_prompt else None
        self.memory = []
    
    # Define the process_tool_call method to process the tool call
    def process_tool_call(self, tool_name, tool_input):
        if tool_name == "calculator":
            return calculate(tool_input["expression"])
        elif tool_name == "formatter":
            return special_format(tool_input["input"], tool_input["type"])
    
    # Define the invoke_tool_use method to iteratively process the tool use
    def invoke_tool_use(self, init_user_message, response_messages, tool_use_body):
        try:
            # Initialize the tool_use_message_content
            tool_use_result_content = []
            # Initialize the response_messages_content, including the current tool use information
            response_messages_content = response_messages
            # Start the loop to process the tool use
            while True:
                tool_use_id = tool_use_body.get("id")
                tool_name = tool_use_body.get("name")
                tool_input = tool_use_body.get("input")

                print(f"\nTool Used: {tool_name}")
                print(f"Tool Input: {tool_input}")
                tool_result = self.process_tool_call(tool_name, tool_input)
                print(f"Tool Result: {tool_result}")
                # Append the current tool use result to the tool_use_result_content
                # This step is very important because the AI model needs to know what tool results have been produced.
                tool_use_result_content.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result,
                    }
                )
                # Prepare the tool_use_result_message and tool_use_message
                tool_use_result_message = {"role": "user", "content": tool_use_result_content} # including current tool use result
                tool_use_message =  {"role": "assistant", "content": response_messages_content} # including current tool use information
                # Prepare the body for the next iteration
                if self.reasoning_prompt:
                    body=json.dumps(
                        {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 10000,
                            "messages": [init_user_message, tool_use_message, tool_use_result_message],
                            "tools": self.tools,
                            "system": self.reasoning_prompt,
                        }  
                    )
                else:
                    body=json.dumps(
                        {
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 10000,
                            "messages": [init_user_message, tool_use_message, tool_use_result_message],
                            "tools": self.tools,
                        }  
                    )
                # Invoke the model with the new body
                response = self.client.invoke_model(body=body, modelId=self.model_name)
                # Extract the response body and messages
                response_body = json.loads(response.get("body").read())
                response_messages = response_body.get('content')
                # Update the response_messages_content with the latest response message
                # This step is very important because the AI model needs to know what tools have been and will be used. 
                # tool_use_result_content and response_messages_content need to be aligned.
                response_messages_content.append(response_messages[-1])
                # Initialize the tool_use_body and assistant_response. Otherwise, they may make inifiite loop
                tool_use_body = None
                assistant_response = ""
                # Check if the response contains another tool_use
                for message in response_messages:
                    if message.get("type") == "tool_use":
                        tool_use_body = message
                    elif message.get("type") == "text":
                        assistant_response = message.get("text")
                # If the response contains another tool_use, continue the loop. Otherwise, break the loop
                if tool_use_body is not None and tool_use_body.get("type") == "tool_use":
                    continue
                else:
                    break
            # Prepare the final_response
            final_response = assistant_response
            final_memory = [init_user_message, tool_use_message, tool_use_result_message]

            return final_response, final_memory
        except ClientError as e:
            logging.error(e)
            return None
    
    # Define the chat_with_model method to chat with the model with a user input prompt.
    def chat_with_model(self, prompt):
        print(f"\n{'='*50}\nUser Message: {prompt}\n{'='*50}")
        tool_use_body = None
        user_message =  {"role": "user", "content": prompt}
        if self.reasoning_prompt:
            body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 10000,
                        "messages": [user_message],
                        "tools": self.tools,
                        "system": self.reasoning_prompt,
                    }  
                )
        else:
            body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 10000,
                        "messages": [user_message],
                        "tools": self.tools,
                    }  
                )
        response = self.client.invoke_model(body=body, modelId=self.model_name)
        response_body = json.loads(response.get("body").read())
        response_messages = response_body.get('content')
        for message in response_messages:
            if message.get("type") == "tool_use":
                tool_use_body = message
            elif message.get("type") == "text":
                assistant_response = message.get("text")
        print(f"\nInitial Response: {assistant_response}")
        
        if tool_use_body is not None and tool_use_body.get("type") == "tool_use":
            final_response, final_memory = self.invoke_tool_use(user_message, response_messages, tool_use_body)
        else:
            final_response = assistant_response
            final_memory = []

        # Save the intermediate results in the memory
        self.memory = final_memory
            
        return final_response


if __name__ == "__main__":
    # Test the AI model capabilities to call one function
    agent = Agent()
    final_response = agent.chat_with_model("What is the result of 1,984,135 * 9,343,116?")
    print(f"\nFinal Response: {final_response}")
    pprint.pprint(agent.memory)

    # Test the AI model capabilities to do reasoning/planning and then call two functions without explicit sequence instruction.
    final_response = agent.chat_with_model("Format the calculation result of (12851 - 593) * 301 + 76 as a decimal.")
    print(f"\nFinal Response: {final_response}")
    pprint.pprint(agent.memory)

    # Test the AI agent with a custom reasoning instruction
    # Test the AI agent with a custom reasoning instruction
    reasoning_instruction = """
    You are a helpful assistant that:
    1. Performs arithmetic operations using the calculator tool
    2. Formats results appropriately using the formatter tool
    3. Explains your process clearly to the user

    Always verify calculations and format results according to the user's needs.
    """
    agent = Agent(reasoning_prompt=reasoning_instruction)
    final_response = agent.chat_with_model("What is the result of 1,984,135 * 9,343,116?")
    print(f"\nFinal Response: {final_response}")
    pprint.pprint(agent.memory)



