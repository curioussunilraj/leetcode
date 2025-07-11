from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, models, schemas # Updated imports for modular structure
from app.database import SessionLocal, engine, create_db_and_tables # Updated database imports
from app.config import settings # Import settings

# Potentially create tables on startup if they don't exist (Alembic handles migrations)
# This is useful for the very first run or in simple setups.
# For production, you'd typically run Alembic migrations separately.
# models.Base.metadata.create_all(bind=engine)
# Let's make this conditional or part of a startup event.

app = FastAPI(
    title="Local Coder's Workspace API",
    description="API for managing coding problems, submissions, and code execution.",
    version="0.1.0",
    #openapi_url=f"{settings.API_V1_STR}/openapi.json" # Example if using API versioning
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    # This is a good place to ensure tables are created, especially for SQLite,
    # if not solely relying on Alembic for the very first setup.
    # models.Base.metadata.create_all(bind=engine)
    # The create_db_and_tables function in database.py now calls Base.metadata.create_all(bind=engine)
    # We can call it here.
    # This is mainly for convenience in local development before Alembic migrations are fully established,
    # or for environments where running migrations explicitly first isn't desired.
    # For a robust setup, Alembic should be the primary way to manage schema.
    # However, for SQLite, create_all is often harmless and convenient.
    print("FastAPI startup: Attempting to create database and tables if they don't exist.")
    try:
        create_db_and_tables()
        print("Database and tables checked/created on startup.")
    except Exception as e:
        print(f"Error during startup table creation: {e}")
    # Note: If Alembic is managing the schema, this create_all might be redundant
    # or could conflict if the models and migrations are out of sync.
    # For now, including it for initial ease of setup. Can be removed if pure Alembic workflow is enforced.


# --- API Endpoints ---

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Local Coder's Workspace API!"}

# FR 1.0: Problem Management
# FR 1.1, FR 1.2, FR 1.3 (partially, AI gen not implemented yet)
@app.post("/problems/", response_model=schemas.Problem, status_code=201, tags=["Problems"])
async def create_new_problem(problem: schemas.ProblemCreate, db: Session = Depends(get_db)):
    # Actual AI generation (FR 1.3) will be a separate step/service call here or in crud.
    # For now, this creates a problem directly from the input schema.
    # FR 1.5: Saved persistently (handled by crud.create_problem)
    # FR 1.4: Validation (handled by Pydantic in schemas.ProblemCreate)
    return crud.create_problem(db=db, problem=problem)

# FR 1.6
@app.get("/problems/", response_model=List[schemas.Problem], tags=["Problems"])
async def read_problems(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    problems = crud.get_problems(db, skip=skip, limit=limit)
    return problems

@app.get("/problems/{problem_id}", response_model=schemas.Problem, tags=["Problems"])
async def read_problem(problem_id: int, db: Session = Depends(get_db)):
    db_problem = crud.get_problem(db, problem_id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return db_problem

# Endpoint for AI Problem Generation (FR 1.1, FR 1.2, FR 1.3)
@app.post("/problems/generate/", response_model=schemas.Problem, status_code=201, tags=["Problems"])
async def generate_ai_problem(
    request: schemas.AIProblemGenerationRequest,
    db: Session = Depends(get_db)
):
    # Placeholder for Gemini API call and processing
    # This would involve:
    # 1. Constructing a prompt based on request.difficulty and request.topic.
    # 2. Calling the Gemini API.
    # 3. Validating the AI's JSON response (FR 1.4).
    # 4. Creating a schemas.ProblemCreate object from the AI response.
    # 5. Saving it using crud.create_problem.

    # --- Placeholder ---
    print(f"Received AI problem generation request: Difficulty='{request.difficulty}', Topic='{request.topic}'")
    # Simulate AI response
    simulated_ai_response_data = {
        "title": f"Generated {request.difficulty} Problem on {request.topic}",
        "description": f"This is an AI-generated problem about {request.topic} with {request.difficulty} difficulty. Implement the solution.",
        "difficulty": request.difficulty,
        "topic": request.topic,
        "function_signatures": [
            {"language": "python", "signature": f"def solve_{request.topic.lower().replace(' ', '_')}(params):"},
            {"language": "javascript", "signature": f"function solve{request.topic.title().replace(' ', '')}(params) {{}}"}
        ],
        "test_cases": [
            {"input": "sample_input_1", "expected_output": "sample_output_1", "hidden": False},
            {"input": "sample_input_2", "expected_output": "sample_output_2", "hidden": True}
        ]
    }
    try:
        problem_create_data = schemas.ProblemCreate(**simulated_ai_response_data)
    except Exception as e: # Catch Pydantic validation error or others
        raise HTTPException(status_code=500, detail=f"Failed to process AI response into ProblemCreate schema: {e}")

    return crud.create_problem(db=db, problem=problem_create_data)
    # --- End Placeholder ---


# FR 3.0: Code Execution & Evaluation (Submission)
# FR 2.7 (Submit button), FR 3.3
@app.post("/submissions/", response_model=schemas.Submission, status_code=201, tags=["Submissions"])
async def create_new_submission(
    submission_create: schemas.SubmissionCreate,
    db: Session = Depends(get_db)
):
    # FR 4.1: Save every submission attempt (initial save with "Pending")
    db_problem = crud.get_problem(db, problem_id=submission_create.problem_id)
    if not db_problem:
        raise HTTPException(status_code=404, detail=f"Problem with id {submission_create.problem_id} not found.")

    submission = crud.create_submission(db=db, submission=submission_create)

    # --- Placeholder for actual code execution via Docker ---
    # This part will be expanded significantly.
    # 1. Get problem's hidden test cases (db_problem.test_cases, filter for hidden or use all)
    # 2. For each test case:
    #    a. Prepare Docker container with user's code (submission.code) and test input.
    #    b. Run container with resource limits (FR 3.4: Time 5s, Memory 256MB).
    #    c. Capture stdout, stderr, execution time, memory usage.
    #    d. Compare output with expected output.
    # 3. Determine overall status (Accepted, Wrong Answer, TLE, MLE, Runtime Error - FR 3.5).
    # 4. If Wrong Answer, include details (FR 3.6).
    # 5. If Accepted, include performance (FR 3.7).
    # 6. Update the submission record in the DB with results using crud.update_submission_status.

    # Simulate execution and update
    simulated_status = "Accepted" # or "Wrong Answer", "Time Limit Exceeded", etc.
    simulated_runtime_ms = 120
    simulated_memory_mb = 15
    simulated_output_text = "Simulated execution output."

    # Example for failed test case
    # simulated_status = "Wrong Answer"
    # simulated_output_text = "Runtime error: Division by zero"
    # failed_input = db_problem.test_cases[0].input if db_problem.test_cases else "N/A"
    # expected_output = db_problem.test_cases[0].expected_output if db_problem.test_cases else "N/A"
    # actual_output = "Some simulated actual output"

    updated_submission = crud.update_submission_status(
        db=db,
        submission_id=submission.id,
        status=simulated_status,
        runtime_ms=simulated_runtime_ms,
        memory_mb=simulated_memory_mb,
        output=simulated_output_text
        # failed_test_case_input=str(failed_input) if simulated_status == "Wrong Answer" else None,
        # failed_test_case_expected_output=str(expected_output) if simulated_status == "Wrong Answer" else None,
        # failed_test_case_actual_output=actual_output if simulated_status == "Wrong Answer" else None,
    )
    if not updated_submission:
        # This should ideally not happen if submission was just created
        raise HTTPException(status_code=500, detail="Failed to update submission after simulated execution.")

    # NFR 3.2: standard code submission should be evaluated and return a result to the UI in under 10 seconds.
    # The actual Docker execution will be the time-consuming part.

    return updated_submission
    # --- End Placeholder ---

# FR 2.0: Coding Workspace (IDE) related backend parts
# FR 2.7 ("Run" button for custom tests), FR 3.1, FR 3.2
@app.post("/execute-custom/", response_model=schemas.CodeExecutionResponse, tags=["Execution"])
async def execute_custom_code(
    request: schemas.CodeExecutionRequest,
    # db: Session = Depends(get_db) # DB might not be needed if not saving this run
):
    # This endpoint is for running code against a single, user-provided custom test case.
    # It does NOT save a submission.
    # 1. Prepare Docker container with user's code (request.code) and custom input (request.custom_input).
    # 2. Run container with resource limits (FR 3.4, though maybe more lenient for custom runs or configurable).
    # 3. Capture stdout, stderr (FR 3.2).
    # 4. Return stdout, stderr, and any runtime errors.

    # --- Placeholder for actual code execution via Docker ---
    print(f"Executing custom code for language: {request.language}")
    print(f"Code: \n{request.code}")
    print(f"Custom Input: {request.custom_input}")

    # Simulate execution
    simulated_stdout = f"Output for custom input: {request.custom_input}"
    simulated_stderr = ""
    simulated_error = None # e.g., "Compilation failed." or "System error during execution."
    simulated_success = True # If execution itself completed, not about code correctness

    # if request.language == "python" and "error" in request.code:
    #     simulated_stderr = "Traceback: \n  File \"solution.py\", line X, in <module>\n    raise ValueError(\"test error\")\nValueError: test error"
    #     simulated_success = True # Still true, code ran but had runtime error
    # elif "compile_error" in request.code: # Fictional example
    #     simulated_error = "Compilation Error: Syntax error at line Y"
    #     simulated_success = False


    return schemas.CodeExecutionResponse(
        success=simulated_success,
        stdout=simulated_stdout,
        stderr=simulated_stderr,
        error=simulated_error
        # runtime_ms can also be returned if measured
    )
    # --- End Placeholder ---


# FR 4.0: Submission History
# FR 4.2
@app.get("/problems/{problem_id}/submissions/", response_model=List[schemas.Submission], tags=["Submissions"])
async def read_submissions_for_problem(
    problem_id: int,
    skip: int = 0, limit: int = 30,
    db: Session = Depends(get_db)
):
    db_problem = crud.get_problem(db, problem_id=problem_id)
    if not db_problem:
        raise HTTPException(status_code=404, detail=f"Problem with id {problem_id} not found.")

    submissions = crud.get_submissions_for_problem(db, problem_id=problem_id, skip=skip, limit=limit)
    return submissions

# FR 4.3
@app.get("/submissions/{submission_id}", response_model=schemas.SubmissionFullDetails, tags=["Submissions"]) # Using SubmissionFullDetails for potential future expansion
async def read_submission(submission_id: int, db: Session = Depends(get_db)):
    db_submission = crud.get_submission(db, submission_id=submission_id)
    if db_submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return db_submission


if __name__ == "__main__":
    import uvicorn
    # This setup is for running uvicorn directly. Docker CMD will handle it in container.
    # Ensure that the host and port match what Dockerfile/docker-compose might expect if overriding.
    # The WORKDIR in Docker is /app, so uvicorn main:app will look for /app/main.py
    # This is correct as per our Dockerfile.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["app"])
