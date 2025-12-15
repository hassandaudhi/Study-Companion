"""
LangChain Agent Implementations for AI Study Companion Pro

This module contains specialized agents for educational content processing,
including summarization, question generation, explanation, and resource recommendation.
"""

from typing import Dict, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from app.config.rag_config import RAGConfig
from app.utils.logger import logger
import json


class BaseAgent:
    """Base class for all agents with common functionality"""

    def __init__(self, temperature: Optional[float] = None):
        """Initialize base agent with LLM"""
        self.llm = RAGConfig.get_llm(temperature=temperature)
        self.logger = logger

    def _parse_json_response(self, response: str) -> Any:
        """
        Parse JSON response from LLM
        
        Args:
            response: Raw response string from LLM
            
        Returns:
            Parsed JSON object or original string if parsing fails
        """
        try:
            # Try to extract JSON from code blocks if present
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()

            return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            return response
        except Exception as e:
            self.logger.error(f"Unexpected error parsing response: {e}")
            return response


class SummarizerAgent(BaseAgent):
    """Agent specialized in summarizing educational content"""

    def __init__(self):
        super().__init__(temperature=0.3)
        self.system_prompt = RAGConfig.SUMMARIZER_SYSTEM_PROMPT

    async def summarize(
        self,
        text: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of educational content
        
        Args:
            text: Text content to summarize
            parameters: Optional parameters for customization
        
        Returns:
            Dict with summary and metadata
        """
        try:
            max_length = parameters.get("max_length", 500) if parameters else 500

            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", f"Summarize the following content in approximately {max_length} words:\n\n{text}")
            ])

            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = await chain.arun(text=text)

            return {
                "summary": result.strip(),
                "original_length": len(text),
                "summary_length": len(result),
                "compression_ratio": round(len(result) / len(text), 2)
            }
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            raise


class QuestionGeneratorAgent(BaseAgent):
    """Agent specialized in generating quiz questions"""

    def __init__(self):
        super().__init__(temperature=0.5)
        self.system_prompt = RAGConfig.QUESTION_GENERATOR_SYSTEM_PROMPT

    async def generate_questions(
        self,
        text: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate quiz questions from educational content
        
        Args:
            text: Text content to generate questions from
            parameters: Optional parameters (e.g., num_questions)
        
        Returns:
            Dict with questions list and metadata
        """
        try:
            num_questions = parameters.get("num_questions", 5) if parameters else 5

            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", f"Generate {num_questions} multiple choice questions from the following content:\n\n{text}")
            ])

            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = await chain.arun(text=text)

            # Try to parse JSON response
            questions = self._parse_json_response(result)

            # If parsing failed, return raw response
            if isinstance(questions, str):
                questions = [{"raw_response": result}]

            return {
                "questions": questions,
                "num_generated": len(questions) if isinstance(questions, list) else 1,
                "source_length": len(text)
            }
        except Exception as e:
            self.logger.error(f"Question generation failed: {e}")
            raise


class ExplainerAgent(BaseAgent):
    """Agent specialized in explaining concepts with context awareness"""

    def __init__(self):
        super().__init__(temperature=0.4)
        self.system_prompt = RAGConfig.EXPLAINER_SYSTEM_PROMPT

    async def explain(
        self,
        question: str,
        context: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Provide context-aware explanation for a question
        
        Args:
            question: Question or concept to explain
            context: Optional retrieved context from RAG
            parameters: Optional parameters for customization
        
        Returns:
            Dict with explanation and metadata
        """
        try:
            if context:
                human_message = f"""Question: {question}

Relevant Context:
{context}

Please provide a comprehensive explanation using the above context."""
            else:
                human_message = f"Please explain: {question}"

            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", human_message)
            ])

            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = await chain.arun(question=question, context=context or "")

            return {
                "explanation": result.strip(),
                "question": question,
                "used_context": bool(context),
                "context_length": len(context) if context else 0
            }
        except Exception as e:
            self.logger.error(f"Explanation failed: {e}")
            raise


class ResourceRecommenderAgent(BaseAgent):
    """Agent specialized in recommending educational resources"""

    def __init__(self):
        super().__init__(temperature=0.6)
        self.system_prompt = RAGConfig.RESOURCE_RECOMMENDER_SYSTEM_PROMPT

    async def recommend(
        self,
        topic: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend educational resources for a topic
        
        Args:
            topic: Topic or content to find resources for
            parameters: Optional parameters (e.g., num_resources, resource_types)
        
        Returns:
            Dict with resource recommendations and metadata
        """
        try:
            num_resources = parameters.get("num_resources", 5) if parameters else 5
            resource_types = parameters.get("resource_types", "all") if parameters else "all"

            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", f"Recommend {num_resources} educational resources for the following topic:\n\n{topic}\n\nResource types: {resource_types}")
            ])

            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = await chain.arun(topic=topic)

            # Try to parse JSON response
            resources = self._parse_json_response(result)

            # If parsing failed, return raw response
            if isinstance(resources, str):
                resources = [{"raw_response": result}]

            return {
                "resources": resources,
                "num_recommended": len(resources) if isinstance(resources, list) else 1,
                "topic": topic
            }
        except Exception as e:
            self.logger.error(f"Resource recommendation failed: {e}")
            raise


# Agent factory
def get_agent(agent_type: str):
    """
    Get agent instance by type
    
    Args:
        agent_type: Type of agent (summarizer, question_generator, explainer, resource_recommender)
    
    Returns:
        Agent instance
    
    Raises:
        ValueError: If agent type is unknown
    """
    agents = {
        "summarizer": SummarizerAgent,
        "question_generator": QuestionGeneratorAgent,
        "explainer": ExplainerAgent,
        "resource_recommender": ResourceRecommenderAgent
    }

    agent_class = agents.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(agents.keys())}")

    return agent_class()


# Pre-instantiated agents for convenience
summarizer_agent = SummarizerAgent()
question_generator_agent = QuestionGeneratorAgent()
explainer_agent = ExplainerAgent()
resource_recommender_agent = ResourceRecommenderAgent()
