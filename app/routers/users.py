from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.database import get_db
from app.models import User
# --- vvvv ADD/UPDATE IMPORTS vvvv ---
from app.schemas import UserRead, UserUpdate, UserPasswordChange
from app.security import get_current_user, get_password_hash, verify_password
# --- ^^^^ END IMPORTS ^^^^ ---

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Fetch the details of the currently authenticated user.
    """
    return current_user


@router.put("/me", response_model=UserRead)
def update_users_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the details (full_name, email, location) of the currently authenticated user.
    """
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided")

    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = db.exec(select(User).where(User.email == update_data["email"])).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered by another user")

    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        print(f"Error updating user: {e}") 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update user details")

# --- vvvv ADD THIS NEW ENDPOINT vvvv ---
@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_user_password(
    password_data: UserPasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Allows a logged-in user to change their own password.
    """
    # 1. Verify the user's old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password."
        )
        
    # 2. Check if new password is too short
    if len(password_data.new_password) < 8:
         raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password must be at least 8 characters long."
        )

    # 3. Hash the new password and save it
    try:
        current_user.hashed_password = get_password_hash(password_data.new_password)
        db.add(current_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating password: {e}"
        )
    
    return # Return 204 No Content
# --- ^^^^ END NEW ENDPOINT ^^^^ ---