from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For server_default=func.now()

from .database import Base
import datetime

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String, nullable=False) # Easy, Medium, Hard
    topic = Column(String, nullable=False) # Arrays, Strings, Graphs, etc.

    # Store function signatures and test cases as JSON
    # FR 1.4: "validate the JSON response from the AI to ensure it contains all required fields"
    # This implies we receive them structured, JSON is a natural fit for DB storage.
    # Example for function_signatures: [{"language": "python", "signature": "def solve():"}, ...]
    # Example for test_cases: [{"input": "...", "expected_output": "...", "hidden": false}, ...]
    function_signatures_json = Column(JSON, nullable=False, name="function_signatures") # Renamed to avoid clash
    test_cases_json = Column(JSON, nullable=False, name="test_cases") # Renamed to avoid clash

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    submissions = relationship("Submission", back_populates="problem")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    language = Column(String, nullable=False)
    code = Column(Text, nullable=False)

    status = Column(String, nullable=True) # Accepted, Wrong Answer, TLE, MLE, Runtime Error, Pending
    runtime_ms = Column(Integer, nullable=True)
    memory_mb = Column(Integer, nullable=True)

    # For detailed feedback on failure (FR 3.6)
    output = Column(Text, nullable=True) # stdout/stderr from execution, or error message
    failed_test_case_input = Column(Text, nullable=True)
    failed_test_case_expected_output = Column(Text, nullable=True)
    failed_test_case_actual_output = Column(Text, nullable=True)

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    problem = relationship("Problem", back_populates="submissions")


# If we need a separate TestCase table linked to Problem (more normalized):
# class TestCase(Base):
#     __tablename__ = "test_cases"
#     id = Column(Integer, primary_key=True, index=True)
#     problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
#     input_data = Column(Text, nullable=False)
#     expected_output_data = Column(Text, nullable=False)
#     is_hidden = Column(Boolean, default=True, nullable=False)
#     problem = relationship("Problem", back_populates="test_cases_rel")
# Problem.test_cases_rel = relationship("TestCase", order_by=TestCase.id, back_populates="problem", cascade="all, delete-orphan")

# For now, keeping test_cases and function_signatures as JSON fields on Problem model is simpler
# and aligns with the idea of getting a structured JSON from Gemini.
# This avoids managing another table and relationship for now.
# We can normalize later if performance or query needs dictate.
    # The names in the model are `function_signatures_json` and `test_cases_json`.
    # We add properties to the model to allow Pydantic's `from_orm` to easily
    # convert these JSON fields into lists of Pydantic schema instances.

    @property
    def function_signatures(self):
        # This property will be used by Pydantic when from_attributes=True
        # It assumes the `schemas` module is available here or imported appropriately.
        # For now, this definition is conceptual. The actual parsing might be
        # better handled in the CRUD layer or via a custom Pydantic validator/serializer
        # if we want to keep models strictly about DB structure.
        # However, for `from_orm` to work seamlessly with nested Pydantic models,
        # the ORM model needs to present attributes that match the Pydantic field names.
        if self.function_signatures_json:
            # Assuming schemas.FunctionSignature is defined and can validate the dicts
            # This dynamic import is not ideal, but shows the intent.
            # from . import schemas # Avoid circular import if schemas imports models
            # return [schemas.FunctionSignature.model_validate(fs) for fs in self.function_signatures_json]
            return self.function_signatures_json # Pydantic will handle validation if type hint is List[FunctionSignatureSchema]
        return []

    @property
    def test_cases(self):
        if self.test_cases_json:
            # from . import schemas # Avoid circular import
            # return [schemas.TestCase.model_validate(tc) for tc in self.test_cases_json]
            return self.test_cases_json # Pydantic will handle validation
        return []
