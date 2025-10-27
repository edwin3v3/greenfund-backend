from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app import models, schemas, security # Make sure these imports are correct
from app.database import get_db
from typing import Annotated # Import Annotated

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.exec(select(models.User).where(
        models.User.email == user_create.email)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")
    
    hashed_password = security.get_password_hash(user_create.password)
    
    # Use your original model validation
    db_user = models.User.model_validate(
        user_create, update={'hashed_password': hashed_password}
    )
    # Or, if that fails, use this:
    # db_user = models.User(
    #     email=user_create.email,
    #     full_name=user_create.full_name,
    #     location=user_create.location,
    #     hashed_password=hashed_password
    # )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- THIS IS THE FIX ---
@router.post("/token", response_model=schemas.Token)
# --- END FIX ---
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], # Use Annotated
    db: Session = Depends(get_db)
):
    user = db.exec(select(models.User).where(
        models.User.email == form_data.username)).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password", 
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # Check if ACCESS_TOKEN_EXPIRE_MINUTES is in your security file
    # If not, just remove the 'expires_delta' part
    try:
        expires_minutes = security.ACCESS_TOKEN_EXPIRE_MINUTES
    except AttributeError:
        expires_minutes = 30 # Default to 30 minutes if not set

    access_token_expires = timedelta(minutes=expires_minutes)
    
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}