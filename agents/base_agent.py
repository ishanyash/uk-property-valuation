# Base Agent Architecture for OpenAI Integration

from abc import ABC, abstractmethod
import os
import time
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class BaseAgent(ABC):
    """
    Base agent class for OpenAI API integration.
    Provides common functionality for all agent types.
    """
    
    def __init__(self, agent_name: str, model: str = "gpt-4"):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name of the agent
            model: OpenAI model to use (default: gpt-4)
        """
        self.agent_name = agent_name
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.conversation_history = []
        
        # Check if API key is available
        if not self.api_key:
            logger.warning(f"OpenAI API key not found for {agent_name}. Please add it to your .env file.")
    
    def call_openai_api(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7, 
                       max_tokens: int = 1000,
                       functions: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Call the OpenAI API with retry logic.
        
        Args:
            messages: List of message dictionaries for the conversation
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens in the response
            functions: Optional function definitions for function calling
            
        Returns:
            API response as a dictionary
        """
        if not self.api_key:
            raise ValueError(f"OpenAI API key not found for {self.agent_name}. Please add it to your .env file.")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if functions:
            payload["functions"] = functions
            payload["function_call"] = "auto"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit error, wait and retry
                    wait_time = (2 ** attempt) * self.retry_delay
                    logger.warning(f"Rate limit reached. Waiting {wait_time} seconds before retry.")
                    time.sleep(wait_time)
                else:
                    response.raise_for_status()
            except Exception as e:
                logger.error(f"Error calling OpenAI API: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * self.retry_delay
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise Exception(f"Failed to call OpenAI API after {self.max_retries} attempts")
    
    def add_to_conversation(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (system, user, assistant)
            content: Content of the message
        """
        self.conversation_history.append({"role": role, "content": content})
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by subclasses.
        
        Returns:
            System prompt string
        """
        return f"You are {self.agent_name}, an AI assistant specialized in property valuation."
    
    def initialize_conversation(self) -> None:
        """Initialize the conversation with the system prompt."""
        self.clear_conversation_history()
        self.add_to_conversation("system", self.get_system_prompt())
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        Must be implemented by subclasses.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            Processed results
        """
        pass
    
    def log_activity(self, activity: str) -> None:
        """
        Log agent activity.
        
        Args:
            activity: Activity description
        """
        logger.info(f"[{self.agent_name}] {activity}")


class AgentCommunicationBus:
    """
    Communication bus for inter-agent messaging.
    Allows agents to send and receive messages.
    """
    
    def __init__(self):
        """Initialize the communication bus."""
        self.message_queue = {}
    
    def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]) -> None:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Name of the sending agent
            to_agent: Name of the receiving agent
            message: Message content
        """
        if to_agent not in self.message_queue:
            self.message_queue[to_agent] = []
        
        self.message_queue[to_agent].append({
            "from": from_agent,
            "content": message,
            "timestamp": time.time()
        })
        
        logger.info(f"Message sent from {from_agent} to {to_agent}")
    
    def get_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Get all messages for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of messages
        """
        messages = self.message_queue.get(agent_name, [])
        self.message_queue[agent_name] = []  # Clear the queue
        return messages
    
    def has_messages(self, agent_name: str) -> bool:
        """
        Check if an agent has messages.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if the agent has messages, False otherwise
        """
        return agent_name in self.message_queue and len(self.message_queue[agent_name]) > 0


class AgentOrchestrator:
    """
    Orchestrator for managing agent workflow.
    Coordinates the execution of multiple agents.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents = {}
        self.communication_bus = AgentCommunicationBus()
    
    def register_agent(self, agent_name: str, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_name: Name of the agent
            agent: Agent instance
        """
        self.agents[agent_name] = agent
        logger.info(f"Agent {agent_name} registered")
    
    def execute_workflow(self, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent workflow.
        
        Args:
            initial_data: Initial data for the workflow
            
        Returns:
            Final workflow results
        """
        # Implementation will depend on the specific workflow
        # This is a placeholder for the actual implementation
        pass
