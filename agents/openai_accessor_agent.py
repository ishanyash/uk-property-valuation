# OpenAI-Powered Accessor Agent

from typing import Dict, List, Any, Optional
import json
import logging
import time
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AccessorAgent(BaseAgent):
    """
    Accessor Agent - Reviews, validates, and approves information from other agents
    
    This agent uses OpenAI to review the outputs of the Research and Evaluation agents,
    validate information for accuracy and consistency, and make final approval decisions
    on what content should be included in the property valuation report.
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Accessor Agent.
        
        Args:
            model: OpenAI model to use (default: gpt-4)
        """
        super().__init__("Accessor Agent", model)
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the Accessor Agent.
        
        Returns:
            System prompt string
        """
        return """
        You are the Accessor Agent, an AI specialized in reviewing, validating, and approving property valuation information.
        Your task is to critically assess the outputs of the Research and Evaluation agents to ensure accuracy,
        consistency, and quality before final report generation.
        
        You should:
        1. Review all property data for accuracy and completeness
        2. Validate calculations and ensure mathematical consistency
        3. Check for logical inconsistencies or contradictions in the analysis
        4. Ensure all valuations and assessments are reasonable and justified
        5. Identify any missing critical information
        6. Make final approval decisions on what content to include in the report
        7. Provide feedback on areas that need improvement or reconsideration
        
        Be thorough, critical, and maintain high standards for data quality and analytical rigor.
        Your role is crucial in ensuring the final report is trustworthy and valuable.
        """
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate the combined outputs of the Research and Evaluation agents.
        
        Args:
            input_data: Dictionary containing the combined outputs of Research and Evaluation agents
            
        Returns:
            Dictionary of approved data for report generation
        """
        if 'address' not in input_data:
            raise ValueError("Input data must include an address")
        
        address = input_data.get('address', '')
        self.log_activity(f"Starting review for address: {address}")
        self.initialize_conversation()
        
        # Extract key sections for review
        property_data = input_data.get('property_data', {})
        evaluation_results = input_data.get('evaluation_results', {})
        
        # Review and validate each section
        validated_data = {}
        
        # Review property details
        validated_data['property_details'] = self._review_property_details(
            property_data.get('property_details', {}),
            property_data.get('address', '')
        )
        
        # Review market data
        validated_data['market_data'] = self._review_market_data(
            property_data.get('market_data', {}),
            property_data.get('local_area_info', {})
        )
        
        # Review valuation
        validated_data['current_valuation'] = self._review_valuation(
            evaluation_results.get('property_appraisal', {}).get('current_valuation', {}),
            property_data.get('property_details', {}),
            property_data.get('market_data', {})
        )
        
        # Review development scenarios
        validated_data['development_scenarios'] = self._review_development_scenarios(
            evaluation_results.get('feasibility_study', {}).get('development_scenarios', []),
            validated_data['current_valuation']
        )
        
        # Review rental analysis
        validated_data['rental_analysis'] = self._review_rental_analysis(
            evaluation_results.get('feasibility_study', {}).get('rental_analysis', {}),
            validated_data['current_valuation'],
            property_data.get('market_data', {})
        )
        
        # Review planning assessment
        validated_data['planning_analysis'] = self._review_planning_assessment(
            evaluation_results.get('planning_analysis', {}),
            property_data.get('planning_history', {})
        )
        
        # Review risk assessment
        validated_data['risk_assessment'] = self._review_risk_assessment(
            evaluation_results.get('risk_assessment', {}),
            property_data,
            evaluation_results
        )
        
        # Review executive summary
        validated_data['executive_summary'] = self._review_executive_summary(
            evaluation_results.get('executive_summary', {}),
            validated_data
        )
        
        # Review conclusion
        validated_data['conclusion'] = self._review_conclusion(
            evaluation_results.get('conclusion', {}),
            validated_data
        )
        
        # Compile final approved data
        approved_data = {
            'address': address,
            'executive_summary': validated_data['executive_summary'],
            'property_appraisal': {
                'property_details': validated_data['property_details'],
                'current_valuation': validated_data['current_valuation'],
                'comparable_analysis': evaluation_results.get('property_appraisal', {}).get('comparable_analysis', {})
            },
            'feasibility_study': {
                'development_scenarios': validated_data['development_scenarios'],
                'rental_analysis': validated_data['rental_analysis']
            },
            'planning_analysis': validated_data['planning_analysis'],
            'risk_assessment': validated_data['risk_assessment'],
            'local_market_analysis': {
                'market_data': validated_data['market_data'],
                'local_area_info': property_data.get('local_area_info', {})
            },
            'conclusion': validated_data['conclusion'],
            'approval_timestamp': time.time(),
            'approval_status': 'Approved'
        }
        
        self.log_activity(f"Completed review for address: {address}")
        return approved_data
    
    def _review_property_details(self, property_details: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Review and validate property details using OpenAI.
        
        Args:
            property_details: Property details from Research Agent
            address: Property address
            
        Returns:
            Validated property details
        """
        self.log_activity("Reviewing property details")
        
        # Prepare the input data for OpenAI
        property_json = json.dumps(property_details, indent=2)
        
        # Add user message requesting property details review
        self.add_to_conversation("user", f"""
        Review these property details for accuracy and completeness:
        
        ADDRESS: {address}
        
        PROPERTY DETAILS:
        {property_json}
        
        Please:
        1. Check for any inconsistencies or unrealistic values
        2. Identify any missing critical information
        3. Validate that the property type, size, and features are consistent
        4. Make any necessary corrections or adjustments
        
        Return the validated property details as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_details = json.loads(json_str)
                return validated_details
            else:
                # If no JSON found, return the original details
                return property_details
        except Exception as e:
            logger.error(f"Error reviewing property details: {str(e)}")
            # Return the original details if review fails
            return property_details
    
    def _review_market_data(self, market_data: Dict[str, Any], local_area_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate market data using OpenAI.
        
        Args:
            market_data: Market data from Research Agent
            local_area_info: Local area information from Research Agent
            
        Returns:
            Validated market data
        """
        self.log_activity("Reviewing market data")
        
        # Prepare the input data for OpenAI
        market_json = json.dumps(market_data, indent=2)
        local_json = json.dumps(local_area_info, indent=2)
        
        # Add user message requesting market data review
        self.add_to_conversation("user", f"""
        Review this market data and local area information for accuracy and consistency:
        
        MARKET DATA:
        {market_json}
        
        LOCAL AREA INFORMATION:
        {local_json}
        
        Please:
        1. Check for any inconsistencies or unrealistic values
        2. Validate that the price trends and yields are reasonable
        3. Ensure the market sentiment aligns with the price trends
        4. Make any necessary corrections or adjustments
        
        Return the validated market data as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_market_data = json.loads(json_str)
                return validated_market_data
            else:
                # If no JSON found, return the original market data
                return market_data
        except Exception as e:
            logger.error(f"Error reviewing market data: {str(e)}")
            # Return the original market data if review fails
            return market_data
    
    def _review_valuation(self, valuation: Dict[str, Any], property_details: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate property valuation using OpenAI.
        
        Args:
            valuation: Valuation from Evaluation Agent
            property_details: Property details from Research Agent
            market_data: Market data from Research Agent
            
        Returns:
            Validated valuation
        """
        self.log_activity("Reviewing property valuation")
        
        # Prepare the input data for OpenAI
        valuation_json = json.dumps(valuation, indent=2)
        property_json = json.dumps(property_details, indent=2)
        market_json = json.dumps(market_data, indent=2)
        
        # Add user message requesting valuation review
        self.add_to_conversation("user", f"""
        Review this property valuation for accuracy and reasonableness:
        
        VALUATION:
        {valuation_json}
        
        PROPERTY DETAILS:
        {property_json}
        
        MARKET DATA:
        {market_json}
        
        Please:
        1. Check if the valuation is reasonable given the property details and market data
        2. Validate the price per square foot calculation
        3. Ensure the confidence level is appropriate
        4. Make any necessary corrections or adjustments
        
        Return the validated valuation as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_valuation = json.loads(json_str)
                return validated_valuation
            else:
                # If no JSON found, return the original valuation
                return valuation
        except Exception as e:
            logger.error(f"Error reviewing valuation: {str(e)}")
            # Return the original valuation if review fails
            return valuation
    
    def _review_development_scenarios(self, scenarios: List[Dict[str, Any]], valuation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Review and validate development scenarios using OpenAI.
        
        Args:
            scenarios: Development scenarios from Evaluation Agent
            valuation: Validated property valuation
            
        Returns:
            Validated development scenarios
        """
        self.log_activity("Reviewing development scenarios")
        
        # Prepare the input data for OpenAI
        scenarios_json = json.dumps(scenarios, indent=2)
        valuation_json = json.dumps(valuation, indent=2)
        
        # Add user message requesting development scenarios review
        self.add_to_conversation("user", f"""
        Review these development scenarios for accuracy and feasibility:
        
        DEVELOPMENT SCENARIOS:
        {scenarios_json}
        
        CURRENT VALUATION:
        {valuation_json}
        
        Please:
        1. Check if the costs are reasonable for each scenario
        2. Validate the value uplift calculations
        3. Ensure the ROI calculations are correct
        4. Make any necessary corrections or adjustments
        
        Return the validated development scenarios as a JSON array.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '[' in assistant_message and ']' in assistant_message:
                json_str = assistant_message[assistant_message.find('['):assistant_message.rfind(']')+1]
                validated_scenarios = json.loads(json_str)
                return validated_scenarios
            else:
                # If no JSON found, return the original scenarios
                return scenarios
        except Exception as e:
            logger.error(f"Error reviewing development scenarios: {str(e)}")
            # Return the original scenarios if review fails
            return scenarios
    
    def _review_rental_analysis(self, rental_analysis: Dict[str, Any], valuation: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate rental analysis using OpenAI.
        
        Args:
            rental_analysis: Rental analysis from Evaluation Agent
            valuation: Validated property valuation
            market_data: Market data from Research Agent
            
        Returns:
            Validated rental analysis
        """
        self.log_activity("Reviewing rental analysis")
        
        # Prepare the input data for OpenAI
        rental_json = json.dumps(rental_analysis, indent=2)
        valuation_json = json.dumps(valuation, indent=2)
        market_json = json.dumps(market_data, indent=2)
        
        # Add user message requesting rental analysis review
        self.add_to_conversation("user", f"""
        Review this rental analysis for accuracy and reasonableness:
        
        RENTAL ANALYSIS:
        {rental_json}
        
        CURRENT VALUATION:
        {valuation_json}
        
        MARKET DATA:
        {market_json}
        
        Please:
        1. Check if the rental income is reasonable given the property valuation
        2. Validate the gross yield calculation
        3. Ensure the rental growth rate is consistent with market data
        4. Verify the rental forecast calculations
        5. Make any necessary corrections or adjustments
        
        Return the validated rental analysis as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_rental = json.loads(json_str)
                return validated_rental
            else:
                # If no JSON found, return the original rental analysis
                return rental_analysis
        except Exception as e:
            logger.error(f"Error reviewing rental analysis: {str(e)}")
            # Return the original rental analysis if review fails
            return rental_analysis
    
    def _review_planning_assessment(self, planning_assessment: Dict[str, Any], planning_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate planning assessment using OpenAI.
        
        Args:
            planning_assessment: Planning assessment from Evaluation Agent
            planning_history: Planning history from Research Agent
            
        Returns:
            Validated planning assessment
        """
        self.log_activity("Reviewing planning assessment")
        
        # Prepare the input data for OpenAI
        planning_json = json.dumps(planning_assessment, indent=2)
        history_json = json.dumps(planning_history, indent=2)
        
        # Add user message requesting planning assessment review
        self.add_to_conversation("user", f"""
        Review this planning assessment for accuracy and completeness:
        
        PLANNING ASSESSMENT:
        {planning_json}
        
        PLANNING HISTORY:
        {history_json}
        
        Please:
        1. Check if the current use class is correct
        2. Validate that the opportunities are realistic
        3. Ensure the constraints are comprehensive
        4. Make any necessary corrections or adjustments
        
        Return the validated planning assessment as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_planning = json.loads(json_str)
                return validated_planning
            else:
                # If no JSON found, return the original planning assessment
                return planning_assessment
        except Exception as e:
            logger.error(f"Error reviewing planning assessment: {str(e)}")
            # Return the original planning assessment if review fails
            return planning_assessment
    
    def _review_risk_assessment(self, risk_assessment: Dict[str, Any], property_data: Dict[str, Any], evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate risk assessment using OpenAI.
        
        Args:
            risk_assessment: Risk assessment from Evaluation Agent
            property_data: Complete property data from Research Agent
            evaluation_results: Complete evaluation results from Evaluation Agent
            
        Returns:
            Validated risk assessment
        """
        self.log_activity("Reviewing risk assessment")
        
        # Prepare the input data for OpenAI
        risk_json = json.dumps(risk_assessment, indent=2)
        
        # Add user message requesting risk assessment review
        self.add_to_conversation("user", f"""
        Review this risk assessment for accuracy and comprehensiveness:
        
        RISK ASSESSMENT:
        {risk_json}
        
        Please:
        1. Check if the overall risk profile is appropriate
        2. Validate that all major risk categories are covered
        3. Ensure the impact ratings are reasonable
        4. Verify that mitigation strategies are practical
        5. Make any necessary corrections or adjustments
        
        Return the validated risk assessment as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_risk = json.loads(json_str)
                return validated_risk
            else:
                # If no JSON found, return the original risk assessment
                return risk_assessment
        except Exception as e:
            logger.error(f"Error reviewing risk assessment: {str(e)}")
            # Return the original risk assessment if review fails
            return risk_assessment
    
    def _review_executive_summary(self, executive_summary: Dict[str, Any], validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate executive summary using OpenAI.
        
        Args:
            executive_summary: Executive summary from Evaluation Agent
            validated_data: All previously validated data
            
        Returns:
            Validated executive summary
        """
        self.log_activity("Reviewing executive summary")
        
        # Prepare the input data for OpenAI
        summary_json = json.dumps(executive_summary, indent=2)
        valuation_json = json.dumps(validated_data.get('current_valuation', {}), indent=2)
        scenarios_json = json.dumps(validated_data.get('development_scenarios', []), indent=2)
        rental_json = json.dumps(validated_data.get('rental_analysis', {}), indent=2)
        
        # Add user message requesting executive summary review
        self.add_to_conversation("user", f"""
        Review this executive summary for accuracy and consistency with the validated data:
        
        EXECUTIVE SUMMARY:
        {summary_json}
        
        VALIDATED VALUATION:
        {valuation_json}
        
        VALIDATED DEVELOPMENT SCENARIOS:
        {scenarios_json}
        
        VALIDATED RENTAL ANALYSIS:
        {rental_json}
        
        Please:
        1. Check if the summary accurately reflects the validated data
        2. Ensure the investment strategy is appropriate
        3. Validate that the strategy rationale is sound
        4. Make any necessary corrections or adjustments
        
        Return the validated executive summary as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_summary = json.loads(json_str)
                return validated_summary
            else:
                # If no JSON found, return the original executive summary
                return executive_summary
        except Exception as e:
            logger.error(f"Error reviewing executive summary: {str(e)}")
            # Return the original executive summary if review fails
            return executive_summary
    
    def _review_conclusion(self, conclusion: Dict[str, Any], validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review and validate conclusion using OpenAI.
        
        Args:
            conclusion: Conclusion from Evaluation Agent
            validated_data: All previously validated data
            
        Returns:
            Validated conclusion
        """
        self.log_activity("Reviewing conclusion")
        
        # Prepare the input data for OpenAI
        conclusion_json = json.dumps(conclusion, indent=2)
        valuation_json = json.dumps(validated_data.get('current_valuation', {}), indent=2)
        rental_json = json.dumps(validated_data.get('rental_analysis', {}), indent=2)
        
        # Add user message requesting conclusion review
        self.add_to_conversation("user", f"""
        Review this conclusion for accuracy and consistency with the validated data:
        
        CONCLUSION:
        {conclusion_json}
        
        VALIDATED VALUATION:
        {valuation_json}
        
        VALIDATED RENTAL ANALYSIS:
        {rental_json}
        
        Please:
        1. Check if the BTR potential rating is appropriate
        2. Ensure the summary statement is accurate
        3. Validate that the recommendation is sound
        4. Make any necessary corrections or adjustments
        
        Return the validated conclusion as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                validated_conclusion = json.loads(json_str)
                return validated_conclusion
            else:
                # If no JSON found, return the original conclusion
                return conclusion
        except Exception as e:
            logger.error(f"Error reviewing conclusion: {str(e)}")
            # Return the original conclusion if review fails
            return conclusion
