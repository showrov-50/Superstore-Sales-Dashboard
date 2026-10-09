# Local Data Analysis Agent

A free, private data analysis application that runs locally using
Python, Streamlit, Pandas, Plotly, Ollama, and Qwen3.

## Features

- Upload CSV and Excel files
- Preview dataset
- Detect missing values and duplicate rows
- View column names and data types
- Create bar, line, and scatter charts
- Download charts as PNG images
- Download analysis reports as text
- Download processed data as CSV
- Ask questions using a local AI model
- Keep temporary conversation history
- Clear chat history
- No paid API required

## Requirements

- Windows 10 or Windows 11
- Python
- Ollama
- Qwen3 4B model
- At least 8 GB RAM; 16 GB is recommended

## Start the Application

Double-click:

start_agent.bat

Or run this command from the project folder:

python -m streamlit run app.py

## Stop the Application

Press Ctrl + C in the Terminal window.

## Local AI Model

The application uses:

qwen3:4b

To confirm that the model is installed:

ollama list

## Privacy

The AI model runs locally through Ollama.
The application does not require an OpenAI API key.

## Important Limitation

AI-generated explanations may contain mistakes.
Always verify important calculations using the displayed tables,
charts, and numeric summaries.