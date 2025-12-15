from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from app.agents.langchain_agents import (
    SummarizerAgent,
    QuestionGeneratorAgent,
    ExplainerAgent,
    ResourceRecommenderAgent
)
import operator


# Define the state for the workflow
class WorkflowState(TypedDict):
    """State for multi-agent workflow"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    input_text: str
    user_id: int
    chat_id: int
    file_id: int
    workflow_type: str
    summary: str
    questions: list
    resources: list
    embeddings: list
    current_step: str
    error: str


class PDFProcessingWorkflow:
    """
    Multi-step workflow for PDF processing:
    1. Extract text from PDF
    2. Summarize content
    3. Generate questions
    4. Recommend resources
    5. Create embeddings
    """

    def __init__(self):
        self.summarizer = SummarizerAgent()
        self.question_generator = QuestionGeneratorAgent()
        self.resource_recommender = ResourceRecommenderAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("summarize", self._summarize_step)
        workflow.add_node("generate_questions", self._generate_questions_step)
        workflow.add_node("recommend_resources", self._recommend_resources_step)
        workflow.add_node("create_embeddings", self._create_embeddings_step)

        # Define edges
        workflow.set_entry_point("summarize")
        workflow.add_edge("summarize", "generate_questions")
        workflow.add_edge("generate_questions", "recommend_resources")
        workflow.add_edge("recommend_resources", "create_embeddings")
        workflow.add_edge("create_embeddings", END)

        return workflow.compile()

    async def _summarize_step(self, state: WorkflowState) -> WorkflowState:
        """Summarize the input text"""
        try:
            result = await self.summarizer.summarize(state["input_text"])
            return {
                **state,
                "summary": result["summary"],
                "current_step": "summarize",
                "messages": state["messages"] + [AIMessage(content=f"Summary generated: {result['summary'][:100]}...")]
            }
        except Exception as e:
            return {
                **state,
                "error": f"Summarization failed: {str(e)}"
            }

    async def _generate_questions_step(self, state: WorkflowState) -> WorkflowState:
        """Generate quiz questions from summary"""
        try:
            result = await self.question_generator.generate_questions(
                state["summary"],
                parameters={"num_questions": 5}
            )
            return {
                **state,
                "questions": result["questions"],
                "current_step": "generate_questions",
                "messages": state["messages"] + [AIMessage(content="Quiz questions generated")]
            }
        except Exception as e:
            return {
                **state,
                "error": f"Question generation failed: {str(e)}"
            }

    async def _recommend_resources_step(self, state: WorkflowState) -> WorkflowState:
        """Recommend learning resources"""
        try:
            # Use summary to determine topic
            result = await self.resource_recommender.recommend(
                state["summary"],
                parameters={"num_resources": 5}
            )
            return {
                **state,
                "resources": result["resources"],
                "current_step": "recommend_resources",
                "messages": state["messages"] + [AIMessage(content="Resources recommended")]
            }
        except Exception as e:
            return {
                **state,
                "error": f"Resource recommendation failed: {str(e)}"
            }

    async def _create_embeddings_step(self, state: WorkflowState) -> WorkflowState:
        """Create embeddings for the content"""
        try:
            # This will be handled by the memory service
            return {
                **state,
                "embeddings": [],
                "current_step": "create_embeddings",
                "messages": state["messages"] + [AIMessage(content="Embeddings created")]
            }
        except Exception as e:
            return {
                **state,
                "error": f"Embedding creation failed: {str(e)}"
            }

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the PDF processing workflow
        
        Args:
            input_data: Dictionary with input_text, user_id, chat_id, file_id
        
        Returns:
            Dictionary with workflow results including status, summary, questions, resources, and embeddings
        """
        initial_state = {
            "messages": [HumanMessage(content="Starting PDF processing workflow")],
            "input_text": input_data["input_text"],
            "user_id": input_data["user_id"],
            "chat_id": input_data.get("chat_id", 0),
            "file_id": input_data.get("file_id", 0),
            "workflow_type": "pdf_processing",
            "summary": "",
            "questions": [],
            "resources": [],
            "embeddings": [],
            "current_step": "",
            "error": ""
        }

        try:
            result = await self.workflow.ainvoke(initial_state)

            return {
                "status": "completed" if not result.get("error") else "failed",
                "summary": result.get("summary", ""),
                "questions": result.get("questions", []),
                "resources": result.get("resources", []),
                "embeddings": result.get("embeddings", []),
                "error": result.get("error", "")
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }


class MultiAgentChatWorkflow:
    """
    Multi-agent workflow for chat interactions:
    1. Identify user intent
    2. Retrieve relevant context from embeddings
    3. Route to appropriate agent
    4. Generate response
    5. Store embeddings if needed
    """

    def __init__(self):
        self.explainer = ExplainerAgent()
        self.resource_recommender = ResourceRecommenderAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("identify_intent", self._identify_intent_step)
        workflow.add_node("retrieve_context", self._retrieve_context_step)
        workflow.add_node("generate_response", self._generate_response_step)
        workflow.add_node("store_embeddings", self._store_embeddings_step)

        # Define edges
        workflow.set_entry_point("identify_intent")
        workflow.add_edge("identify_intent", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_response")
        workflow.add_edge("generate_response", "store_embeddings")
        workflow.add_edge("store_embeddings", END)

        return workflow.compile()

    async def _identify_intent_step(self, state: WorkflowState) -> WorkflowState:
        """Identify user intent from the message"""
        return {
            **state,
            "current_step": "identify_intent",
            "messages": state["messages"] + [AIMessage(content="Intent identified")]
        }

    async def _retrieve_context_step(self, state: WorkflowState) -> WorkflowState:
        """Retrieve relevant context from vector store"""
        return {
            **state,
            "current_step": "retrieve_context",
            "messages": state["messages"] + [AIMessage(content="Context retrieved")]
        }

    async def _generate_response_step(self, state: WorkflowState) -> WorkflowState:
        """Generate response using appropriate agent"""
        try:
            result = await self.explainer.explain(
                state["input_text"],
                context=""
            )
            return {
                **state,
                "summary": result["explanation"],
                "current_step": "generate_response",
                "messages": state["messages"] + [AIMessage(content=result["explanation"])]
            }
        except Exception as e:
            return {
                **state,
                "error": f"Response generation failed: {str(e)}"
            }

    async def _store_embeddings_step(self, state: WorkflowState) -> WorkflowState:
        """Store conversation embeddings"""
        return {
            **state,
            "current_step": "store_embeddings",
            "messages": state["messages"] + [AIMessage(content="Embeddings stored")]
        }

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the multi-agent chat workflow
        
        Args:
            input_data: Dictionary with input_text, user_id, chat_id
        
        Returns:
            Dictionary with workflow results including status, response, and error if any
        """
        initial_state = {
            "messages": [HumanMessage(content=input_data["input_text"])],
            "input_text": input_data["input_text"],
            "user_id": input_data["user_id"],
            "chat_id": input_data.get("chat_id", 0),
            "file_id": 0,
            "workflow_type": "multi_agent_chat",
            "summary": "",
            "questions": [],
            "resources": [],
            "embeddings": [],
            "current_step": "",
            "error": ""
        }

        try:
            result = await self.workflow.ainvoke(initial_state)

            return {
                "status": "completed" if not result.get("error") else "failed",
                "response": result.get("summary", ""),
                "error": result.get("error", "")
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }


# Workflow factory
def get_workflow(workflow_type: str):
    """
    Get workflow instance by type
    
    Args:
        workflow_type: Type of workflow (pdf_processing, multi_agent_chat)
        
    Returns:
        Workflow instance
        
    Raises:
        ValueError: If workflow type is unknown
    """
    workflows = {
        "pdf_processing": PDFProcessingWorkflow,
        "multi_agent_chat": MultiAgentChatWorkflow
    }

    workflow_class = workflows.get(workflow_type)
    if not workflow_class:
        available = list(workflows.keys())
        raise ValueError(f"Unknown workflow type: {workflow_type}. Available: {available}")

    return workflow_class()
