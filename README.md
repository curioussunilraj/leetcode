Software Requirements Specification (SRS): Local Coder's Workspace
Version: 1.0
Date: July 12, 2025
Author: Gemini

1. Introduction
1.1 Purpose
This document specifies the complete requirements for the "Local Coder's Workspace," a self-hosted application designed for a single user to practice coding problems. The application will leverage a modern tech stack to provide an experience similar to platforms like LeetCode, but running entirely on a local machine. Its core features include AI-powered problem generation, secure multi-language code execution, and detailed submission history.

1.2 Scope
The scope of this project is a desktop application experience, accessed via a web browser, that runs entirely on the user's local machine. It is not a multi-user, cloud-hosted SaaS application. The system will handle problem generation, provide a full-featured coding IDE, execute code securely, and persist user progress locally.

1.3 Target Audience
The primary audience includes:

Software engineers preparing for technical interviews.

Computer science students learning data structures and algorithms.

Developers looking to sharpen their coding skills in various programming languages.

2. Overall Description
2.1 Product Perspective
The Local Coder's Workspace is a self-contained system composed of a frontend web application, a backend API server, and a local database. It is designed to be started with a single command. It relies on two external interfaces: the Google Gemini API for problem generation (requiring an internet connection) and the local Docker daemon for secure code execution.

2.2 High-Level Features
AI-Powered Problem Generation: Dynamically create new, unique coding problems using AI.

Multi-Language IDE: An in-browser workspace to write, test, and submit solutions in multiple languages.

Secure Sandboxed Execution: Run untrusted user code in an isolated environment with resource limits.

Interactive Debugging: Run code against custom user-defined test cases.

Rich Feedback & Analysis: Provide detailed feedback on failed test cases and performance metrics (time, memory) for successful ones.

Persistent Submission History: Track and review all past submission attempts for every problem.

2.3 User Characteristics
The intended user is technically proficient and comfortable with:

Writing code in at least one of the supported languages.

Installing and running Docker Desktop on their local machine.

Working with a command-line interface for initial setup.

2.4 Constraints
Deployment: The application is designed exclusively for local execution.

Frontend Technology: The frontend shall be built using React.

Backend Technology: The backend shall be built using Python with the FastAPI framework.

Execution Environment: Code execution shall be sandboxed using Docker containers.

Dependencies: The user must have Node.js, Python, and Docker Desktop installed. An active internet connection is required for problem generation.

3. System Architecture & Technology Stack
Component

Technology

Rationale

Orchestration

Docker Compose

For single-command startup of all services.

Frontend

React (with Vite)

Modern, component-based UI framework.

Backend

Python (with FastAPI)

High-performance, modern API development with data validation.

Database

SQLite (via SQLAlchemy)

Serverless, file-based DB for simple local persistence. SQLAlchemy provides an abstraction layer for potential future DB swaps.

Code Execution

Docker Engine

Industry standard for secure, isolated code execution.

AI Integration

Google Gemini API

For generating high-quality, structured problem data.

Communication

REST API

Standard, stateless communication between frontend and backend.


Export to Sheets
4. Functional Requirements (FR)
FR 1.0: Problem Management
FR 1.1: The user shall be able to trigger the generation of a new coding problem via the UI.

FR 1.2: The generation request shall allow the user to specify Difficulty (Easy, Medium, Hard) and Topic (e.g., Arrays, Strings, Graphs, Dynamic Programming).

FR 1.3: The backend shall send a structured prompt to the Gemini API based on the user's selections.

FR 1.4: The backend shall validate the JSON response from the AI to ensure it contains all required fields (title, description, function signature, test cases) in the correct format.

FR 1.5: Generated problems shall be saved persistently in the local SQLite database.

FR 1.6: The UI shall display a list of all previously generated problems, allowing the user to select one to work on.

FR 2.0: Coding Workspace (IDE)
FR 2.1: The IDE view shall display the selected problem's title and description. The description field must support Markdown rendering.

FR 2.2: The IDE shall provide a code editor with syntax highlighting for all supported languages.

FR 2.3: The user shall be able to select the programming language for their solution from a dropdown menu. Supported languages: Python, JavaScript, C++.

FR 2.4: The code editor's content shall be automatically saved to the browser's localStorage to prevent data loss on page refresh.

FR 2.5: The UI shall feature an optional, user-startable session timer.

FR 2.6: The UI shall provide a panel for the user to input custom test cases.

FR 2.7: The UI shall provide a "Run" button for custom tests and a "Submit" button for the full solution.

FR 3.0: Code Execution & Evaluation
FR 3.1: When the "Run" button is clicked, the system shall execute the user's code only against the provided custom test case.

FR 3.2: The output of a "Run" action shall display the code's stdout and any runtime errors.

FR 3.3: When the "Submit" button is clicked, the system shall execute the user's code against all hidden test cases stored in the database for that problem.

FR 3.4: All code execution must occur within a Docker container with strict resource limits:

Time Limit: 5 seconds

Memory Limit: 256 MB

FR 3.5: The system shall return one of the following statuses upon submission: Accepted, Wrong Answer, Time Limit Exceeded, Memory Limit Exceeded, Runtime Error.

FR 3.6: If the status is Wrong Answer, the response shall include the input that failed, the user's code output, and the expected output.

FR 3.7: If the status is Accepted, the response shall include the measured runtime (ms) and memory usage (MB) of the solution.

FR 4.0: Submission History
FR 4.1: The system shall save every submission attempt to the database, including the full source code, status, language, and performance metrics.

FR 4.2: The UI shall display a historical list of all submissions for the currently viewed problem.

FR 4.3: The user shall be able to click on a past submission to view its details and the code that was submitted.

5. Non-Functional Requirements (NFR)
NFR 1.0: Usability

NFR 1.1: The entire application stack (frontend, backend) shall be startable with a single command: docker-compose up.

NFR 1.2: The user interface shall be clean, intuitive, and responsive to different window sizes.

NFR 1.3: The application shall support both a light and a dark theme.

NFR 2.0: Security

NFR 2.1: User-submitted code must be executed in a sandboxed environment that has no access to the host machine's filesystem or network.

NFR 2.2: API keys (e.g., for Gemini) must not be hardcoded. They shall be loaded from an environment variable (.env file).

NFR 3.0: Performance

NFR 3.1: The frontend application should achieve a Lighthouse performance score of 90+ on desktop.

NFR 3.2: A standard code submission should be evaluated and return a result to the UI in under 10 seconds.

NFR 4.0: Maintainability

NFR 4.1: The backend codebase shall be clearly structured into modules (e.g., API routes, services, database models, schemas).

NFR 4.2: The API between the frontend and backend shall be well-defined and consistently structured.

6. External Interface Requirements
EIR 1.0: Google Gemini API

EIR 1.1: The system will interface with the Gemini REST API via its Python SDK.

EIR 1.2: The system will authenticate using an API key provided by the user.

EIR 1.3: The system will send prompts designed to elicit a JSON object with a predefined schema. It must handle potential API errors gracefully.

EIR 2.0: Docker Engine

EIR 2.1: The Python backend will interface with the Docker Engine installed on the host machine via the Docker SDK for Python.

EIR 2.2: The system requires permissions to: pull images, create containers, run containers with resource constraints, inspect running containers, and remove containers.







