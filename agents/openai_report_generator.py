# OpenAI-Powered Report Generation Agent

from typing import Dict, List, Any, Optional
import json
import logging
import time
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ReportGenerationAgent(BaseAgent):
    """
    Report Generation Agent - Creates dynamic, professional property valuation reports
    
    This agent uses OpenAI to generate natural language content for property valuation reports
    based on the approved data from the Accessor Agent. It creates contextual, professional
    report sections with appropriate formatting and style.
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Report Generation Agent.
        
        Args:
            model: OpenAI model to use (default: gpt-4)
        """
        super().__init__("Report Generation Agent", model)
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the Report Generation Agent.
        
        Returns:
            System prompt string
        """
        return """
        You are the Report Generation Agent, an AI specialized in creating professional property valuation reports.
        Your task is to transform approved data from the Accessor Agent into well-written, contextual report content
        that provides valuable insights for property investors.
        
        You should:
        1. Generate natural language content for each section of the report
        2. Ensure a professional, authoritative tone throughout
        3. Highlight key insights and recommendations clearly
        4. Format content appropriately for each section
        5. Maintain consistency in terminology and style
        6. Include all relevant data points in a readable, digestible format
        
        Your writing should be clear, concise, and valuable to property investors.
        Avoid unnecessary jargon while maintaining professional real estate terminology.
        """
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete property valuation report based on approved data.
        
        Args:
            input_data: Dictionary containing approved data from the Accessor Agent
            
        Returns:
            Dictionary with complete report content
        """
        if 'address' not in input_data:
            raise ValueError("Approved data must include an address")
        
        address = input_data.get('address', '')
        self.log_activity(f"Starting report generation for address: {address}")
        self.initialize_conversation()
        
        # Generate report sections
        report_content = {
            'address': address,
            'title': self._generate_title(address, input_data),
            'executive_summary': self._generate_executive_summary(input_data.get('executive_summary', {})),
            'property_appraisal': self._generate_property_appraisal(
                input_data.get('property_appraisal', {}),
                address
            ),
            'feasibility_study': self._generate_feasibility_study(
                input_data.get('feasibility_study', {}),
                address
            ),
            'planning_analysis': self._generate_planning_analysis(
                input_data.get('planning_analysis', {}),
                address
            ),
            'risk_assessment': self._generate_risk_assessment(
                input_data.get('risk_assessment', {}),
                address
            ),
            'local_market_analysis': self._generate_local_market_analysis(
                input_data.get('local_market_analysis', {}),
                address
            ),
            'conclusion': self._generate_conclusion(
                input_data.get('conclusion', {}),
                address
            ),
            'report_date': time.strftime('%B %d, %Y'),
            'report_id': f"BTR-{int(time.time())}"
        }
        
        # Generate HTML report
        report_html = self._generate_report_html(report_content)
        
        self.log_activity(f"Completed report generation for address: {address}")
        return {
            'address': address,
            'report_content': report_content,
            'report_html': report_html,
            'generation_timestamp': time.time()
        }
    
    def _generate_title(self, address: str, input_data: Dict[str, Any]) -> str:
        """
        Generate the report title using OpenAI.
        
        Args:
            address: Property address
            input_data: Complete approved data
            
        Returns:
            Report title string
        """
        self.log_activity("Generating report title")
        
        # Extract BTR potential from conclusion
        btr_potential = input_data.get('conclusion', {}).get('btr_potential', 'moderate')
        
        # Add user message requesting title generation
        self.add_to_conversation("user", f"""
        Generate a professional title for a property valuation report for this address:
        
        ADDRESS: {address}
        
        BTR POTENTIAL: {btr_potential}
        
        The title should be concise and include:
        1. The phrase "BTR Report"
        2. The property address or a shortened version of it
        3. The BTR potential rating
        
        Return only the title text, without any additional explanation.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
            max_tokens=100
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Clean up the title
        title = assistant_message.strip().replace('"', '')
        
        # If title is too long, create a simpler version
        if len(title) > 100:
            title = f"BTR Report: {address} - {btr_potential.capitalize()} Potential"
        
        return title
    
    def _generate_executive_summary(self, executive_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the executive summary section using OpenAI.
        
        Args:
            executive_summary: Executive summary data from Accessor Agent
            
        Returns:
            Dictionary with executive summary content
        """
        self.log_activity("Generating executive summary")
        
        # Prepare the input data for OpenAI
        summary_json = json.dumps(executive_summary, indent=2)
        
        # Add user message requesting executive summary generation
        self.add_to_conversation("user", f"""
        Generate a professional executive summary for a property valuation report based on this data:
        
        EXECUTIVE SUMMARY DATA:
        {summary_json}
        
        The executive summary should include:
        1. A brief overview of the property (type, current valuation)
        2. The best development scenario with key metrics
        3. Rental income potential and yield
        4. Key planning opportunities
        5. Risk profile
        6. Recommended investment strategy with rationale
        
        Write in a professional, authoritative tone. Format the response as a JSON object with these fields:
        - "overview": A paragraph with the property overview
        - "development": A paragraph about development potential
        - "rental": A paragraph about rental potential
        - "planning": A paragraph about planning opportunities
        - "risk": A paragraph about risk profile
        - "strategy": A paragraph about recommended strategy
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                summary_content = json.loads(json_str)
                
                # Add the original data
                summary_content['data'] = executive_summary
                
                return summary_content
            else:
                # If no JSON found, create default content
                return {
                    'overview': f"This {executive_summary.get('property_type', 'residential')} property is currently valued at {executive_summary.get('current_valuation', '£500,000')}.",
                    'development': "Development potential includes options for refurbishment to increase property value.",
                    'rental': f"The property has a potential monthly rental income of {executive_summary.get('rental_income', '£2,000')} with a gross yield of {executive_summary.get('gross_yield', '4.8%')}.",
                    'planning': "There are several planning opportunities available for this property.",
                    'risk': f"The overall risk profile is {executive_summary.get('risk_profile', 'medium')}.",
                    'strategy': f"The recommended investment strategy is {executive_summary.get('investment_strategy', 'Buy to let')} because {executive_summary.get('strategy_rationale', 'it offers good rental yield potential')}.",
                    'data': executive_summary
                }
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            # Return basic content if generation fails
            return {
                'overview': "This property offers investment potential in the current market.",
                'development': "Several development options are available to increase value.",
                'rental': "The property has good rental income potential.",
                'planning': "Planning opportunities exist for this property.",
                'risk': "The investment carries a moderate risk profile.",
                'strategy': "A balanced investment approach is recommended.",
                'data': executive_summary
            }
    
    def _generate_property_appraisal(self, property_appraisal: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Generate the property appraisal section using OpenAI.
        
        Args:
            property_appraisal: Property appraisal data from Accessor Agent
            address: Property address
            
        Returns:
            Dictionary with property appraisal content
        """
        self.log_activity("Generating property appraisal")
        
        # Extract key components
        property_details = property_appraisal.get('property_details', {})
        current_valuation = property_appraisal.get('current_valuation', {})
        comparable_analysis = property_appraisal.get('comparable_analysis', {})
        
        # Prepare the input data for OpenAI
        details_json = json.dumps(property_details, indent=2)
        valuation_json = json.dumps(current_valuation, indent=2)
        comparable_json = json.dumps(comparable_analysis, indent=2)
        
        # Add user message requesting property appraisal generation
        self.add_to_conversation("user", f"""
        Generate a professional property appraisal section for a valuation report based on this data:
        
        ADDRESS: {address}
        
        PROPERTY DETAILS:
        {details_json}
        
        CURRENT VALUATION:
        {valuation_json}
        
        COMPARABLE ANALYSIS:
        {comparable_json}
        
        The property appraisal should include:
        1. A detailed description of the property
        2. Current valuation with methodology and confidence level
        3. Analysis of comparable properties and how they support the valuation
        4. Key value drivers and detractors
        
        Write in a professional, authoritative tone. Format the response as a JSON object with these fields:
        - "description": A detailed paragraph describing the property
        - "valuation": A paragraph about the current valuation
        - "comparables": A paragraph analyzing comparable properties
        - "value_factors": A paragraph about key value drivers and detractors
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                appraisal_content = json.loads(json_str)
                
                # Add the original data
                appraisal_content['data'] = {
                    'property_details': property_details,
                    'current_valuation': current_valuation,
                    'comparable_analysis': comparable_analysis
                }
                
                return appraisal_content
            else:
                # If no JSON found, create default content
                property_type = property_details.get('property_type', 'residential property')
                bedrooms = property_details.get('bedrooms', '?')
                bathrooms = property_details.get('bathrooms', '?')
                floor_area = property_details.get('floor_area', 'unknown size')
                
                return {
                    'description': f"This {property_type} at {address} features {bedrooms} bedrooms and {bathrooms} bathrooms with a total floor area of {floor_area}.",
                    'valuation': f"The property is currently valued at {current_valuation.get('formatted_value', '£500,000')} based on {current_valuation.get('methodology', 'comparable analysis')}.",
                    'comparables': f"Analysis of {comparable_analysis.get('count', 'several')} comparable properties in the area supports this valuation.",
                    'value_factors': "Key value drivers include the property's location and condition.",
                    'data': {
                        'property_details': property_details,
                        'current_valuation': current_valuation,
                        'comparable_analysis': comparable_analysis
                    }
                }
        except Exception as e:
            logger.error(f"Error generating property appraisal: {str(e)}")
            # Return basic content if generation fails
            return {
                'description': f"This property at {address} offers comfortable living accommodation.",
                'valuation': "The property has been valued based on comparable properties in the area.",
                'comparables': "Several comparable properties support this valuation.",
                'value_factors': "Location and condition are key factors affecting the property's value.",
                'data': {
                    'property_details': property_details,
                    'current_valuation': current_valuation,
                    'comparable_analysis': comparable_analysis
                }
            }
    
    def _generate_feasibility_study(self, feasibility_study: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Generate the feasibility study section using OpenAI.
        
        Args:
            feasibility_study: Feasibility study data from Accessor Agent
            address: Property address
            
        Returns:
            Dictionary with feasibility study content
        """
        self.log_activity("Generating feasibility study")
        
        # Extract key components
        development_scenarios = feasibility_study.get('development_scenarios', [])
        rental_analysis = feasibility_study.get('rental_analysis', {})
        
        # Prepare the input data for OpenAI
        scenarios_json = json.dumps(development_scenarios, indent=2)
        rental_json = json.dumps(rental_analysis, indent=2)
        
        # Add user message requesting feasibility study generation
        self.add_to_conversation("user", f"""
        Generate a professional feasibility study section for a property valuation report based on this data:
        
        ADDRESS: {address}
        
        DEVELOPMENT SCENARIOS:
        {scenarios_json}
        
        RENTAL ANALYSIS:
        {rental_json}
        
        The feasibility study should include:
        1. An overview of development potential
        2. Detailed analysis of each development scenario (costs, value uplift, ROI)
        3. Rental income potential and yield analysis
        4. Rental growth forecast and implications
        5. Recommendations for maximizing returns
        
        Write in a professional, authoritative tone. Format the response as a JSON object with these fields:
        - "overview": A paragraph providing an overview of development potential
        - "scenarios": A paragraph analyzing the development scenarios
        - "rental_potential": A paragraph about rental income potential
        - "growth_forecast": A paragraph about rental growth forecast
        - "recommendations": A paragraph with recommendations for maximizing returns
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                feasibility_content = json.loads(json_str)
                
                # Add the original data
                feasibility_content['data'] = {
                    'development_scenarios': development_scenarios,
                    'rental_analysis': rental_analysis
                }
                
                return feasibility_content
            else:
                # If no JSON found, create default content
                return {
                    'overview': f"The property at {address} offers several development opportunities to increase its value and rental potential.",
                    'scenarios': "Multiple refurbishment scenarios have been analyzed, with varying costs, value uplifts, and returns on investment.",
                    'rental_potential': f"The property has potential for strong rental income with an estimated gross yield of {rental_analysis.get('formatted_gross_yield', '4.8%')}.",
                    'growth_forecast': f"Rental growth is projected at {rental_analysis.get('formatted_rental_growth_rate', '4.5%')} annually over the next few years.",
                    'recommendations': "To maximize returns, a targeted refurbishment focusing on key areas would be most effective.",
                    'data': {
                        'development_scenarios': development_scenarios,
                        'rental_analysis': rental_analysis
                    }
                }
        except Exception as e:
            logger.error(f"Error generating feasibility study: {str(e)}")
            # Return basic content if generation fails
            return {
                'overview': "This property offers development potential to increase value.",
                'scenarios': "Several refurbishment options have been analyzed.",
                'rental_potential': "The property has good rental income potential.",
                'growth_forecast': "Rental growth is expected to follow market trends.",
                'recommendations': "A balanced approach to refurbishment is recommended.",
                'data': {
                    'development_scenarios': development_scenarios,
                    'rental_analysis': rental_analysis
                }
            }
    
    def _generate_planning_analysis(self, planning_analysis: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Generate the planning analysis section using OpenAI.
        
        Args:
            planning_analysis: Planning analysis data from Accessor Agent
            address: Property address
            
        Returns:
            Dictionary with planning analysis content
        """
        self.log_activity("Generating planning analysis")
        
        # Prepare the input data for OpenAI
        planning_json = json.dumps(planning_analysis, indent=2)
        
        # Add user message requesting planning analysis generation
        self.add_to_conversation("user", f"""
        Generate a professional planning analysis section for a property valuation report based on this data:
        
        ADDRESS: {address}
        
        PLANNING ANALYSIS:
        {planning_json}
        
        The planning analysis should include:
        1. Current use class and implications
        2. Planning opportunities with explanation
        3. Planning constraints and challenges
        4. Recommendations for navigating planning processes
        
        Write in a professional, authoritative tone. Format the response as a JSON object with these fields:
        - "current_use": A paragraph about the current use class and implications
        - "opportunities": A paragraph about planning opportunities
        - "constraints": A paragraph about planning constraints
        - "recommendations": A paragraph with recommendations for planning
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                planning_content = json.loads(json_str)
                
                # Add the original data
                planning_content['data'] = planning_analysis
                
                return planning_content
            else:
                # If no JSON found, create default content
                current_use_class = planning_analysis.get('current_use_class', 'C3 (Residential)')
                opportunities = planning_analysis.get('opportunities', ['Internal reconfiguration potential'])
                constraints = planning_analysis.get('constraints', ['Planning permission required for major changes'])
                
                return {
                    'current_use': f"The property is currently classified as {current_use_class}, which allows for residential use.",
                    'opportunities': f"Planning opportunities include {', '.join(opportunities[:2])}.",
                    'constraints': f"Key planning constraints include {', '.join(constraints[:2])}.",
                    'recommendations': "It is recommended to consult with the local planning authority before undertaking any significant changes to the property.",
                    'data': planning_analysis
                }
        except Exception as e:
            logger.error(f"Error generating planning analysis: {str(e)}")
            # Return basic content if generation fails
            return {
                'current_use': "The property is currently in residential use.",
                'opportunities': "There are opportunities for internal improvements without planning permission.",
                'constraints': "Major external changes would require planning approval.",
                'recommendations': "Consult with planning professionals before making significant changes.",
                'data': planning_analysis
            }
    
    def _generate_risk_assessment(self, risk_assessment: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Generate the risk assessment section using OpenAI.
        
        Args:
            risk_assessment: Risk assessment data from Accessor Agent
            address: Property address
            
        Returns:
            Dictionary with risk assessment content
        """
        self.log_activity("Generating risk assessment")
        
        # Prepare the input data for OpenAI
        risk_json = json.dumps(risk_assessment, indent=2)
        
        # Add user message requesting risk assessment generation
        self.add_to_conversation("user", f"""
        Generate a professional risk assessment section for a property valuation report based on this data:
        
        ADDRESS: {address}
        
        RISK ASSESSMENT:
        {risk_json}
        
        The risk assessment should include:
        1. Overall risk profile and implications
        2. Analysis of key risk categories (market, financial, legal, etc.)
        3. Impact assessment of identified risks
        4. Mitigation strategies for major risks
        
        Write in a professional, authoritative tone. Format the response as a JSON object with these fields:
        - "overview": A paragraph about the overall risk profile
        - "key_risks": A paragraph analyzing key risk categories
        - "impact": A paragraph about the potential impact of identified risks
        - "mitigation": A paragraph about risk mitigation strategies
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                risk_content = json.loads(json_str)
                
                # Add the original data
                risk_content['data'] = risk_assessment
                
                return risk_content
            else:
                # If no JSON found, create default content
                risk_profile = risk_assessment.get('risk_profile', 'Medium')
                identified_risks = risk_assessment.get('identified_risks', [])
                
                risk_categories = []
                for risk in identified_risks[:3]:
                    if 'category' in risk:
                        risk_categories.append(risk['category'])
                
                if not risk_categories:
                    risk_categories = ['Market', 'Financial']
                
                return {
                    'overview': f"The property presents a {risk_profile.lower()} risk profile for investment.",
                    'key_risks': f"Key risk categories include {', '.join(risk_categories)}.",
                    'impact': "These risks could impact the property's value and rental returns if not properly managed.",
                    'mitigation': "Implementing appropriate mitigation strategies can help manage these risks effectively.",
                    'data': risk_assessment
                }
        except Exception as e:
            logger.error(f"Error generating risk assessment: {str(e)}")
            # Return basic content if generation fails
            return {
                'overview': "The property presents a moderate risk profile.",
                'key_risks': "Market and financial risks are the primary concerns.",
                'impact': "These risks could affect investment returns if not managed.",
                'mitigation': "Proper risk management strategies are recommended.",
                'data': risk_assessment
            }
    
    def _generate_local_market_analysis(self, local_market_analysis: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Generate the local market analysis section using OpenAI.
        
        Args:
            local_market_analysis: Local market analysis data from Accessor Agent
            address: Property address
            
        Returns:
            Dictionary with local market analysis content
        """
        self.log_activity("Generating local market analysis")
        
        # Extract key components
        market_data = local_market_analysis.get('market_data', {})
        local_area_info = local_market_analysis.get('local_area_info', {})
        
        # Prepare the input data for OpenAI
        market_json = json.dumps(market_data, indent=2)
        local_json = json.dumps(local_area_info, indent=2)
        
        # Add user message requesting local market analysis generation
        self.add_to_conversation("user", f"""
        Generate a professional local market analysis section for a property valuation report based on this data:
        
        ADDRESS: {address}
        
        MARKET DATA:
        {market_json}
        
        LOCAL AREA INFORMATION:
        {local_json}
        
        The local market analysis should include:
        1. Overview of the local property market
        2. Price trends and market sentiment
        3. Rental demand and yield analysis
        4. Local amenities and transport links
        5. Demographics and their impact on property demand
        
        Write in a professional, authoritative tone. Format the response as a JSON object with these fields:
        - "market_overview": A paragraph providing an overview of the local property market
        - "price_trends": A paragraph about price trends and market sentiment
        - "rental_market": A paragraph about rental demand and yields
        - "amenities": A paragraph about local amenities and transport
        - "demographics": A paragraph about local demographics and their impact
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                market_content = json.loads(json_str)
                
                # Add the original data
                market_content['data'] = {
                    'market_data': market_data,
                    'local_area_info': local_area_info
                }
                
                return market_content
            else:
                # If no JSON found, create default content
                price_trend_1yr = market_data.get('price_trend_1yr', '+3.2%')
                average_price_per_sqft = market_data.get('average_price_per_sqft', '£689')
                market_sentiment = market_data.get('market_sentiment', 'Stable')
                rental_demand = market_data.get('rental_demand', 'High')
                
                transport = local_area_info.get('transport', {})
                nearest_station = transport.get('nearest_station', 'the nearest station')
                transport_links = transport.get('transport_links', 'good')
                
                return {
                    'market_overview': f"The local property market around {address} is characterized by {market_sentiment.lower()} conditions with {rental_demand.lower()} rental demand.",
                    'price_trends': f"Property prices in the area have shown a {price_trend_1yr} change over the past year, with an average price per square foot of {average_price_per_sqft}.",
                    'rental_market': f"The rental market in this area is {rental_demand.lower()}, offering good potential for buy-to-let investors.",
                    'amenities': f"The property benefits from {transport_links} transport links, with {nearest_station} providing convenient access to the wider area.",
                    'demographics': "The local demographic profile supports continued demand for quality residential accommodation.",
                    'data': {
                        'market_data': market_data,
                        'local_area_info': local_area_info
                    }
                }
        except Exception as e:
            logger.error(f"Error generating local market analysis: {str(e)}")
            # Return basic content if generation fails
            return {
                'market_overview': "The local property market shows stable conditions.",
                'price_trends': "Property prices in the area have shown moderate growth.",
                'rental_market': "The rental market offers good potential for investors.",
                'amenities': "The property has good access to local amenities and transport.",
                'demographics': "The local demographic profile supports property demand.",
                'data': {
                    'market_data': market_data,
                    'local_area_info': local_area_info
                }
            }
    
    def _generate_conclusion(self, conclusion: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Generate the conclusion section using OpenAI.
        
        Args:
            conclusion: Conclusion data from Accessor Agent
            address: Property address
            
        Returns:
            Dictionary with conclusion content
        """
        self.log_activity("Generating conclusion")
        
        # Prepare the input data for OpenAI
        conclusion_json = json.dumps(conclusion, indent=2)
        
        # Add user message requesting conclusion generation
        self.add_to_conversation("user", f"""
        Generate a professional conclusion section for a property valuation report based on this data:
        
        ADDRESS: {address}
        
        CONCLUSION:
        {conclusion_json}
        
        The conclusion should include:
        1. Final assessment of the property's BTR potential
        2. Summary of key findings from the report
        3. Clear investment recommendation
        4. Next steps for the investor
        
        Write in a professional, authoritative tone. Format the response as a JSON object with these fields:
        - "btr_assessment": A paragraph about the property's BTR potential
        - "key_findings": A paragraph summarizing key findings
        - "recommendation": A paragraph with the investment recommendation
        - "next_steps": A paragraph outlining next steps for the investor
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                conclusion_content = json.loads(json_str)
                
                # Add the original data
                conclusion_content['data'] = conclusion
                
                return conclusion_content
            else:
                # If no JSON found, create default content
                btr_potential = conclusion.get('btr_potential', 'moderate')
                summary = conclusion.get('summary', 'This property has potential for investment.')
                recommendation = conclusion.get('recommendation', 'Consider refurbishment to improve returns.')
                
                return {
                    'btr_assessment': f"The property at {address} demonstrates {btr_potential} Build to Rent (BTR) potential.",
                    'key_findings': summary,
                    'recommendation': recommendation,
                    'next_steps': "We recommend arranging a viewing of the property and consulting with a financial advisor to discuss funding options.",
                    'data': conclusion
                }
        except Exception as e:
            logger.error(f"Error generating conclusion: {str(e)}")
            # Return basic content if generation fails
            return {
                'btr_assessment': "The property has moderate Build to Rent potential.",
                'key_findings': "Our analysis indicates this is a viable investment opportunity.",
                'recommendation': "Consider this property as part of a diversified portfolio.",
                'next_steps': "Arrange a viewing and consult with financial advisors.",
                'data': conclusion
            }
    
    def _generate_report_html(self, report_content: Dict[str, Any]) -> str:
        """
        Generate the complete HTML report using the report content.
        
        Args:
            report_content: Complete report content
            
        Returns:
            HTML string for the report
        """
        self.log_activity("Generating HTML report")
        
        # Extract key components
        address = report_content.get('address', '')
        title = report_content.get('title', f"BTR Report: {address}")
        report_date = report_content.get('report_date', time.strftime('%B %d, %Y'))
        report_id = report_content.get('report_id', f"BTR-{int(time.time())}")
        
        executive_summary = report_content.get('executive_summary', {})
        property_appraisal = report_content.get('property_appraisal', {})
        feasibility_study = report_content.get('feasibility_study', {})
        planning_analysis = report_content.get('planning_analysis', {})
        risk_assessment = report_content.get('risk_assessment', {})
        local_market_analysis = report_content.get('local_market_analysis', {})
        conclusion = report_content.get('conclusion', {})
        
        # Build the HTML report
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #ddd;
                    padding-bottom: 20px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .header p {{
                    color: #7f8c8d;
                    margin: 5px 0;
                }}
                .section {{
                    margin-bottom: 30px;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 20px;
                }}
                .section h2 {{
                    color: #2c3e50;
                    border-left: 4px solid #3498db;
                    padding-left: 10px;
                }}
                .section h3 {{
                    color: #2c3e50;
                    margin-top: 20px;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .data-table th, .data-table td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                .data-table th {{
                    background-color: #f2f2f2;
                }}
                .data-table tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .highlight-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 2px solid #ddd;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
                @media print {{
                    .container {{
                        width: 100%;
                        max-width: none;
                    }}
                    .no-print {{
                        display: none;
                    }}
                    body {{
                        font-size: 12pt;
                    }}
                    .section {{
                        page-break-inside: avoid;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <p>Property Address: {address}</p>
                    <p>Report Date: {report_date}</p>
                    <p>Report ID: {report_id}</p>
                </div>
                
                <div class="section">
                    <h2>Executive Summary</h2>
                    <div class="highlight-box">
                        <p><strong>BTR Potential:</strong> {conclusion.get('data', {}).get('btr_potential', 'Moderate').capitalize()}</p>
                        <p><strong>Recommended Strategy:</strong> {executive_summary.get('data', {}).get('investment_strategy', 'Buy to let')}</p>
                    </div>
                    <h3>Property Overview</h3>
                    <p>{executive_summary.get('overview', '')}</p>
                    <h3>Development Potential</h3>
                    <p>{executive_summary.get('development', '')}</p>
                    <h3>Rental Potential</h3>
                    <p>{executive_summary.get('rental', '')}</p>
                    <h3>Planning Opportunities</h3>
                    <p>{executive_summary.get('planning', '')}</p>
                    <h3>Risk Profile</h3>
                    <p>{executive_summary.get('risk', '')}</p>
                    <h3>Recommended Strategy</h3>
                    <p>{executive_summary.get('strategy', '')}</p>
                </div>
                
                <div class="section">
                    <h2>Property Appraisal</h2>
                    <h3>Property Description</h3>
                    <p>{property_appraisal.get('description', '')}</p>
                    <h3>Current Valuation</h3>
                    <p>{property_appraisal.get('valuation', '')}</p>
                    
                    <h3>Property Details</h3>
                    <table class="data-table">
                        <tr>
                            <th>Property Type</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('property_type', 'N/A')}</td>
                            <th>Tenure</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('tenure', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Bedrooms</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('bedrooms', 'N/A')}</td>
                            <th>Bathrooms</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('bathrooms', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Floor Area</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('floor_area', 'N/A')}</td>
                            <th>Year Built</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('year_built', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>EPC Rating</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('epc_rating', 'N/A')}</td>
                            <th>Council Tax Band</th>
                            <td>{property_appraisal.get('data', {}).get('property_details', {}).get('council_tax_band', 'N/A')}</td>
                        </tr>
                    </table>
                    
                    <h3>Comparable Properties</h3>
                    <p>{property_appraisal.get('comparables', '')}</p>
                    
                    <h3>Value Factors</h3>
                    <p>{property_appraisal.get('value_factors', '')}</p>
                </div>
                
                <div class="section">
                    <h2>Feasibility Study</h2>
                    <h3>Development Overview</h3>
                    <p>{feasibility_study.get('overview', '')}</p>
                    
                    <h3>Development Scenarios</h3>
                    <p>{feasibility_study.get('scenarios', '')}</p>
                    
                    <table class="data-table">
                        <tr>
                            <th>Scenario</th>
                            <th>Cost</th>
                            <th>Value Uplift</th>
                            <th>New Value</th>
                            <th>ROI</th>
                        </tr>
        """
        
        # Add development scenarios to the table
        for scenario in feasibility_study.get('data', {}).get('development_scenarios', []):
            html += f"""
                        <tr>
                            <td>{scenario.get('name', 'N/A')}</td>
                            <td>{scenario.get('formatted_cost', 'N/A')}</td>
                            <td>{scenario.get('formatted_value_uplift', 'N/A')} ({scenario.get('value_uplift_percentage', 'N/A')})</td>
                            <td>{scenario.get('formatted_new_value', 'N/A')}</td>
                            <td>{scenario.get('formatted_roi', 'N/A')}</td>
                        </tr>
            """
        
        html += f"""
                    </table>
                    
                    <h3>Rental Potential</h3>
                    <p>{feasibility_study.get('rental_potential', '')}</p>
                    
                    <table class="data-table">
                        <tr>
                            <th>Monthly Rental Income</th>
                            <td>{feasibility_study.get('data', {}).get('rental_analysis', {}).get('formatted_monthly_rental_income', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Annual Rental Income</th>
                            <td>{feasibility_study.get('data', {}).get('rental_analysis', {}).get('formatted_annual_rental_income', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Gross Yield</th>
                            <td>{feasibility_study.get('data', {}).get('rental_analysis', {}).get('formatted_gross_yield', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Rental Growth Rate</th>
                            <td>{feasibility_study.get('data', {}).get('rental_analysis', {}).get('formatted_rental_growth_rate', 'N/A')}</td>
                        </tr>
                    </table>
                    
                    <h3>Rental Growth Forecast</h3>
                    <p>{feasibility_study.get('growth_forecast', '')}</p>
                    
                    <table class="data-table">
                        <tr>
                            <th>Year</th>
                            <th>Monthly Rent</th>
                            <th>Annual Rent</th>
                            <th>Growth</th>
                        </tr>
        """
        
        # Add rental forecast to the table
        for forecast in feasibility_study.get('data', {}).get('rental_analysis', {}).get('rental_forecast', []):
            html += f"""
                        <tr>
                            <td>{forecast.get('year', 'N/A')}</td>
                            <td>{forecast.get('formatted_monthly_rent', 'N/A')}</td>
                            <td>{forecast.get('formatted_annual_rent', 'N/A')}</td>
                            <td>{forecast.get('growth', 'N/A')}</td>
                        </tr>
            """
        
        html += f"""
                    </table>
                    
                    <h3>Recommendations</h3>
                    <p>{feasibility_study.get('recommendations', '')}</p>
                </div>
                
                <div class="section">
                    <h2>Planning Analysis</h2>
                    <h3>Current Use</h3>
                    <p>{planning_analysis.get('current_use', '')}</p>
                    
                    <h3>Planning Opportunities</h3>
                    <p>{planning_analysis.get('opportunities', '')}</p>
                    <ul>
        """
        
        # Add planning opportunities to the list
        for opportunity in planning_analysis.get('data', {}).get('opportunities', []):
            html += f"""
                        <li>{opportunity}</li>
            """
        
        html += f"""
                    </ul>
                    
                    <h3>Planning Constraints</h3>
                    <p>{planning_analysis.get('constraints', '')}</p>
                    <ul>
        """
        
        # Add planning constraints to the list
        for constraint in planning_analysis.get('data', {}).get('constraints', []):
            html += f"""
                        <li>{constraint}</li>
            """
        
        html += f"""
                    </ul>
                    
                    <h3>Recommendations</h3>
                    <p>{planning_analysis.get('recommendations', '')}</p>
                </div>
                
                <div class="section">
                    <h2>Risk Assessment</h2>
                    <h3>Risk Overview</h3>
                    <p>{risk_assessment.get('overview', '')}</p>
                    
                    <div class="highlight-box">
                        <p><strong>Overall Risk Profile:</strong> {risk_assessment.get('data', {}).get('risk_profile', 'Medium')}</p>
                    </div>
                    
                    <h3>Key Risks</h3>
                    <p>{risk_assessment.get('key_risks', '')}</p>
                    
                    <table class="data-table">
                        <tr>
                            <th>Category</th>
                            <th>Description</th>
                            <th>Impact</th>
                            <th>Mitigation</th>
                        </tr>
        """
        
        # Add identified risks to the table
        for risk in risk_assessment.get('data', {}).get('identified_risks', []):
            html += f"""
                        <tr>
                            <td>{risk.get('category', 'N/A')}</td>
                            <td>{risk.get('description', 'N/A')}</td>
                            <td>{risk.get('impact', 'N/A')}</td>
                            <td>{risk.get('mitigation', 'N/A')}</td>
                        </tr>
            """
        
        html += f"""
                    </table>
                    
                    <h3>Impact Assessment</h3>
                    <p>{risk_assessment.get('impact', '')}</p>
                    
                    <h3>Mitigation Strategies</h3>
                    <p>{risk_assessment.get('mitigation', '')}</p>
                </div>
                
                <div class="section">
                    <h2>Local Market Analysis</h2>
                    <h3>Market Overview</h3>
                    <p>{local_market_analysis.get('market_overview', '')}</p>
                    
                    <h3>Price Trends</h3>
                    <p>{local_market_analysis.get('price_trends', '')}</p>
                    
                    <table class="data-table">
                        <tr>
                            <th>Average Price per Sqft</th>
                            <td>{local_market_analysis.get('data', {}).get('market_data', {}).get('average_price_per_sqft', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>1-Year Price Trend</th>
                            <td>{local_market_analysis.get('data', {}).get('market_data', {}).get('price_trend_1yr', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>5-Year Price Trend</th>
                            <td>{local_market_analysis.get('data', {}).get('market_data', {}).get('price_trend_5yr', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Market Sentiment</th>
                            <td>{local_market_analysis.get('data', {}).get('market_data', {}).get('market_sentiment', 'N/A')}</td>
                        </tr>
                    </table>
                    
                    <h3>Rental Market</h3>
                    <p>{local_market_analysis.get('rental_market', '')}</p>
                    
                    <table class="data-table">
                        <tr>
                            <th>Average Rental Yield</th>
                            <td>{local_market_analysis.get('data', {}).get('market_data', {}).get('average_rental_yield', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Rental Demand</th>
                            <td>{local_market_analysis.get('data', {}).get('market_data', {}).get('rental_demand', 'N/A')}</td>
                        </tr>
                        <tr>
                            <th>Average Time on Market</th>
                            <td>{local_market_analysis.get('data', {}).get('market_data', {}).get('average_time_on_market', 'N/A')}</td>
                        </tr>
                    </table>
                    
                    <h3>Local Amenities and Transport</h3>
                    <p>{local_market_analysis.get('amenities', '')}</p>
                    
                    <h3>Demographics</h3>
                    <p>{local_market_analysis.get('demographics', '')}</p>
                </div>
                
                <div class="section">
                    <h2>Conclusion</h2>
                    <div class="highlight-box">
                        <p><strong>BTR Potential:</strong> {conclusion.get('data', {}).get('btr_potential', 'Moderate').capitalize()}</p>
                    </div>
                    
                    <h3>BTR Assessment</h3>
                    <p>{conclusion.get('btr_assessment', '')}</p>
                    
                    <h3>Key Findings</h3>
                    <p>{conclusion.get('key_findings', '')}</p>
                    
                    <h3>Investment Recommendation</h3>
                    <p>{conclusion.get('recommendation', '')}</p>
                    
                    <h3>Next Steps</h3>
                    <p>{conclusion.get('next_steps', '')}</p>
                </div>
                
                <div class="footer">
                    <p>This report was generated on {report_date}</p>
                    <p>Report ID: {report_id}</p>
                    <p>&copy; 2025 Property Valuation App. All rights reserved.</p>
                    <p class="no-print">This report is for informational purposes only and should not be considered as financial advice.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
