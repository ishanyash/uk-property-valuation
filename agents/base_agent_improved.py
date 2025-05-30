import os
import sys
import logging
import time
import json
import random
from typing import Dict, List, Any, Optional, Callable
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base Agent class for all agents in the system.
    Provides common functionality for OpenAI API calls, conversation management, and error handling.
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
        self.conversation_history = []
        self.client = None
        self._initialize_openai_client()
        
    def _initialize_openai_client(self):
        """Initialize the OpenAI client with API key from environment variables."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning(f"[{self.agent_name}] OpenAI API key not found in environment variables")
        
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error initializing OpenAI client: {str(e)}")
            raise
    
    def log_activity(self, message: str):
        """Log agent activity."""
        logger.info(f"[{self.agent_name}] {message}")
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the agent.
        
        Returns:
            System prompt string
        """
        return f"You are {self.agent_name}, an AI assistant."
    
    def initialize_conversation(self):
        """Initialize or reset the conversation history."""
        self.conversation_history = [
            {"role": "system", "content": self.get_system_prompt()}
        ]
    
    def add_to_conversation(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (system, user, assistant)
            content: Message content
        """
        self.conversation_history.append({"role": role, "content": content})
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_history
    
    def call_openai_api(self, 
                       messages: List[Dict[str, str]], 
                       temperature: float = 0.7, 
                       max_tokens: int = 2000,
                       max_retries: int = 5,
                       initial_retry_delay: float = 1.0,
                       max_retry_delay: float = 60.0,
                       jitter: float = 0.1) -> Dict[str, Any]:
        """
        Call the OpenAI API with robust error handling and exponential backoff.
        
        Args:
            messages: List of conversation messages
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts
            initial_retry_delay: Initial delay between retries in seconds
            max_retry_delay: Maximum delay between retries in seconds
            jitter: Random jitter factor to add to delay
            
        Returns:
            OpenAI API response
        
        Raises:
            Exception: If API call fails after all retries
        """
        if not self.client:
            self._initialize_openai_client()
            
        if not self.client:
            raise ValueError(f"[{self.agent_name}] OpenAI client not initialized")
        
        retry_count = 0
        retry_delay = initial_retry_delay
        
        while retry_count <= max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Convert to dict for consistent handling
                response_dict = {
                    "choices": [
                        {
                            "message": {
                                "content": response.choices[0].message.content,
                                "role": response.choices[0].message.role
                            },
                            "index": response.choices[0].index,
                            "finish_reason": response.choices[0].finish_reason
                        }
                    ],
                    "created": response.created,
                    "model": response.model,
                    "object": response.object,
                    "usage": {
                        "completion_tokens": response.usage.completion_tokens,
                        "prompt_tokens": response.usage.prompt_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
                
                return response_dict
                
            except openai.RateLimitError as e:
                retry_count += 1
                
                if retry_count > max_retries:
                    error_msg = f"Failed to call OpenAI API after {max_retries} attempts due to rate limits"
                    logger.error(f"[{self.agent_name}] {error_msg}")
                    raise Exception(error_msg)
                
                # Add jitter to avoid thundering herd
                jitter_amount = random.uniform(-jitter, jitter) * retry_delay
                actual_delay = min(retry_delay + jitter_amount, max_retry_delay)
                actual_delay = max(actual_delay, 0.1)  # Ensure positive delay
                
                logger.warning(f"[{self.agent_name}] Rate limit reached. Waiting {actual_delay:.1f} seconds before retry {retry_count}/{max_retries}.")
                time.sleep(actual_delay)
                
                # Exponential backoff
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except openai.APIError as e:
                retry_count += 1
                
                if retry_count > max_retries:
                    error_msg = f"Failed to call OpenAI API after {max_retries} attempts: {str(e)}"
                    logger.error(f"[{self.agent_name}] {error_msg}")
                    raise Exception(error_msg)
                
                # Add jitter to avoid thundering herd
                jitter_amount = random.uniform(-jitter, jitter) * retry_delay
                actual_delay = min(retry_delay + jitter_amount, max_retry_delay)
                actual_delay = max(actual_delay, 0.1)  # Ensure positive delay
                
                logger.warning(f"[{self.agent_name}] API error: {str(e)}. Waiting {actual_delay:.1f} seconds before retry {retry_count}/{max_retries}.")
                time.sleep(actual_delay)
                
                # Exponential backoff
                retry_delay = min(retry_delay * 2, max_retry_delay)
                
            except Exception as e:
                error_msg = f"Unexpected error calling OpenAI API: {str(e)}"
                logger.error(f"[{self.agent_name}] {error_msg}")
                raise Exception(error_msg)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        To be implemented by subclasses.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Results dictionary
        """
        raise NotImplementedError("Subclasses must implement process method")


class AgentOrchestrator:
    """
    Orchestrates multiple agents and manages their workflow.
    """
    
    def __init__(self):
        """Initialize the agent orchestrator."""
        self.agents = {}
    
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance
        """
        self.agents[agent_id] = agent
        logger.info(f"Agent {agent_id} registered")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def execute_workflow(self, workflow: List[Dict[str, Any]], initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow of agent steps.
        
        Args:
            workflow: List of workflow steps with agent_id and optional parameters
            initial_data: Initial data to pass to the first agent
            
        Returns:
            Final results from the workflow
        """
        current_data = initial_data
        results = {
            'workflow_steps': [],
            'final_result': None,
            'status': 'in_progress'
        }
        
        try:
            for step in workflow:
                agent_id = step.get('agent_id')
                if not agent_id or agent_id not in self.agents:
                    raise ValueError(f"Invalid agent ID: {agent_id}")
                
                agent = self.agents[agent_id]
                step_params = step.get('parameters', {})
                
                # Merge step parameters with current data
                input_data = {**current_data, **step_params}
                
                # Process with the agent
                step_result = agent.process(input_data)
                
                # Store step results
                step_info = {
                    'agent_id': agent_id,
                    'input_size': len(str(input_data)),
                    'output_size': len(str(step_result)),
                    'status': 'success'
                }
                results['workflow_steps'].append(step_info)
                
                # Update current data for next step
                current_data = step_result
            
            # Set final result and status
            results['final_result'] = current_data
            results['status'] = 'complete'
            
        except Exception as e:
            logger.error(f"Error in workflow execution: {str(e)}")
            results['status'] = 'error'
            results['error'] = str(e)
            
            # Add error info to the last step if it exists
            if results['workflow_steps']:
                results['workflow_steps'][-1]['status'] = 'error'
                results['workflow_steps'][-1]['error'] = str(e)
        
        return results
