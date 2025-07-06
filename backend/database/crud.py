from sqlalchemy.orm import Session
from . import models

# --- Validation Cases ---

def get_validation_case(db: Session, case_id: str):
    return db.query(models.ValidationCase).filter(models.ValidationCase.case_id == case_id).first()

def get_all_validation_cases(db: Session):
    return db.query(models.ValidationCase).all()

def create_validation_case(db: Session, case_id: str, clinical_history: str):
    db_case = models.ValidationCase(case_id=case_id, clinical_history=clinical_history)
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

# --- User Submissions ---

def create_user_submission(db: Session, query: str):
    db_submission = models.UserSubmission(query=query)
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

# --- Validation Submissions ---

def create_validation_submission(db: Session, user_identifier: str, case_id: str, answer: str, user_group: str):
    db_submission = models.ValidationSubmission(
        user_identifier=user_identifier,
        case_id=case_id,
        answer=answer,
        user_group=user_group
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_all_validation_submissions(db: Session):
    return db.query(models.ValidationSubmission).order_by(models.ValidationSubmission.user_identifier, models.ValidationSubmission.case_id).all()

def delete_all_validation_submissions(db: Session):
    num_rows_deleted = db.query(models.ValidationSubmission).delete()
    db.commit()
    return num_rows_deleted 