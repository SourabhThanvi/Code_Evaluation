README.md
=========

Introduction
------------
**Code Evolution Analyzer** is a Python-based code analysis platform that helps developers generate, analyze, and understand how their code evolves over time. The tool leverages **LLMs** (specifically, Gemini and OpenAI models) together with **AST diffing** techniques to compare versions of Python code. It not only generates clean, beginner-friendly code from natural-language queries but also analyzes structural changes when developers modify the generated code. The analyzer extracts insights into added or removed functions, classes, naming patterns, complexity shifts, and refactoring patterns. In addition, a comprehensive report is generated with recommendations to improve code quality and developer learning outcomes.


🎥 Demo
-------
> _Watch the video below to see how the platform works step by step._

https://github.com/user-attachments/assets/412f208d-c74f-4bcf-bce9-08ec726ee54e


Usage
-----
The repository supports code generation, modification, and analysis through both a **web-based UI** and an **API**. Here is a step-by-step guide:

1. **Code Generation:**  
   - Launch the user interface using Streamlit by running the application (see Installation below).  
   - Input your query (for example, “Write a function to generate the Fibonacci series up to 5 places”) in the interface.  
   - The system uses a Gemini-based LLM to generate simple, clean Python code suitable for programming freshers.  
   - The generated code is saved for subsequent analysis.

2. **Code Modification:**  
   - Edit the generated code as needed. Modifications may include code simplification, renaming functions, rewriting conditions, or adding new logic.  
   - Upload the updated file through the UI. The module captures the original file from step 1 and the modified file provided by the user.

3. **Analysis & Report Generation:**  
   - Upon uploading the modified code, the application invokes an AST parsing workflow that compares the original and modified versions.  
   - Structural differences are computed, including added/removed functions, classes, increased node counts, and changes in control flow (using LangGraph workflows as seen in multiple modules).
   - The output is a detailed report that includes a change summary, developer insights, learning observations, and actionable recommendations.

The UI offers a three-step navigation: **Generate Code**, **Upload Updated Code**, and **View Analysis Report**. Alternatively, RESTful endpoints are provided for programmatic access (see API endpoint documentation in the source code).

Features
--------
The key features of the repository include:

- **Code Generation:**  
  • Generates simple and idiomatic Python code based on natural-language queries.  
  • Powered by Gemini and OpenAI LLMs with feedback mechanisms to reduce complexity.

- **Structural Code Analysis:**  
  • Uses AST diffing to detect structural changes like added or removed functions, classes, and imports.  
  • Computes complexity metrics (e.g., total nodes, if statements, loops) to spot refactoring patterns.

- **Pattern Tracking & Report Generation:**  
  • Extracts developer behavior insights through pattern extraction and learning insights analysis.  
  • Provides a high-level, structured report including a change summary, insights into developer style (for example, whether they prefer brevity or simplification), observations, and actionable suggestions.

- **Interactive User Interface:**  
  • A Streamlit-based UI for generating code and visualizing analysis results.  
  • REST API endpoints for integration with other tools or CI pipelines.

Configuration
-------------
Configuration is managed via a JSON file and environment variables:

- **Config File:**  
  The file located at **config/config.yaml** includes key parameters such as:  
  • *gemini_api_key*: The API key for connecting with the Gemini LLM.  
  • *max_refinement_loops*: Maximum allowed code refinement iterations.  
  • *directories*: Paths for storing generated code, reports, codes, and patterns.  
  • *files*: File names for saving AST patterns and analysis history.  
  • *session_config*: Settings for checkpointing, default user identification, and session timeout.

- **Environment Variables:**  
  Use a **.env** file to set up the `GEMINI_API_KEY` needed for authenticating the LLM client.

Requirements
------------
Before running the application, ensure that you have the following:

- **Python Version:**  
  • Python 3.10 or higher.

- **Dependencies:**  
  • **Streamlit:** For the web-based UI.  
  • **Pydantic:** For data and report modeling.  
  • **LangGraph:** For building and executing the state workflow graphs.  
  • **python-dotenv:** For managing environment variables.  
  • **langchain_google_genai:** For interacting with Gemini LLM.  

  Refer to the requirements file (if available) or install via pip:
  
      pip install streamlit pydantic langgraph python-dotenv langchain_google_genai

Installation
------------
To set up the Code Evolution Analyzer, follow these steps:

1. **Clone the Repository:**  
   • Use Git to clone the repository:
   
         git clone https://github.com/SourabhThanvi/Code_Evaluation.git

2. **Install Dependencies:**  
   • Navigate to the repository directory and install all required packages:
   
         pip install -r requirements.txt

3. **Configure Environment Variables:**  
   • Create a **.env** file in the root directory and define your Gemini API key:
   
         GEMINI_API_KEY=your_gemini_api_key_here

4. **Run the Application:**  
   • For the Streamlit-based user interface, execute:
   
         streamlit run app.py

   • To use the API endpoints (built using FastAPI), run the main API script:
   
         python main.py

This setup ensures that the Code Evolution Analyzer is ready for both interactive and programmatic usage.

File Structure
--------------
```plaintext
Code_Evaluation/
│
├── Agent/
│   ├── client.py              # Loads Gemini/OpenAI clients
│   ├── generator.py           # Code generator using LLM
│   ├── custom_prompt.py       # Custom prompts for structured outputs
│   └── markdown_remove.py     # Helper to clean LLM markdown responses
│
├── Diff_analysis/
│   ├── analyzer.py            # AST-based code analyzer
│
├── config/
│   └── config.yaml            # YAML-based configuration
│
├── app.py                     # Streamlit UI entry point
├── main.py                    # API server entry point (FastAPI)
├── .env                       # Environment variables (e.g., API keys)
├── requirements.txt           # Required dependencies
└── README.md                  # This file
