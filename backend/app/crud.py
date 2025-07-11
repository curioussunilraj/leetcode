from sqlalchemy.orm import Session
from . import models, schemas
# import json # No longer needed for this specific mapping if properties work as expected

# With the @property additions in models.Problem, Pydantic's from_orm (or model_validate with from_attributes=True)
# should be able to handle the conversion for function_signatures and test_cases.

def get_problem(db: Session, problem_id: int) -> Optional[schemas.Problem]:
    db_problem = db.query(models.Problem).filter(models.Problem.id == problem_id).first()
    if db_problem:
        # Pydantic V2 uses from_orm on the schema class
        return schemas.Problem.from_orm(db_problem)
    return None

def get_problems(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Problem]:
    db_problems = db.query(models.Problem).offset(skip).limit(limit).all()
    # Pydantic V2 uses from_orm on the schema class
    return [schemas.Problem.from_orm(p) for p in db_problems]

def create_problem(db: Session, problem: schemas.ProblemCreate) -> schemas.Problem:
    db_problem = models.Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        topic=problem.topic,
        function_signatures_json=[fs.model_dump() for fs in problem.function_signatures],
        test_cases_json=[tc.model_dump() for tc in problem.test_cases]
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    # Pydantic V2 uses from_orm on the schema class
    return schemas.Problem.from_orm(db_problem)

# update_problem, delete_problem can be added later if needed.
# For update, you'd fetch the problem, update its fields (including _json fields), commit, refresh, then from_orm.

def create_submission(db: Session, submission: schemas.SubmissionCreate) -> schemas.Submission:
    db_submission = models.Submission(
        problem_id=submission.problem_id,
        language=submission.language,
        code=submission.code,
        # Status, runtime, memory, etc., will be updated after execution
        status="Pending" # Initial status
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return schemas.Submission.from_orm(db_submission)

def update_submission_status(
    db: Session,
    submission_id: int,
    status: str,
    runtime_ms: Optional[int] = None,
    memory_mb: Optional[int] = None,
    output: Optional[str] = None,
    failed_test_case_input: Optional[str] = None, # Assuming these are stringified for DB
    failed_test_case_expected_output: Optional[str] = None,
    failed_test_case_actual_output: Optional[str] = None
) -> Optional[schemas.Submission]:
    db_submission = db.query(models.Submission).filter(models.Submission.id == submission_id).first()
    if db_submission:
        db_submission.status = status
        db_submission.runtime_ms = runtime_ms
        db_submission.memory_mb = memory_mb
        db_submission.output = output
        db_submission.failed_test_case_input = failed_test_case_input
        db_submission.failed_test_case_expected_output = failed_test_case_expected_output
        db_submission.failed_test_case_actual_output = failed_test_case_actual_output

        db.commit()
        db.refresh(db_submission)
        return schemas.Submission.from_orm(db_submission)
    return None

def get_submission(db: Session, submission_id: int) -> Optional[schemas.Submission]:
    db_submission = db.query(models.Submission).filter(models.Submission.id == submission_id).first()
    if db_submission:
        return schemas.Submission.from_orm(db_submission)
    return None

def get_submissions_for_problem(db: Session, problem_id: int, skip: int = 0, limit: int = 100) -> List[schemas.Submission]:
    submissions = db.query(models.Submission)\
        .filter(models.Submission.problem_id == problem_id)\
        .order_by(models.Submission.submitted_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return [schemas.Submission.from_orm(s) for s in submissions]

# Type hinting imports
from typing import Optional, List

# Note: For `_map_problem_model_to_schema`, we are doing manual mapping.
# Pydantic's `from_orm` can have issues with complex nested structures or when field names
# differ significantly (like `test_cases` vs `test_cases_json`).
# A more robust way might involve custom `model_validator` in the Pydantic schema if direct `from_orm` is preferred.
# However, for this specific case where JSON fields in model need to be parsed into lists of Pydantic models,
# this explicit mapping in `crud` is clear and effective.
# schemas.Problem.from_orm(db_problem) would not work directly due to function_signatures_json and test_cases_json.
# We could add properties to the SQLAlchemy model `Problem` that do the parsing,
# and then `from_orm` might work if `Config.from_attributes = True` is set.
# Example property in models.Problem:
# @property
# def function_signatures(self):
#     return [schemas.FunctionSignature.model_validate(fs) for fs in self.function_signatures_json]
#
# And then schemas.Problem would list `function_signatures: List[schemas.FunctionSignature]`
# This is a cleaner approach. Let's consider refactoring to that.

# Refactoring `_map_problem_model_to_schema` by adding properties to the SQLAlchemy model
# is a good idea for future enhancement. For now, this explicit mapping works.
