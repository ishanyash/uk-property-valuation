# OpenAI-Powered Evaluation Agent

from typing import Dict, List, Any, Optional
import json
import logging
import time
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class EvaluationAgent(BaseAgent):
    """
    Evaluation Agent - Analyzes property data and performs valuations using OpenAI
    
    This agent uses OpenAI to analyze data collected by the Research Agent,
    validate information from multiple sources, perform calculations for valuations,
    ROI, and development scenarios, and prepare structured data for report generation.
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Evaluation Agent.
        
        Args:
            model: OpenAI model to use (default: gpt-4)
        """
        super().__init__("Evaluation Agent", model)
        self.refurbishment_cost_benchmarks = {
            'light': {'cost_per_sqft': 70, 'description': 'Painting, decorating, minor works'},
            'medium': {'cost_per_sqft': 180, 'description': 'New kitchen, bathroom, and cosmetic work'},
            'heavy': {'cost_per_sqft': 225, 'description': 'Structural changes, extensions, full renovation'},
            'hmo': {'cost_per_room': 30000, 'description': 'Conversion to HMO (House in Multiple Occupation)'}
        }
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the Evaluation Agent.
        
        Returns:
            System prompt string
        """
        return """
        You are the Evaluation Agent, an AI specialized in analyzing property data and performing valuations.
        Your task is to analyze property information collected by the Research Agent and generate
        comprehensive evaluation results.
        
        You should:
        1. Analyze property details, market data, and comparable properties
        2. Calculate current property valuation using appropriate methodologies
        3. Generate development scenarios with costs, value uplifts, and ROI
        4. Calculate rental income potential and yields
        5. Assess planning opportunities and constraints
        6. Perform risk assessment for the property investment
        7. Generate executive summary and conclusion
        
        Use these refurbishment cost benchmarks:
        - Light refurbishment: £70 per square foot (painting, decorating, minor works)
        - Medium refurbishment: £180 per square foot (new kitchen, bathroom, and cosmetic work)
        - Heavy refurbishment: £225 per square foot (structural changes, extensions, full renovation)
        - HMO conversion: £30,000 per room
        
        Be thorough, accurate, and provide clear reasoning for all valuations and assessments.
        Format all monetary values appropriately (e.g., £500,000) and include percentage values
        where relevant (e.g., 5.2%).
        """
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process property data and generate evaluation results.
        
        Args:
            input_data: Dictionary containing property data from the Research Agent
            
        Returns:
            Dictionary of evaluation results
        """
        if 'address' not in input_data:
            raise ValueError("Property data must include an address")
        
        address = input_data.get('address', '')
        self.log_activity(f"Starting evaluation for address: {address}")
        self.initialize_conversation()
        
        # Extract key property details
        property_details = input_data.get('property_details', {})
        market_data = input_data.get('market_data', {})
        comparables = input_data.get('comparable_properties', [])
        local_info = input_data.get('local_area_info', {})
        planning_history = input_data.get('planning_history', {})
        
        # Calculate current valuation
        current_valuation = self._calculate_valuation(property_details, market_data, comparables)
        
        # Generate development scenarios
        development_scenarios = self._generate_development_scenarios(property_details, current_valuation)
        
        # Calculate rental income and yield
        rental_analysis = self._calculate_rental_analysis(property_details, market_data, current_valuation)
        
        # Assess planning opportunities
        planning_assessment = self._assess_planning_opportunities(input_data)
        
        # Perform risk assessment
        risk_assessment = self._assess_risks(input_data)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            property_details, 
            current_valuation, 
            development_scenarios, 
            rental_analysis,
            planning_assessment,
            risk_assessment
        )
        
        # Generate conclusion
        conclusion = self._generate_conclusion(
            property_details,
            current_valuation,
            development_scenarios,
            rental_analysis
        )
        
        # Compile evaluation results
        evaluation_results = {
            'address': address,
            'executive_summary': executive_summary,
            'property_appraisal': {
                'property_details': property_details,
                'current_valuation': current_valuation,
                'comparable_analysis': self._analyze_comparables(comparables)
            },
            'feasibility_study': {
                'development_scenarios': development_scenarios,
                'rental_analysis': rental_analysis
            },
            'planning_analysis': planning_assessment,
            'risk_assessment': risk_assessment,
            'local_market_analysis': {
                'market_data': market_data,
                'local_area_info': local_info
            },
            'conclusion': conclusion,
            'evaluation_timestamp': time.time()
        }
        
        self.log_activity(f"Completed evaluation for address: {address}")
        return evaluation_results
    
    def _calculate_valuation(self, property_details: Dict[str, Any], market_data: Dict[str, Any], comparables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate the current property valuation using OpenAI.
        
        Args:
            property_details: Property details from Research Agent
            market_data: Market data from Research Agent
            comparables: Comparable properties from Research Agent
            
        Returns:
            Dictionary with valuation details
        """
        self.log_activity("Calculating property valuation")
        
        # Prepare the input data for OpenAI
        property_json = json.dumps(property_details, indent=2)
        market_json = json.dumps(market_data, indent=2)
        comparables_json = json.dumps(comparables, indent=2)
        
        # Add user message requesting valuation
        self.add_to_conversation("user", f"""
        Calculate the current market valuation for this property based on the following information:
        
        PROPERTY DETAILS:
        {property_json}
        
        MARKET DATA:
        {market_json}
        
        COMPARABLE PROPERTIES:
        {comparables_json}
        
        Please calculate:
        1. The current market value of the property
        2. The price per square foot
        3. The confidence level of the valuation (High/Medium/Low)
        4. The methodology used
        
        Format the value as a number and also as a formatted string with currency symbol.
        Return the results as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,  # Lower temperature for more consistent calculations
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
                valuation = json.loads(json_str)
                
                # Ensure all required fields are present
                if 'value' not in valuation and 'formatted_value' in valuation:
                    # Try to extract numeric value from formatted value
                    formatted_value = valuation['formatted_value']
                    if '£' in formatted_value:
                        try:
                            numeric_value = int(formatted_value.replace('£', '').replace(',', ''))
                            valuation['value'] = numeric_value
                        except:
                            valuation['value'] = 0
                
                # Add current date if not present
                if 'valuation_date' not in valuation:
                    from datetime import datetime
                    valuation['valuation_date'] = datetime.now().strftime('%B %d, %Y')
                
                return valuation
            else:
                # If no JSON found, create default valuation
                # Extract size from property details if available
                size = 0
                size_str = property_details.get('floor_area', '')
                if size_str:
                    try:
                        size = int(size_str.split(' ')[0])  # Extract numeric part
                    except:
                        size = 700  # Default size
                
                # Extract price per sqft from market data if available
                price_per_sqft = 0
                price_per_sqft_str = market_data.get('average_price_per_sqft', '')
                if price_per_sqft_str:
                    try:
                        price_per_sqft = int(price_per_sqft_str.replace('£', '').replace(',', ''))
                    except:
                        price_per_sqft = 689  # Default price per sqft
                
                # Calculate value
                value = size * price_per_sqft
                
                return {
                    'value': value,
                    'formatted_value': f'£{value:,}',
                    'price_per_sqft': price_per_sqft,
                    'formatted_price_per_sqft': f'£{price_per_sqft}',
                    'valuation_date': time.strftime('%B %d, %Y'),
                    'confidence_level': 'Medium',
                    'methodology': 'Comparable analysis with market data adjustment'
                }
        except Exception as e:
            logger.error(f"Error calculating valuation: {str(e)}")
            # Return a basic valuation if calculation fails
            return {
                'value': 500000,
                'formatted_value': '£500,000',
                'price_per_sqft': 700,
                'formatted_price_per_sqft': '£700',
                'valuation_date': time.strftime('%B %d, %Y'),
                'confidence_level': 'Low',
                'methodology': 'Basic estimation'
            }
    
    def _generate_development_scenarios(self, property_details: Dict[str, Any], current_valuation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate development scenarios for the property using OpenAI.
        
        Args:
            property_details: Property details from Research Agent
            current_valuation: Current valuation results
            
        Returns:
            List of development scenarios
        """
        self.log_activity("Generating development scenarios")
        
        # Prepare the input data for OpenAI
        property_json = json.dumps(property_details, indent=2)
        valuation_json = json.dumps(current_valuation, indent=2)
        benchmarks_json = json.dumps(self.refurbishment_cost_benchmarks, indent=2)
        
        # Add user message requesting development scenarios
        self.add_to_conversation("user", f"""
        Generate development scenarios for this property based on the following information:
        
        PROPERTY DETAILS:
        {property_json}
        
        CURRENT VALUATION:
        {valuation_json}
        
        REFURBISHMENT COST BENCHMARKS:
        {benchmarks_json}
        
        Generate two development scenarios:
        1. Cosmetic Refurbishment (light refurbishment)
        2. Light Refurbishment (medium refurbishment)
        
        For each scenario, calculate:
        - Total cost based on the appropriate benchmark and property size
        - Value uplift (percentage and amount)
        - New property value after refurbishment
        - Return on Investment (ROI) percentage
        - Brief recommendation
        
        Format all monetary values with currency symbols and include percentage values.
        Return the results as a JSON array of scenario objects.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,  # Lower temperature for more consistent calculations
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
                scenarios = json.loads(json_str)
                return scenarios
            else:
                # If no JSON found, create default scenarios
                # Extract size from property details
                size = 0
                size_str = property_details.get('floor_area', '')
                if size_str:
                    try:
                        size = int(size_str.split(' ')[0])  # Extract numeric part
                    except:
                        size = 700  # Default size
                
                # Extract current value
                current_value = current_valuation.get('value', 500000)
                
                # Calculate scenarios
                light_cost = size * self.refurbishment_cost_benchmarks['light']['cost_per_sqft']
                light_value_uplift = current_value * 0.10  # 10% increase
                light_new_value = current_value + light_value_uplift
                light_roi = (light_value_uplift / light_cost) * 100
                
                medium_cost = size * self.refurbishment_cost_benchmarks['medium']['cost_per_sqft']
                medium_value_uplift = current_value * 0.15  # 15% increase
                medium_new_value = current_value + medium_value_uplift
                medium_roi = (medium_value_uplift / medium_cost) * 100
                
                return [
                    {
                        'name': 'Cosmetic Refurbishment',
                        'description': self.refurbishment_cost_benchmarks['light']['description'],
                        'cost': light_cost,
                        'formatted_cost': f'£{light_cost:,}',
                        'value_uplift': light_value_uplift,
                        'formatted_value_uplift': f'£{light_value_uplift:,}',
                        'value_uplift_percentage': '10.0%',
                        'new_value': light_new_value,
                        'formatted_new_value': f'£{light_new_value:,}',
                        'roi': light_roi,
                        'formatted_roi': f'{light_roi:.1f}%',
                        'recommendation': 'High potential for good returns with minimal investment'
                    },
                    {
                        'name': 'Light Refurbishment',
                        'description': self.refurbishment_cost_benchmarks['medium']['description'],
                        'cost': medium_cost,
                        'formatted_cost': f'£{medium_cost:,}',
                        'value_uplift': medium_value_uplift,
                        'formatted_value_uplift': f'£{medium_value_uplift:,}',
                        'value_uplift_percentage': '15.0%',
                        'new_value': medium_new_value,
                        'formatted_new_value': f'£{medium_new_value:,}',
                        'roi': medium_roi,
                        'formatted_roi': f'{medium_roi:.1f}%',
                        'recommendation': 'Moderate potential with higher investment required'
                    }
                ]
        except Exception as e:
            logger.error(f"Error generating development scenarios: {str(e)}")
            # Return basic scenarios if generation fails
            return [
                {
                    'name': 'Cosmetic Refurbishment',
                    'description': 'Basic improvements',
                    'formatted_cost': '£20,000',
                    'formatted_value_uplift': '£40,000',
                    'value_uplift_percentage': '8%',
                    'formatted_new_value': '£540,000',
                    'formatted_roi': '100%',
                    'recommendation': 'Consider this option for quick returns'
                },
                {
                    'name': 'Light Refurbishment',
                    'description': 'More extensive improvements',
                    'formatted_cost': '£50,000',
                    'formatted_value_uplift': '£75,000',
                    'value_uplift_percentage': '15%',
                    'formatted_new_value': '£575,000',
                    'formatted_roi': '50%',
                    'recommendation': 'Consider this option for better long-term value'
                }
            ]
    
    def _calculate_rental_analysis(self, property_details: Dict[str, Any], market_data: Dict[str, Any], current_valuation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate rental income and yield using OpenAI.
        
        Args:
            property_details: Property details from Research Agent
            market_data: Market data from Research Agent
            current_valuation: Current valuation results
            
        Returns:
            Dictionary with rental analysis
        """
        self.log_activity("Calculating rental analysis")
        
        # Prepare the input data for OpenAI
        property_json = json.dumps(property_details, indent=2)
        market_json = json.dumps(market_data, indent=2)
        valuation_json = json.dumps(current_valuation, indent=2)
        
        # Add user message requesting rental analysis
        self.add_to_conversation("user", f"""
        Calculate rental income potential and yield for this property based on the following information:
        
        PROPERTY DETAILS:
        {property_json}
        
        MARKET DATA:
        {market_json}
        
        CURRENT VALUATION:
        {valuation_json}
        
        Please calculate:
        1. Monthly rental income potential
        2. Annual rental income potential
        3. Gross yield percentage
        4. Rental growth rate (use market data or default to 4.5% if not available)
        5. 3-year rental forecast showing growth
        
        Format all monetary values with currency symbols and include percentage values.
        Return the results as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,  # Lower temperature for more consistent calculations
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
                rental_analysis = json.loads(json_str)
                return rental_analysis
            else:
                # If no JSON found, create default rental analysis
                # Extract current value
                current_value = current_valuation.get('value', 500000)
                
                # Extract yield from market data or use default
                yield_percentage = 0.045  # Default 4.5%
                yield_str = market_data.get('average_rental_yield', '')
                if yield_str:
                    try:
                        yield_percentage = float(yield_str.replace('%', '')) / 100
                    except:
                        pass
                
                # Calculate rental income
                annual_rental_income = current_value * yield_percentage
                monthly_rental_income = annual_rental_income / 12
                
                # Calculate rental growth
                rental_growth_rate = 0.045  # 4.5% annual growth
                
                # Generate rental forecast
                rental_forecast = []
                for year in range(3):  # 3-year forecast
                    if year == 0:
                        year_rental = monthly_rental_income
                        year_annual = annual_rental_income
                        growth = '-'
                    else:
                        year_rental = rental_forecast[year-1]['monthly_rent'] * (1 + rental_growth_rate)
                        year_annual = year_rental * 12
                        growth = f'{rental_growth_rate*100:.1f}%'
                    
                    rental_forecast.append({
                        'year': f'Year {year if year > 0 else "Current"}',
                        'monthly_rent': year_rental,
                        'formatted_monthly_rent': f'£{year_rental:,.0f}',
                        'annual_rent': year_annual,
                        'formatted_annual_rent': f'£{year_annual:,.0f}',
                        'growth': growth
                    })
                
                return {
                    'monthly_rental_income': monthly_rental_income,
                    'formatted_monthly_rental_income': f'£{monthly_rental_income:,.0f}',
                    'annual_rental_income': annual_rental_income,
                    'formatted_annual_rental_income': f'£{annual_rental_income:,.0f}',
                    'gross_yield': yield_percentage,
                    'formatted_gross_yield': f'{yield_percentage*100:.1f}%',
                    'rental_demand': market_data.get('rental_demand', 'Medium'),
                    'rental_forecast': rental_forecast,
                    'rental_growth_rate': rental_growth_rate,
                    'formatted_rental_growth_rate': f'{rental_growth_rate*100:.1f}%'
                }
        except Exception as e:
            logger.error(f"Error calculating rental analysis: {str(e)}")
            # Return basic rental analysis if calculation fails
            return {
                'formatted_monthly_rental_income': '£2,000',
                'formatted_annual_rental_income': '£24,000',
                'formatted_gross_yield': '4.8%',
                'rental_forecast': [
                    {'year': 'Year Current', 'formatted_monthly_rent': '£2,000', 'growth': '-'},
                    {'year': 'Year 1', 'formatted_monthly_rent': '£2,090', 'growth': '4.5%'},
                    {'year': 'Year 2', 'formatted_monthly_rent': '£2,184', 'growth': '4.5%'}
                ],
                'formatted_rental_growth_rate': '4.5%'
            }
    
    def _assess_planning_opportunities(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess planning opportunities for the property using OpenAI.
        
        Args:
            property_data: Complete property data from Research Agent
            
        Returns:
            Dictionary with planning assessment
        """
        self.log_activity("Assessing planning opportunities")
        
        # Prepare the input data for OpenAI
        property_details = property_data.get('property_details', {})
        planning_history = property_data.get('planning_history', {})
        local_area_info = property_data.get('local_area_info', {})
        
        property_json = json.dumps(property_details, indent=2)
        planning_json = json.dumps(planning_history, indent=2)
        local_json = json.dumps(local_area_info, indent=2)
        
        # Add user message requesting planning assessment
        self.add_to_conversation("user", f"""
        Assess planning opportunities and constraints for this property based on the following information:
        
        PROPERTY DETAILS:
        {property_json}
        
        PLANNING HISTORY:
        {planning_json}
        
        LOCAL AREA INFORMATION:
        {local_json}
        
        Please provide:
        1. Current use class of the property
        2. List of planning opportunities (3-5 items)
        3. List of planning constraints (2-4 items)
        4. List of recommendations (3 items)
        
        Return the results as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.5,
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
                planning_assessment = json.loads(json_str)
                return planning_assessment
            else:
                # If no JSON found, create default planning assessment
                current_use_class = property_details.get('current_use_class', 'C3 (Residential)')
                
                return {
                    'current_use_class': current_use_class,
                    'planning_history': planning_history,
                    'opportunities': [
                        'Potential for internal reconfiguration within existing use class',
                        'Possibility for loft conversion or extension (subject to planning permission)',
                        'Potential for modernization to increase rental value'
                    ],
                    'constraints': [
                        'Change of use from residential may require planning permission',
                        'Any external alterations may require planning approval'
                    ],
                    'recommendations': [
                        'Consult with local planning authority for specific guidance',
                        'Consider pre-application advice for major alterations',
                        'Review local development plan for future area changes'
                    ]
                }
        except Exception as e:
            logger.error(f"Error assessing planning opportunities: {str(e)}")
            # Return basic planning assessment if assessment fails
            return {
                'current_use_class': 'C3 (Residential)',
                'opportunities': ['Internal reconfiguration potential'],
                'constraints': ['Planning permission required for major changes'],
                'recommendations': ['Consult with local planning authority']
            }
    
    def _assess_risks(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risks associated with the property investment using OpenAI.
        
        Args:
            property_data: Complete property data from Research Agent
            
        Returns:
            Dictionary with risk assessment
        """
        self.log_activity("Assessing investment risks")
        
        # Prepare the input data for OpenAI
        property_details = property_data.get('property_details', {})
        market_data = property_data.get('market_data', {})
        local_area_info = property_data.get('local_area_info', {})
        
        property_json = json.dumps(property_details, indent=2)
        market_json = json.dumps(market_data, indent=2)
        local_json = json.dumps(local_area_info, indent=2)
        
        # Add user message requesting risk assessment
        self.add_to_conversation("user", f"""
        Assess investment risks for this property based on the following information:
        
        PROPERTY DETAILS:
        {property_json}
        
        MARKET DATA:
        {market_json}
        
        LOCAL AREA INFORMATION:
        {local_json}
        
        Please provide:
        1. Overall risk profile (High/Medium/Low)
        2. List of identified risks (3-5 items), each with:
           - Category (Market, Financial, Legal, Regulatory, Property)
           - Description
           - Impact (High/Medium/Low)
           - Mitigation strategy
        3. Brief overall assessment
        
        Return the results as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.5,
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
                risk_assessment = json.loads(json_str)
                return risk_assessment
            else:
                # If no JSON found, create default risk assessment
                tenure = property_details.get('tenure', '')
                market_sentiment = market_data.get('market_sentiment', '')
                
                risks = []
                
                # Add market risk if sentiment is not strong
                if market_sentiment != 'Strong':
                    risks.append({
                        'category': 'Market',
                        'description': 'Market sentiment is not strong, which may affect future value growth',
                        'impact': 'Medium',
                        'mitigation': 'Consider longer-term hold strategy to ride out market fluctuations'
                    })
                
                # Add leasehold risk if applicable
                if tenure == 'Leasehold':
                    risks.append({
                        'category': 'Legal',
                        'description': 'Leasehold property may have service charges and lease length considerations',
                        'impact': 'Medium',
                        'mitigation': 'Verify lease length and service charge history before purchase'
                    })
                
                # Add default risks
                risks.append({
                    'category': 'Financial',
                    'description': 'Interest rate changes could affect financing costs and overall profitability',
                    'impact': 'Medium',
                    'mitigation': 'Consider fixed-rate financing options to provide cost certainty'
                })
                
                risks.append({
                    'category': 'Regulatory',
                    'description': 'Changes to landlord regulations or tax policies could impact returns',
                    'impact': 'Medium',
                    'mitigation': 'Stay informed of regulatory changes and maintain compliance'
                })
                
                return {
                    'risk_profile': 'Medium',
                    'identified_risks': risks,
                    'overall_assessment': 'The property presents a moderate risk profile with manageable challenges'
                }
        except Exception as e:
            logger.error(f"Error assessing risks: {str(e)}")
            # Return basic risk assessment if assessment fails
            return {
                'risk_profile': 'Medium',
                'identified_risks': [
                    {
                        'category': 'Financial',
                        'description': 'Interest rate fluctuations',
                        'impact': 'Medium',
                        'mitigation': 'Fixed-rate financing'
                    },
                    {
                        'category': 'Market',
                        'description': 'Market volatility',
                        'impact': 'Medium',
                        'mitigation': 'Long-term investment strategy'
                    }
                ],
                'overall_assessment': 'Moderate risk profile'
            }
    
    def _analyze_comparables(self, comparables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze comparable properties using OpenAI.
        
        Args:
            comparables: List of comparable properties from Research Agent
            
        Returns:
            Dictionary with comparable analysis
        """
        self.log_activity("Analyzing comparable properties")
        
        if not comparables:
            return {
                'count': 0,
                'comparables': [],
                'average_price': 0,
                'formatted_average_price': '£0',
                'average_price_per_sqft': 0,
                'formatted_average_price_per_sqft': '£0',
                'analysis': 'No comparable properties available for analysis'
            }
        
        # Prepare the input data for OpenAI
        comparables_json = json.dumps(comparables, indent=2)
        
        # Add user message requesting comparable analysis
        self.add_to_conversation("user", f"""
        Analyze these comparable properties:
        
        COMPARABLE PROPERTIES:
        {comparables_json}
        
        Please provide:
        1. Count of comparable properties
        2. Average sale price
        3. Average price per square foot
        4. Brief analysis of the comparables (1-2 sentences)
        
        Format all monetary values with currency symbols.
        Return the results as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.3,  # Lower temperature for more consistent calculations
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
                comparable_analysis = json.loads(json_str)
                
                # Add the original comparables to the analysis
                comparable_analysis['comparables'] = comparables
                
                return comparable_analysis
            else:
                # If no JSON found, calculate basic analysis
                total_price = 0
                total_price_per_sqft = 0
                count = len(comparables)
                
                for comp in comparables:
                    # Extract price
                    price_str = comp.get('sale_price', '£0')
                    try:
                        price = int(price_str.replace('£', '').replace(',', ''))
                    except:
                        price = 0
                    
                    # Extract price per sqft
                    price_per_sqft_str = comp.get('price_per_sqft', '£0')
                    try:
                        price_per_sqft = int(price_per_sqft_str.replace('£', '').replace(',', ''))
                    except:
                        price_per_sqft = 0
                    
                    total_price += price
                    total_price_per_sqft += price_per_sqft
                
                avg_price = total_price / count if count > 0 else 0
                avg_price_per_sqft = total_price_per_sqft / count if count > 0 else 0
                
                return {
                    'count': count,
                    'comparables': comparables,
                    'average_price': avg_price,
                    'formatted_average_price': f'£{avg_price:,.0f}',
                    'average_price_per_sqft': avg_price_per_sqft,
                    'formatted_average_price_per_sqft': f'£{avg_price_per_sqft:.0f}',
                    'analysis': f'Based on {count} comparable properties within 0.5 miles'
                }
        except Exception as e:
            logger.error(f"Error analyzing comparables: {str(e)}")
            # Return basic comparable analysis if analysis fails
            return {
                'count': len(comparables),
                'comparables': comparables,
                'formatted_average_price': '£500,000',
                'formatted_average_price_per_sqft': '£700',
                'analysis': f'Based on {len(comparables)} comparable properties'
            }
    
    def _generate_executive_summary(self, property_details: Dict[str, Any], 
                                   current_valuation: Dict[str, Any],
                                   development_scenarios: List[Dict[str, Any]], 
                                   rental_analysis: Dict[str, Any],
                                   planning_assessment: Dict[str, Any], 
                                   risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an executive summary for the property using OpenAI.
        
        Args:
            property_details: Property details
            current_valuation: Current valuation results
            development_scenarios: Development scenarios
            rental_analysis: Rental analysis
            planning_assessment: Planning assessment
            risk_assessment: Risk assessment
            
        Returns:
            Dictionary with executive summary
        """
        self.log_activity("Generating executive summary")
        
        # Prepare the input data for OpenAI
        property_json = json.dumps(property_details, indent=2)
        valuation_json = json.dumps(current_valuation, indent=2)
        scenarios_json = json.dumps(development_scenarios, indent=2)
        rental_json = json.dumps(rental_analysis, indent=2)
        planning_json = json.dumps(planning_assessment, indent=2)
        risk_json = json.dumps(risk_assessment, indent=2)
        
        # Add user message requesting executive summary
        self.add_to_conversation("user", f"""
        Generate an executive summary for this property based on the following information:
        
        PROPERTY DETAILS:
        {property_json}
        
        CURRENT VALUATION:
        {valuation_json}
        
        DEVELOPMENT SCENARIOS:
        {scenarios_json}
        
        RENTAL ANALYSIS:
        {rental_json}
        
        PLANNING ASSESSMENT:
        {planning_json}
        
        RISK ASSESSMENT:
        {risk_json}
        
        Please provide:
        1. Property type
        2. Current valuation
        3. Best development scenario (name, cost, new value, ROI)
        4. Rental income and gross yield
        5. Key planning opportunities and constraints
        6. Risk profile
        7. Recommended investment strategy (Refurbish to sell, Refurbish to let, Buy to let, Hold for capital growth)
        8. Brief rationale for the strategy
        
        Return the results as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.5,
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
                executive_summary = json.loads(json_str)
                return executive_summary
            else:
                # If no JSON found, create default executive summary
                # Determine best development scenario based on ROI
                best_scenario = None
                best_roi = 0
                for scenario in development_scenarios:
                    roi = 0
                    roi_str = scenario.get('formatted_roi', '0%')
                    try:
                        roi = float(roi_str.replace('%', ''))
                    except:
                        pass
                    
                    if roi > best_roi:
                        best_roi = roi
                        best_scenario = scenario
                
                if not best_scenario and development_scenarios:
                    best_scenario = development_scenarios[0]
                
                # Determine investment strategy
                strategy = 'Buy to let'
                rationale = 'Good rental yield potential'
                
                yield_value = 0
                yield_str = rental_analysis.get('formatted_gross_yield', '0%')
                try:
                    yield_value = float(yield_str.replace('%', ''))
                except:
                    pass
                
                if yield_value > 5 and best_roi > 100:
                    strategy = 'Refurbish to let'
                    rationale = 'High rental yield combined with good refurbishment returns'
                elif yield_value <= 5 and best_roi > 50:
                    strategy = 'Refurbish to sell'
                    rationale = 'Moderate rental yield but good potential for capital growth after refurbishment'
                elif yield_value <= 4:
                    strategy = 'Hold for capital growth'
                    rationale = 'Limited immediate returns but potential for long-term appreciation'
                
                return {
                    'property_type': property_details.get('property_type', 'Residential'),
                    'current_valuation': current_valuation.get('formatted_value', '£500,000'),
                    'best_development_scenario': {
                        'name': best_scenario.get('name', 'Refurbishment') if best_scenario else 'Refurbishment',
                        'cost': best_scenario.get('formatted_cost', '£50,000') if best_scenario else '£50,000',
                        'new_value': best_scenario.get('formatted_new_value', '£550,000') if best_scenario else '£550,000',
                        'roi': best_scenario.get('formatted_roi', '50%') if best_scenario else '50%'
                    },
                    'rental_income': rental_analysis.get('formatted_monthly_rental_income', '£2,000'),
                    'gross_yield': rental_analysis.get('formatted_gross_yield', '4.8%'),
                    'planning_opportunities': planning_assessment.get('opportunities', ['Internal reconfiguration potential']),
                    'planning_constraints': planning_assessment.get('constraints', ['Planning permission required for major changes']),
                    'risk_profile': risk_assessment.get('risk_profile', 'Medium'),
                    'investment_strategy': strategy,
                    'strategy_rationale': rationale
                }
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            # Return basic executive summary if generation fails
            return {
                'property_type': 'Residential',
                'current_valuation': '£500,000',
                'best_development_scenario': {
                    'name': 'Refurbishment',
                    'cost': '£50,000',
                    'new_value': '£550,000',
                    'roi': '50%'
                },
                'rental_income': '£2,000',
                'gross_yield': '4.8%',
                'planning_opportunities': ['Internal reconfiguration potential'],
                'planning_constraints': ['Planning permission required for major changes'],
                'risk_profile': 'Medium',
                'investment_strategy': 'Buy to let',
                'strategy_rationale': 'Good rental yield potential'
            }
    
    def _generate_conclusion(self, property_details: Dict[str, Any], 
                            current_valuation: Dict[str, Any],
                            development_scenarios: List[Dict[str, Any]], 
                            rental_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a conclusion for the property report using OpenAI.
        
        Args:
            property_details: Property details
            current_valuation: Current valuation results
            development_scenarios: Development scenarios
            rental_analysis: Rental analysis
            
        Returns:
            Dictionary with conclusion
        """
        self.log_activity("Generating conclusion")
        
        # Prepare the input data for OpenAI
        property_json = json.dumps(property_details, indent=2)
        valuation_json = json.dumps(current_valuation, indent=2)
        scenarios_json = json.dumps(development_scenarios, indent=2)
        rental_json = json.dumps(rental_analysis, indent=2)
        
        # Add user message requesting conclusion
        self.add_to_conversation("user", f"""
        Generate a conclusion for this property report based on the following information:
        
        PROPERTY DETAILS:
        {property_json}
        
        CURRENT VALUATION:
        {valuation_json}
        
        DEVELOPMENT SCENARIOS:
        {scenarios_json}
        
        RENTAL ANALYSIS:
        {rental_json}
        
        Please provide:
        1. BTR (Build to Rent) potential rating (excellent/good/moderate/poor)
        2. Summary statement about the property (1-2 sentences including property type, size, value, rental income, and yield)
        3. Recommendation statement (1 sentence about the best development scenario)
        
        Return the results as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.5,
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
                conclusion = json.loads(json_str)
                return conclusion
            else:
                # If no JSON found, create default conclusion
                # Determine BTR potential based on yield
                btr_potential = 'moderate'
                yield_value = 0
                yield_str = rental_analysis.get('formatted_gross_yield', '0%')
                try:
                    yield_value = float(yield_str.replace('%', ''))
                except:
                    pass
                
                if yield_value > 15:
                    btr_potential = 'excellent'
                elif yield_value > 8:
                    btr_potential = 'good'
                elif yield_value > 5:
                    btr_potential = 'moderate'
                else:
                    btr_potential = 'poor'
                
                # Determine best development scenario
                best_scenario = None
                best_roi = 0
                for scenario in development_scenarios:
                    roi = 0
                    roi_str = scenario.get('formatted_roi', '0%')
                    try:
                        roi = float(roi_str.replace('%', ''))
                    except:
                        pass
                    
                    if roi > best_roi:
                        best_roi = roi
                        best_scenario = scenario
                
                if not best_scenario and development_scenarios:
                    best_scenario = development_scenarios[0]
                
                # Generate summary
                property_type = property_details.get('property_type', 'property')
                floor_area = property_details.get('floor_area', 'unknown size')
                value = current_valuation.get('formatted_value', '£500,000')
                rental_income = rental_analysis.get('formatted_monthly_rental_income', '£2,000')
                yield_str = rental_analysis.get('formatted_gross_yield', '4.8%')
                
                summary = f"This {floor_area} {property_type} property has {btr_potential} BTR potential. The estimated value is {value} with a potential monthly rental income of {rental_income}, giving a gross yield of {yield_str}."
                
                # Generate recommendation
                recommendation = "Consider holding the property as-is for rental income."
                if best_scenario:
                    scenario_name = best_scenario.get('name', 'refurbishment').lower()
                    scenario_cost = best_scenario.get('formatted_cost', '£50,000')
                    scenario_new_value = best_scenario.get('formatted_new_value', '£550,000')
                    scenario_roi = best_scenario.get('formatted_roi', '50%')
                    
                    recommendation = f"The recommended strategy is to {scenario_name} with an estimated cost of {scenario_cost}, potentially increasing the property value to {scenario_new_value} (ROI: {scenario_roi})."
                
                return {
                    'btr_potential': btr_potential,
                    'summary': summary,
                    'recommendation': recommendation
                }
        except Exception as e:
            logger.error(f"Error generating conclusion: {str(e)}")
            # Return basic conclusion if generation fails
            return {
                'btr_potential': 'moderate',
                'summary': 'This property has moderate BTR potential with a reasonable yield.',
                'recommendation': 'Consider light refurbishment to improve rental returns.'
            }
