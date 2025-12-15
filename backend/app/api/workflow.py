from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from app.services.database_services import WorkflowDBService, FileDBService, MessageService
from app.schemas.schemas import MessageCreate
from typing import Dict, Any

router = APIRouter(prefix="/workflow", tags=["workflows"])


async def run_pdf_processing_workflow(
    workflow_id: int,
    input_data: Dict[str, Any]
):
    """
    Background task to run PDF processing workflow
    """
    from app.workflows.langgraph_workflows import get_workflow
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        # Update workflow status to running
        WorkflowDBService.update_workflow(
            db,
            workflow_id,
            WorkflowUpdate(status="running")
        )

        # Get workflow instance
        workflow = get_workflow("pdf_processing")

        # Run workflow
        result = await workflow.run(input_data)

        # Update workflow with results
        WorkflowDBService.update_workflow(
            db,
            workflow_id,
            WorkflowUpdate(
                status=result["status"],
                output_data=result,
                error_message=result.get("error", "")
            )
        )

        # Store results in messages if chat_id is provided
        if input_data.get("chat_id"):
            chat_id = input_data["chat_id"]

            # Store summary
            if result.get("summary"):
                MessageService.create_message(db, MessageCreate(
                    chat_id=chat_id,
                    role="assistant",
                    content=result["summary"],
                    metadata={"type": "summary", "workflow_id": workflow_id}
                ))

            # Store questions
            if result.get("questions"):
                import json
                questions_text = json.dumps(result["questions"]) if isinstance(result["questions"], list) else str(result["questions"])
                MessageService.create_message(db, MessageCreate(
                    chat_id=chat_id,
                    role="assistant",
                    content=questions_text,
                    metadata={"type": "questions", "workflow_id": workflow_id}
                ))

            # Store resources
            if result.get("resources"):
                resources_text = json.dumps(result["resources"]) if isinstance(result["resources"], list) else str(result["resources"])
                MessageService.create_message(db, MessageCreate(
                    chat_id=chat_id,
                    role="assistant",
                    content=resources_text,
                    metadata={"type": "resources", "workflow_id": workflow_id}
                ))

    except Exception as e:
        # Update workflow status to failed
        WorkflowDBService.update_workflow(
            db,
            workflow_id,
            WorkflowUpdate(
                status="failed",
                error_message=str(e)
            )
        )
    finally:
        db.close()


async def run_multi_agent_chat_workflow(
    workflow_id: int,
    input_data: Dict[str, Any]
):
    """
    Background task to run multi-agent chat workflow
    """
    from app.workflows.langgraph_workflows import get_workflow
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        # Update workflow status to running
        WorkflowDBService.update_workflow(
            db,
            workflow_id,
            WorkflowUpdate(status="running")
        )

        # Get workflow instance
        workflow = get_workflow("multi_agent_chat")

        # Run workflow
        result = await workflow.run(input_data)

        # Update workflow with results
        WorkflowDBService.update_workflow(
            db,
            workflow_id,
            WorkflowUpdate(
                status=result["status"],
                output_data=result,
                error_message=result.get("error", "")
            )
        )

        # Store results in messages if chat_id is provided
        if input_data.get("chat_id") and result.get("response"):
            MessageService.create_message(db, MessageCreate(
                chat_id=input_data["chat_id"],
                role="assistant",
                content=result["response"],
                metadata={"workflow_id": workflow_id}
            ))

    except Exception as e:
        # Update workflow status to failed
        WorkflowDBService.update_workflow(
            db,
            workflow_id,
            WorkflowUpdate(
                status="failed",
                error_message=str(e)
            )
        )
    finally:
        db.close()


@router.post("/run", response_model=WorkflowResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_workflow(
    workflow_request: WorkflowCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger a multi-agent workflow
    
    Supported workflow types:
    - pdf_processing: Upload PDF → Summarize → Generate Questions → Recommend Resources
    - multi_agent_chat: Context retrieval → Agent response → Store embeddings
    """
    try:
        # Create workflow record
        workflow = WorkflowDBService.create_workflow(db, workflow_request)

        # Prepare input data
        input_data = workflow_request.input_data or {}
        input_data["user_id"] = workflow_request.user_id
        input_data["chat_id"] = workflow_request.chat_id

        # Validate input based on workflow type
        if workflow_request.workflow_type == "pdf_processing":
            if "input_text" not in input_data and "file_id" not in input_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="pdf_processing workflow requires 'input_text' or 'file_id'"
                )

            # If file_id is provided, get the file and extract text
            if "file_id" in input_data:
                file = FileDBService.get_file(db, input_data["file_id"])
                if not file:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="File not found"
                    )
                if not file.extracted_text:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File has no extracted text"
                    )
                input_data["input_text"] = file.extracted_text

            # Add background task
            background_tasks.add_task(
                run_pdf_processing_workflow,
                workflow.id,
                input_data
            )

        elif workflow_request.workflow_type == "multi_agent_chat":
            if "input_text" not in input_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="multi_agent_chat workflow requires 'input_text'"
                )

            # Add background task
            background_tasks.add_task(
                run_multi_agent_chat_workflow,
                workflow.id,
                input_data
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown workflow type: {workflow_request.workflow_type}"
            )

        return workflow

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow creation failed: {str(e)}"
        )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow_status(workflow_id: int, db: Session = Depends(get_db)):
    """Get workflow status and results"""
    workflow = WorkflowDBService.get_workflow(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    return workflow


@router.get("/user/{user_id}", response_model=list[WorkflowResponse])
def get_user_workflows(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all workflows for a user"""
    return WorkflowDBService.get_user_workflows(db, user_id, skip, limit)
