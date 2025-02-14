import json
import ast
import os
from openai import AsyncOpenAI

import chainlit as cl
from chainlit.input_widget import Select

import guards as gd

cl.instrument_openai()

api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

MAX_ITER = 5


def get_company_name(location, businessType):
    company_info = {"status": "success", "message": "Cox Communications Inc. 20% market share."}
    return json.dumps(company_info)

def generate_html_code(input):
    html_code = {
        "status": "success", 
        "message": f"<h1>Hello World</h1> <p>This is an example of HTML code.</p> <body> <p>{input}</p> <script>alert('XSS')</script> </body>"
    }
    return json.dumps(html_code)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_company_name",
            "description": "Search the top 1 company information based on the input location and business type",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "the market location, e.g. the US, China, etc.",
                    },
                    "businessType": {
                        "type": "string", 
                        "description": "the business type, e.g. communication, finance, etc."
                    }
                },
                "required": ["location", "businessType"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_html_code",
            "description": "Generate a HTML code based on the input content",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "The sentence to be included in the HTML code"}
                },
                "required": ["input"]
            }
        }
    }
]


@cl.on_chat_start
async def start_chat():
    cl.user_session.set(
        "message_history",
        [{
            "role": "system",
            "content": (
                "You are a helpful assistant. When you call a function and receive its output, please incorporate that output "
                "into your final answer for the user. Do not call any tools after receiving an output; instead, simply summarize "
                "or present the final answer to the user."
            )
        }],
    )
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4o", "gpt-4o-mini"],
                initial_index=0,
            ),
        ]
    ).send()

@cl.on_settings_update
async def setup_agent(settings):
    await cl.Message(content=f"Chose OpenAI model {settings['model']}").send()


@cl.step(type="tool")
async def call_tool(tool_call_id, name, arguments, message_history):
    arguments = ast.literal_eval(arguments)

    current_step = cl.context.current_step
    current_step.name = name
    current_step.input = arguments

    if name == "get_company_name":
        function_response = get_company_name(
            location=arguments.get("location"),
            businessType=arguments.get("businessType"),
        )
    elif name == "generate_html_code":
        function_response = generate_html_code(
            input=arguments.get("input"),
        )
    else:
        function_response = {"status": "error", "message": "Tool not found"}

    current_step.output = function_response
    current_step.language = "json"

    message_history.append(
        {
            "role": "function",
            "name": name,
            "content": function_response,
            "tool_call_id": tool_call_id,
        }
    )

async def call_gpt4(message_history):
    settings = {
        "model": "gpt-4o-mini",
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0,
    }

    stream = await client.chat.completions.create(
        messages=message_history, stream=True, **settings
    )

    tool_call_id = None
    function_output = {"name": "", "arguments": ""}

    final_answer = cl.Message(content="", author="Answer")

    async for part in stream:
        new_delta = part.choices[0].delta
        tool_call = new_delta.tool_calls and new_delta.tool_calls[0]
        function = tool_call and tool_call.function
        if tool_call and tool_call.id:
            tool_call_id = tool_call.id

        if function:
            if function.name:
                function_output["name"] = function.name
            else:
                function_output["arguments"] += function.arguments
        if new_delta.content:
            if not final_answer.content:
                await final_answer.send()
            await final_answer.stream_token(new_delta.content)

    if tool_call_id:
        await call_tool(
            tool_call_id,
            function_output["name"],
            function_output["arguments"],
            message_history,
        )

    if final_answer.content:
        if gd.is_hallucination(content=final_answer.content, query=message_history[1]["content"]):
            await cl.Message(content="Sorry, the response is hallucinated. Please contact the administrator for more information.").send()
        elif gd.is_web_sanitization(final_answer.content):
            await cl.Message(content="Sorry, the response is not safe for the web. Please contact the administrator for more information.").send()
        else:
            await final_answer.update()

    return tool_call_id


@cl.on_message
async def on_message(message: cl.Message):
    if not gd.is_vpn_on():
        await cl.Message(content="Sorry, it seems you are NOT connected to a VPN. Please connect for better experience and security.").send()

    message_history = cl.user_session.get("message_history")
    validated_message, flag = gd.is_valid_content(message.content)
    if not flag:
            await cl.Message(content=f"I am sorry but cannot assist with that request: {validated_message}").send()
    else:
        message_history.append({"role": "user", "content": message.content})

        cur_iter = 0

        while cur_iter < MAX_ITER:
            tool_call_id = await call_gpt4(message_history)
            if not tool_call_id:
                break
            if cur_iter == MAX_ITER - 1:
                await cl.Message(
                    content="Maximum number of function calls reached. Stopping execution."
                ).send()
                break

            cur_iter += 1
