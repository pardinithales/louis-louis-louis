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

def create_validation_submission(db: Session, user_identifier: str, case_id: str, answer: str, user_group: str, user_type: str):
    db_submission = models.ValidationSubmission(
        user_identifier=user_identifier,
        case_id=case_id,
        answer=answer,
        user_group=user_group,
        user_type=user_type
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

def create_sus_response(db: Session, user_identifier: str, q1: int, q2: int, q3: int, q4: int, q5: int, q6: int, q7: int, q8: int, q9: int, q10: int):
    db_sus = models.SUSResponse(
        user_identifier=user_identifier,
        q1=q1,
        q2=q2,
        q3=q3,
        q4=q4,
        q5=q5,
        q6=q6,
        q7=q7,
        q8=q8,
        q9=q9,
        q10=q10
    )
    db.add(db_sus)
    db.commit()
    db.refresh(db_sus)
    return db_sus 

def get_all_sus_responses(db: Session):
    return db.query(models.SUSResponse).order_by(models.SUSResponse.user_identifier, models.SUSResponse.created_at).all()

def delete_all_sus_responses(db: Session):
    num_rows_deleted = db.query(models.SUSResponse).delete()
    db.commit()
    return num_rows_deleted 