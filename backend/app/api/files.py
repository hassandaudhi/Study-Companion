from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import FileCreate, FileResponse
from app.services.database_services import FileDBService, UserService
from app.services.file_service import file_service
from typing import List

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    user_id: int = None,
    chat_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Upload a file, extract text, and store metadata
    """
    try:
        # Validate required fields
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )

        # Verify user exists
        user = UserService.get_user(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Save file to storage
        file_info = await file_service.save_file(file, user_id)

        # Create file record in database
        file_create = FileCreate(
            user_id=user_id,
            chat_id=chat_id,
            filename=file_info["filename"],
            original_filename=file_info["original_filename"],
            file_path=file_info["file_path"],
            file_type=file_info["file_type"],
            file_size=file_info["file_size"]
        )

        db_file = FileDBService.create_file(db, file_create)

        # Extract text from file
        try:
            extracted_text = file_service.extract_text(
                file_info["file_path"],
                file_info["file_type"]
            )

            # Update file with extracted text
            db_file = FileDBService.update_file_status(
                db,
                db_file.id,
                status="processed",
                extracted_text=extracted_text
            )
        except Exception as e:
            # Update status to failed if text extraction fails
            FileDBService.update_file_status(db, db_file.id, status="failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract text: {str(e)}"
            )

        return db_file

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


@router.get("/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    """Get file metadata by ID"""
    file = FileDBService.get_file(db, file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return file


@router.get("/user/{user_id}", response_model=List[FileResponse])
def get_user_files(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all files for a user"""
    # Verify user exists
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return FileDBService.get_user_files(db, user_id, skip, limit)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Delete file and its metadata"""
    file = FileDBService.get_file(db, file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # Delete physical file
    await file_service.delete_file(file.file_path)

    # Delete database record
    FileDBService.delete_file(db, file_id)

    return None
