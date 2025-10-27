from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, desc, func 
from typing import List

from app.database import get_db
# 1. Import Notification model
from app.models import ForumThread, ForumPost, User, Badge, UserBadge, Notification 
from app.schemas import ( 
    ForumThreadCreate, ForumThreadReadBasic, ForumThreadReadWithPosts,
    ForumPostCreate, ForumPostRead
)
from app.security import get_current_user

router = APIRouter(prefix="/forum", tags=["Forum"])

# --- Thread Endpoints ---
@router.post("/threads", response_model=ForumThreadReadBasic, status_code=status.HTTP_201_CREATED)
def create_thread(
    thread_data: ForumThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_thread = ForumThread(**thread_data.model_dump(),
                                owner_id=current_user.id)
        db.add(db_thread)
        db.commit()
        db.refresh(db_thread)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating thread: {e}")

    # --- Badge Logic (Community Member) ---
    try:
        thread_count = db.exec(
            select(func.count(ForumThread.id))
            .where(ForumThread.owner_id == current_user.id)
        ).one()

        if thread_count == 1:
            badge_name = "Community Member"
            badge = db.exec(select(Badge).where(Badge.name == badge_name)).first()
            if badge:
                existing_link = db.get(UserBadge, (current_user.id, badge.id))
                if not existing_link:
                    new_badge_link = UserBadge(user_id=current_user.id, badge_id=badge.id)
                    db.add(new_badge_link)
                    db.commit()
    except Exception as e:
        print(f"Error awarding 'Community Member' badge: {e}")
    # --- End Badge Logic ---

    # Eagerly load owner if necessary before returning
    _ = db_thread.owner 
    return db_thread


@router.get("/threads", response_model=List[ForumThreadReadBasic])
def get_all_threads(
    skip: int = 0,
    limit: int = 20, 
    db: Session = Depends(get_db),
):
    statement = (
        select(ForumThread)
        .order_by(desc(ForumThread.created_at))
        .offset(skip)
        .limit(limit)
    )
    threads = db.exec(statement).all()
    # Ensure owner data is loaded if relationships are lazy
    # for thread in threads:
    #     _ = thread.owner 
    return threads


@router.get("/threads/{thread_id}", response_model=ForumThreadReadWithPosts)
def get_thread_by_id(
    thread_id: int,
    db: Session = Depends(get_db),
):
    db_thread = db.get(ForumThread, thread_id)

    if not db_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    # Ensure relationships are loaded for Pydantic conversion
    _ = db_thread.owner
    for post in db_thread.posts:
        _ = post.owner

    db_thread.posts.sort(key=lambda p: p.created_at)

    return db_thread

# --- Post Endpoints ---
@router.post("/posts", response_model=ForumPostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: ForumPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_thread = db.get(ForumThread, post_data.thread_id)
    if not db_thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Thread not found, cannot post reply.")

    try:
        db_post = ForumPost(**post_data.model_dump(), owner_id=current_user.id)
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating post: {e}")

    # --- vvvv NOTIFICATION LOGIC vvvv ---
    try:
        # Check if the poster is different from the thread owner
        if db_thread.owner_id != current_user.id:
            # Create a notification for the thread owner
            # Use poster's full name if available, otherwise email
            poster_name = current_user.full_name or current_user.email
            notification_message = f"{poster_name} replied to your thread '{db_thread.title}'."
            
            new_notification = Notification(
                user_id=db_thread.owner_id, # Notify the thread owner
                message=notification_message,
                post_id=db_post.id # Link notification to the new post
            )
            db.add(new_notification)
            db.commit() # Commit the notification separately
            
    except Exception as e:
        # Log error but don't fail the post creation
        # Rollback might be needed if the commit above fails, but depends on session state
        # db.rollback() 
        print(f"ERROR: Could not create notification for post {db_post.id}: {e}")
    # --- ^^^^ END NOTIFICATION LOGIC ^^^^ ---

    # Ensure owner is loaded for the response
    _ = db_post.owner 
    
    return db_post