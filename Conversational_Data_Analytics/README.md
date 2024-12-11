# Conversational Data Analytics with the OpenAI Assistant Feature

### Supported Features

| Streaming | Files | Code Interpreter | Voice |
| --------- | ----- | ---------------- | ----- |
| ✅        | ✅    | ✅               | ✅    |

### Get an OpenAI API key

Go to OpenAI's [API keys page](https://platform.openai.com/api-keys) and create one if you don't have one already.

### Create a .env file

In the `.env` file and set your `OPENAI_API_KEY`.

### Create the assistant

`python create_assistant.py`

This will print the id of your assistant, set it in your `.env` file.

### Run locally

`chainlit run app.py`

### [Optional] Get a Literal AI API key

> [!NOTE]  
> Literal AI is an all in one observability, evaluation and analytics platform for building LLM apps.

Go to [Literal AI](https://cloud.getliteral.ai/), create a project and go to Settings to get your API key.
