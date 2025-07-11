from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any
import datetime

# --- Test Case Schemas ---
class TestCaseBase(BaseModel):
    input: Any # Can be string, list, dict, etc. depending on problem
    expected_output: Any # Same as input
    hidden: bool = False

class TestCaseCreate(TestCaseBase):
    pass

class TestCase(TestCaseBase):
    # id: Optional[int] = None # If we had a separate TestCase table
    # problem_id: Optional[int] = None # If we had a separate TestCase table

    class Config:
        from_attributes = True


# --- Function Signature Schemas ---
class FunctionSignatureBase(BaseModel):
    language: str = Field(..., example="python")
    signature: str = Field(..., example="def solve(arr: list[int], target: int) -> list[int]:")

class FunctionSignatureCreate(FunctionSignatureBase):
    pass

class FunctionSignature(FunctionSignatureBase):
    # id: Optional[int] = None # If we had a separate table
    # problem_id: Optional[int] = None # If we had a separate table

    class Config:
        from_attributes = True


# --- Problem Schemas ---
class ProblemBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, example="Two Sum")
    description: str = Field(..., min_length=10, example="Given an array of integers nums...")
    difficulty: str = Field(..., example="Easy") # Could be an Enum: Easy, Medium, Hard
    topic: str = Field(..., example="Arrays")    # Could be an Enum or predefined list

    # These will be mapped from/to the _json fields in the SQLAlchemy model
    function_signatures: List[FunctionSignatureCreate] = Field(..., example=[
        {"language": "python", "signature": "def twoSum(nums, target):"},
        {"language": "javascript", "signature": "function twoSum(nums, target) {}"}
    ])
    test_cases: List[TestCaseCreate] = Field(..., example=[
        {"input": {"nums": [2,7,11,15], "target": 9}, "expected_output": [0,1], "hidden": False},
        {"input": {"nums": [3,2,4], "target": 6}, "expected_output": [1,2], "hidden": False}
    ])

    @validator('difficulty')
    def difficulty_must_be_valid(cls, value):
        allowed_difficulties = ["Easy", "Medium", "Hard"]
        if value not in allowed_difficulties:
            raise ValueError(f"Difficulty must be one of {allowed_difficulties}")
        return value

    # Add more validators as needed (e.g., for topic, function_signatures, test_cases structure)

class ProblemCreate(ProblemBase):
    pass # Inherits all fields and validators from ProblemBase

class Problem(ProblemBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None # updated_at can be null if not updated

    # Override to use the non-Create versions for response model
    function_signatures: List[FunctionSignature]
    test_cases: List[TestCase]


    class Config:
        from_attributes = True # Enables creating Pydantic model from ORM model instance


# --- Submission Schemas ---
class SubmissionBase(BaseModel):
    problem_id: int
    language: str = Field(..., example="python")
    code: str = Field(..., min_length=1, example="def solve():\n  return 42")

    @validator('language')
    def language_must_be_supported(cls, value):
        supported_languages = ["python", "javascript", "cpp"] # FR 2.3
        if value.lower() not in supported_languages:
            raise ValueError(f"Language must be one of {supported_languages}")
        return value.lower()


class SubmissionCreate(SubmissionBase):
    pass # No extra fields on creation beyond base

class Submission(SubmissionBase):
    id: int
    submitted_at: datetime.datetime
    status: Optional[str] = Field(None, example="Accepted") # Accepted, Wrong Answer, TLE, MLE, Runtime Error, Pending
    runtime_ms: Optional[int] = Field(None, example=100)
    memory_mb: Optional[int] = Field(None, example=10)

    output: Optional[str] = None # Combined stdout/stderr or error message
    failed_test_case_input: Optional[Any] = None
    failed_test_case_expected_output: Optional[Any] = None
    failed_test_case_actual_output: Optional[Any] = None


    class Config:
        from_attributes = True


# --- For AI Problem Generation Request ---
class AIProblemGenerationRequest(BaseModel):
    difficulty: str = Field(..., example="Medium")
    topic: str = Field(..., example="Dynamic Programming")

    @validator('difficulty')
    def difficulty_must_be_valid(cls, value):
        allowed_difficulties = ["Easy", "Medium", "Hard"]
        if value not in allowed_difficulties:
            raise ValueError(f"Difficulty must be one of {allowed_difficulties}")
        return value

    # We might want to add more specific validation for topics if we have a predefined list.


# --- For Code Execution Request (Custom Test) ---
class CodeExecutionRequest(BaseModel):
    language: str
    code: str
    custom_input: Optional[Any] = None # Input for a single custom test case

    @validator('language')
    def language_must_be_supported(cls, value):
        supported_languages = ["python", "javascript", "cpp"] # FR 2.3
        if value.lower() not in supported_languages:
            raise ValueError(f"Language must be one of {supported_languages}")
        return value.lower()

# --- For Code Execution Response (Custom Test) ---
class CodeExecutionResponse(BaseModel):
    success: bool # True if execution completed (even if code is wrong), False if system error during execution
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[str] = None # For system errors or compilation errors not part of stderr
    runtime_ms: Optional[int] = None # Optional, might not be measured for simple runs
    # memory_mb: Optional[int] = None # Optional, might not be measured for simple runs

    # If we want to include evaluation against custom input's expected output (if provided by user)
    # input_provided: Optional[Any] = None
    # expected_output_provided: Optional[Any] = None
    # actual_output: Optional[Any] = None # Parsed from stdout if possible
    # match: Optional[bool] = None

    # For now, simple stdout/stderr is enough for FR 3.2
    # "The output of a "Run" action shall display the code's stdout and any runtime errors."

class SubmissionFullDetails(Submission):
    # Could potentially include problem details if needed in one go, but usually fetched separately
    # problem: Optional[Problem] = None
    pass
