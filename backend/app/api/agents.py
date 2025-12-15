from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import AgentRequest, AgentResponse
from app.agents.langchain_agents import get_agent
from app.services.database_services import FileDBService, MessageService
from app.schemas.schemas import MessageCreate

router = APIRouter(prefix="/agent", tags=["agents"])


@router.post("/summarizer", response_model=AgentResponse)
async def summarize_content(request: AgentRequest, db: Session = Depends(get_db)):
    """
    Generate summary from input text or uploaded file
    """
    try:
        # Validate that at least one input source is provided
        if not request.input_text and not request.file_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either input_text or file_id must be provided"
            )

        # Get input text
        if request.input_text:
            text = request.input_text
        elif request.file_id:
            file = FileDBService.get_file(db, request.file_id)
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
            text = file.extracted_text

        # Validate text is not empty
        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input text cannot be empty"
            )

        # Get summarizer agent
        agent = get_agent("summarizer")

        # Generate summary
        result = await agent.summarize(text, request.parameters)

        # Store message if chat_id is provided
        if request.chat_id:
            # Store user message
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="user",
                content=f"Summarize: {text[:100]}...",
                metadata={"agent": "summarizer", "file_id": request.file_id}
            ))

            # Store assistant response
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="assistant",
                content=result["summary"],
                metadata=result
            ))

        return AgentResponse(
            output_text=result["summary"],
            metadata=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )


@router.post("/question_generator", response_model=AgentResponse)
async def generate_questions(request: AgentRequest, db: Session = Depends(get_db)):
    """
    Generate quiz questions from input text or summary
    """
    try:
        # Validate that at least one input source is provided
        if not request.input_text and not request.file_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either input_text or file_id must be provided"
            )

        # Get input text
        if request.input_text:
            text = request.input_text
        elif request.file_id:
            file = FileDBService.get_file(db, request.file_id)
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
            text = file.extracted_text

        # Validate text is not empty
        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input text cannot be empty"
            )

        # Get question generator agent
        agent = get_agent("question_generator")

        # Generate questions
        result = await agent.generate_questions(text, request.parameters)

        # Store message if chat_id is provided
        if request.chat_id:
            # Store user message
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="user",
                content="Generate quiz questions",
                metadata={"agent": "question_generator", "file_id": request.file_id}
            ))

            # Store assistant response
            import json
            questions_text = json.dumps(result["questions"]) if isinstance(result["questions"], list) else str(result["questions"])
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="assistant",
                content=questions_text,
                metadata=result
            ))

        return AgentResponse(
            output_text=str(result["questions"]),
            metadata=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question generation failed: {str(e)}"
        )


@router.post("/explainer", response_model=AgentResponse)
async def explain_concept(request: AgentRequest, db: Session = Depends(get_db)):
    """
    Provide context-aware explanation for a question
    """
    try:
        # Validate input
        if not request.input_text or not request.input_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="input_text is required for explanations and cannot be empty"
            )

        # Get explainer agent
        agent = get_agent("explainer")

        # Retrieve context from RAG service if user_id is provided
        context = None
        if request.user_id:
            from app.services.rag_service import rag_service
            retrieval_result = await rag_service.retrieve_context(
                query=request.input_text,
                user_id=request.user_id,
                top_k=3
            )
            if retrieval_result["status"] == "success":
                context = retrieval_result["context"]

        # Generate explanation
        result = await agent.explain(
            request.input_text,
            context=context,
            parameters=request.parameters
        )

        # Store message if chat_id is provided
        if request.chat_id:
            # Store user message
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="user",
                content=request.input_text,
                metadata={"agent": "explainer"}
            ))

            # Store assistant response
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="assistant",
                content=result["explanation"],
                metadata=result
            ))

        return AgentResponse(
            output_text=result["explanation"],
            metadata=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explanation failed: {str(e)}"
        )


@router.post("/resource_recommender", response_model=AgentResponse)
async def recommend_resources(request: AgentRequest, db: Session = Depends(get_db)):
    """
    Recommend learning resources based on topic or content
    """
    try:
        # Validate input
        if not request.input_text or not request.input_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="input_text is required for resource recommendations and cannot be empty"
            )

        # Get resource recommender agent
        agent = get_agent("resource_recommender")

        # Generate recommendations
        result = await agent.recommend(request.input_text, request.parameters)

        # Store message if chat_id is provided
        if request.chat_id:
            # Store user message
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="user",
                content=f"Recommend resources for: {request.input_text}",
                metadata={"agent": "resource_recommender"}
            ))

            # Store assistant response
            import json
            resources_text = json.dumps(result["resources"]) if isinstance(result["resources"], list) else str(result["resources"])
            MessageService.create_message(db, MessageCreate(
                chat_id=request.chat_id,
                role="assistant",
                content=resources_text,
                metadata=result
            ))

        return AgentResponse(
            output_text=str(result["resources"]),
            metadata=result,
            resources=result["resources"] if isinstance(result["resources"], list) else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resource recommendation failed: {str(e)}"
        )
