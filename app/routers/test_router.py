from fastapi import APIRouter

# Ensure the variable is named 'router'
router = APIRouter(
    prefix="/api/v1/test",  # Prefix defined inside
    tags=["test"],
)


@router.get("/hello")
def read_hello():
    print("--- Test route /api/v1/test/hello was hit! ---")
    return {"message": "Test route is working!"}
