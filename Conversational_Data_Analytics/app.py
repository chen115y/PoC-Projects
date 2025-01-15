import os
import plotly
from io import BytesIO
from pathlib import Path
from typing import List

from openai import AsyncAssistantEventHandler, AsyncOpenAI, OpenAI

from literalai.helper import utc_now

import chainlit as cl
from chainlit.config import config
from chainlit.element import Element
from openai.types.beta.threads.runs import RunStep


async_openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
sync_openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

assistant = sync_openai_client.beta.assistants.retrieve(
    os.environ.get("OPENAI_ASSISTANT_ID")
)

config.ui.name = assistant.name

class EventHandler(AsyncAssistantEventHandler):
    """
    Handles events from the OpenAI Assistant API and manages message display in the Chainlit interface.
    """

    def __init__(self, assistant_name: str) -> None:
        super().__init__()
        self.current_message: cl.Message = None
        self.current_step: cl.Step = None
        self.current_tool_call = None
        self.assistant_name = assistant_name

    async def on_run_step_created(self, run_step: RunStep) -> None:
        cl.user_session.set("run_step", run_step)

    async def on_text_created(self, text) -> None:
        self.current_message = await cl.Message(author=self.assistant_name, content="").send()

    async def on_text_delta(self, delta, snapshot):
        if delta.value:
            await self.current_message.stream_token(delta.value)

    async def on_text_done(self, text):
        """
        Handles when text generation is complete, processes any file annotations, and updates the message.
        
        This method:
        - Updates the current message
        - For each file annotation:
            - Retrieves the file content
            - If the file is a Plotly figure, displays it as an interactive plot
            - Otherwise displays it as a downloadable file
            - Updates any file path references in the message with proper Chainlit links
        
        Args:
            text: The completed text object containing content and annotations
        """
        await self.current_message.update()
        if text.annotations:
            print(text.annotations)
            for annotation in text.annotations:
                if annotation.type == "file_path":
                    response = await async_openai_client.files.with_raw_response.content(annotation.file_path.file_id)
                    file_name = annotation.text.split("/")[-1]
                    try:
                        fig = plotly.io.from_json(response.content)
                        element = cl.Plotly(name=file_name, figure=fig)
                        await cl.Message(
                            content="",
                            elements=[element]).send()
                    except Exception as e:
                        element = cl.File(content=response.content, name=file_name)
                        await cl.Message(
                            content="",
                            elements=[element]).send()
                    # Hack to fix links
                    if annotation.text in self.current_message.content and element.chainlit_key:
                        self.current_message.content = self.current_message.content.replace(annotation.text, f"/project/file/{element.chainlit_key}?session_id={cl.context.session.id}")
                        await self.current_message.update()

    async def on_tool_call_created(self, tool_call):
        """
        Handles the creation of a tool call by initializing and sending a new step in the Chainlit interface.

        Args:
            tool_call: The tool call object from the OpenAI Assistant API containing information about the tool being called.

        This method:
        - Sets the current tool call ID
        - Creates a new Chainlit Step with the tool type
        - Configures the step to show Python input
        - Sets the start time
        - Sends the step to the interface
        """
        self.current_tool_call = tool_call.id
        self.current_step = cl.Step(name=tool_call.type, type="tool", parent_id=cl.context.session.id)
        self.current_step.show_input = "python"
        self.current_step.start = utc_now()
        await self.current_step.send()

    async def on_tool_call_delta(self, delta, snapshot): 
        """
        Handles streaming updates from tool calls in the OpenAI Assistant API.

        This method processes incremental updates (deltas) from tool calls and manages the display
        of code execution steps in the Chainlit interface.

        Args:
            delta: The incremental update containing changes in the tool call
            snapshot: The current state of the tool call after applying the delta

        The method handles:
        - Creating new steps for tool calls (code interpreter or function calls)
        - Streaming code input
        - Processing code interpreter outputs including:
            - Log messages
            - Generated images
            - Code execution results

        The step display is updated in real-time as new information arrives from the tool call.
        """
        if snapshot.id != self.current_tool_call:
            self.current_tool_call = snapshot.id
            self.current_step = cl.Step(name=delta.type, type="tool",  parent_id=cl.context.session.id)
            self.current_step.start = utc_now()
            if snapshot.type == "code_interpreter":
                 self.current_step.show_input = "python"
            if snapshot.type == "function":
                self.current_step.name = snapshot.function.name
                self.current_step.language = "json"
            await self.current_step.send()
        
        if delta.type == "function":
            pass
        
        if delta.type == "code_interpreter":
            if delta.code_interpreter.outputs:
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        self.current_step.output += output.logs
                        self.current_step.language = "markdown"
                        self.current_step.end = utc_now()
                        await self.current_step.update()
                    elif output.type == "image":
                        self.current_step.language = "json"
                        self.current_step.output = output.image.model_dump_json()
            else:
                if delta.code_interpreter.input:
                    await self.current_step.stream_token(delta.code_interpreter.input, is_input=True)  

    async def on_event(self, event) -> None:
        if event.event == "error":
            return cl.ErrorMessage(content=str(event.data.message)).send()

    async def on_exception(self, exception: Exception) -> None:
        return cl.ErrorMessage(content=str(exception)).send()

    async def on_tool_call_done(self, tool_call):       
        self.current_step.end = utc_now()
        await self.current_step.update()

    async def on_image_file_done(self, image_file):
        """
        Handles the completion of image file processing by retrieving and displaying the image in the chat interface.

        Args:
            image_file: The image file object containing the file_id from the OpenAI API

        This method:
            - Retrieves the image content using the file_id
            - Creates a Chainlit Image element with the content
            - Adds the image to the current message's elements
            - Updates the message to display the image inline
        """
        image_id = image_file.file_id
        response = await async_openai_client.files.with_raw_response.content(image_id)
        image_element = cl.Image(
            name=image_id,
            content=response.content,
            display="inline",
            size="large"
        )
        if not self.current_message.elements:
            self.current_message.elements = []
        self.current_message.elements.append(image_element)
        await self.current_message.update()


@cl.step(type="tool")
async def speech_to_text(audio_file):
    response = await async_openai_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )

    return response.text


async def upload_files(files: List[Element]):
    """
    Uploads files to OpenAI's API for use with assistants.

    Args:
        files (List[Element]): List of file elements to upload, each containing a file path

    Returns:
        list: A list of file IDs returned by the OpenAI API after successful upload

    The function iterates through the provided files, uploads each one to OpenAI's API
    with the purpose set to "assistants", and collects the returned file IDs.
    """
    file_ids = []
    for file in files:
        uploaded_file = await async_openai_client.files.create(
            file=Path(file.path), purpose="assistants"
        )
        file_ids.append(uploaded_file.id)
    return file_ids


async def process_files(files: List[Element]):
    """
    Process uploaded files and prepare them for use with OpenAI Assistant API.
    
    Args:
        files (List[Element]): List of file elements to be processed
        
    Returns:
        list: A list of dictionaries containing file_id and allowed tools for each file.
              For text-based files (docx, markdown, pdf, txt), both code_interpreter and file_search 
              tools are enabled. For other file types, only code_interpreter is enabled.
              
    Each dictionary in the returned list has the format:
    {
        "file_id": str,  # The ID of the uploaded file
        "tools": list    # List of allowed tools for this file
    }
    """
    # Upload files if any and get file_ids
    file_ids = []
    if len(files) > 0:
        file_ids = await upload_files(files)

    return [
        {
            "file_id": file_id,
            "tools": [{"type": "code_interpreter"}, {"type": "file_search"}] if file.mime in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/markdown", "application/pdf", "text/plain"] else [{"type": "code_interpreter"}],
        }
        for file_id, file in zip(file_ids, files)
    ]


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Run Tesla stock analysis",
            message="Make a data analysis on the tesla-stock-price.csv file I previously uploaded.",
            icon="/public/write.svg",
            ),
        cl.Starter(
            label="Run a data analysis on my CSV",
            message="Make a data analysis on the next CSV file I will upload.",
            icon="/public/write.svg",
            )
        ]

@cl.on_chat_start
async def start_chat():
    # Create a Thread
    thread = await async_openai_client.beta.threads.create()
    # Store thread ID in user session for later use
    cl.user_session.set("thread_id", thread.id)
    
    
@cl.on_stop
async def stop_chat():
    current_run_step: RunStep = cl.user_session.get("run_step")
    if current_run_step:
        await async_openai_client.beta.threads.runs.cancel(thread_id=current_run_step.thread_id, run_id=current_run_step.run_id)


@cl.on_message
async def main(message: cl.Message):
    """
    Handles incoming chat messages by processing them through the OpenAI Assistant API.

    This function:
    1. Retrieves the current thread ID from the user session
    2. Processes any file attachments in the message
    3. Creates a new message in the OpenAI thread with the user's content and attachments
    4. Streams the assistant's response using the EventHandler

    Args:
        message (cl.Message): The incoming message object from Chainlit containing:
            - content: The text content of the message
            - elements: Any file attachments or elements included in the message

    The function integrates with OpenAI's Assistant API to maintain conversation context
    and handle file processing while streaming responses back to the user interface.
    """
    thread_id = cl.user_session.get("thread_id")

    attachments = await process_files(message.elements)

    # Add a Message to the Thread
    oai_message = await async_openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message.content,
        attachments=attachments,
    )

    # Create and Stream a Run
    async with async_openai_client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id=assistant.id,
        event_handler=EventHandler(assistant_name=assistant.name),
    ) as stream:
        await stream.until_done()
