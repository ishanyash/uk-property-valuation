"""
Minimal Backend Test Framework for Property Valuation App - Refined Version

This script provides a simple, testable backend for the property valuation app
with improved agent prompts for realistic ROI, yield calculations, and location-specific details.
"""

import os
import sys
import json
import logging
import time
from typing import Dict, Any, List
from dotenv import load_dotenv
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agent_output.log')
    ]
)
logger = logging.getLogger("property_valuation")

# Load environment variables
load_dotenv()

class SimpleAgent:
    """Base class for all agents in the minimal test framework"""
    
    def __init__(self, name: str, model: str = "gpt-4"):
        self.name = name
        self.model = model
        self.client = None
        self._initialize_client()
        logger.info(f"Agent {name} initialized")
        
    def _initialize_client(self):
        """Initialize the OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error(f"OpenAI API key not found. Please add it to your .env file.")
            raise ValueError("OpenAI API key not found")
            
        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise
    
    def call_openai(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Call OpenAI API with simple retry logic"""
        if not self.client:
            self._initialize_client()
            
        max_retries = 3
        retry_count = 0
        retry_delay = 2
        
        while retry_count <= max_retries:
            try:
                logger.info(f"[{self.name}] Calling OpenAI API")
                
                # Log the messages being sent (for debugging)
                for msg in messages:
                    logger.debug(f"Message ({msg['role']}): {msg['content'][:100]}...")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature
                )
                
                content = response.choices[0].message.content
                logger.info(f"[{self.name}] Received response from OpenAI API")
                logger.debug(f"Response: {content[:100]}...")
                
                return content
                
            except openai.RateLimitError as e:
                retry_count += 1
                if retry_count > max_retries:
                    logger.error(f"[{self.name}] Rate limit reached after {max_retries} retries")
                    raise
                
                logger.warning(f"[{self.name}] Rate limit reached. Waiting {retry_delay} seconds before retry {retry_count}/{max_retries}")
                time.sleep(retry_delay)
                retry_delay *= 2
                
            except Exception as e:
                logger.error(f"[{self.name}] Error calling OpenAI API: {str(e)}")
                raise
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process method")


class ResearchAgent(SimpleAgent):
    """Agent responsible for researching property data"""
    
    def __init__(self):
        super().__init__("Research Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research property data based on address"""
        address = input_data.get("address", "")
        logger.info(f"[{self.name}] Researching property: {address}")
        
        # Extract postcode for location-specific research
        postcode = self._extract_postcode(address)
        region = self._determine_region(postcode)
        
        # Create system prompt
        system_prompt = """You are a property research agent specializing in UK real estate. Your task is to gather detailed, location-specific information about a UK property based on its address.
Focus on the following aspects:
1. Property details (type, size, bedrooms, bathrooms, etc.)
2. Local area information specific to the postcode/region (amenities, transport, schools, etc.)
3. Accurate market data for the specific location (average prices, trends, etc.)
4. Planning history and opportunities relevant to the property type and area
5. Genuinely comparable properties in the immediate vicinity

Format your response as a structured JSON object with these sections."""
        
        # Create user prompt
        user_prompt = f"""Research the following UK property address:
{address}

Postcode: {postcode}
Region: {region}

Generate realistic, location-specific data that accurately reflects:
1. The property type and features typical for this specific area
2. Local amenities and transport links actually present in this location
3. Current market conditions in this specific postcode area
4. Realistic planning history based on local council policies
5. Genuinely comparable properties with realistic prices for this location

Return your findings as a JSON object with the following structure:
{{
  "property_details": {{
    "property_type": "... (specific to this location)",
    "bedrooms": 0,
    "bathrooms": 0,
    "reception_rooms": 0,
    "floor_area": "... sq ft",
    "epc_rating": "... (realistic for property age and type)",
    "tenure": "...",
    "year_built": "... (realistic for the area)"
  }},
  "local_area": {{
    "description": "... (specific to {region} and {postcode})",
    "amenities": ["... (actual local amenities)", "..."],
    "transport_links": ["... (actual transport options)", "..."],
    "schools": ["... (actual local schools)", "..."],
    "crime_rate": "... (based on actual local statistics)"
  }},
  "market_data": {{
    "average_price": "£... (accurate for {postcode} area)",
    "price_per_sqft": "£... (accurate for {postcode} area)",
    "price_trend_1yr": "...% (realistic for {region})",
    "price_trend_5yr": "...% (realistic for {region})",
    "rental_yield": "...% (realistic for this property type in {postcode})",
    "days_on_market": 0
  }},
  "planning_history": {{
    "recent_applications": ["... (realistic for this property type)", "..."],
    "local_development_plans": ["... (actual local development plans)", "..."]
  }},
  "comparable_properties": [
    {{
      "address": "... (nearby address in same postcode area)",
      "price": "£... (realistic for the area)",
      "sold_date": "... (recent date)",
      "description": "... (similar property features)"
    }},
    ...
  ]
}}

Ensure all data is accurate and specific to {postcode} in {region}, with realistic property features, prices, and market trends for this exact location."""
        
        # Call OpenAI API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_content = self.call_openai(messages)
            
            # Parse JSON response
            try:
                property_data = json.loads(response_content)
                logger.info(f"[{self.name}] Successfully parsed property data")
                
                # Save raw response to file for inspection
                with open("research_output_refined.json", "w") as f:
                    json.dump(property_data, f, indent=2)
                    
                return {
                    "address": address,
                    "postcode": postcode,
                    "region": region,
                    "property_data": property_data
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"[{self.name}] Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response_content}")
                
                # Save problematic response for debugging
                with open("research_error_output.txt", "w") as f:
                    f.write(response_content)
                    
                raise ValueError(f"Failed to parse research data: {str(e)}")
                
        except Exception as e:
            logger.error(f"[{self.name}] Error in research process: {str(e)}")
            raise
    
    def _extract_postcode(self, address: str) -> str:
        """Extract postcode from address"""
        # Simple regex-like extraction for UK postcodes
        # In a real implementation, this would use a proper UK postcode regex
        parts = address.upper().split()
        if len(parts) >= 1:
            # Look for postcode patterns in the address parts
            for i in range(len(parts)-1, -1, -1):
                part = parts[i]
                # Check for common UK postcode formats
                if len(part) >= 5 and any(c.isdigit() for c in part) and any(c.isalpha() for c in part):
                    return part
            
            # If no postcode found, try to extract from the last parts
            if len(parts) >= 2:
                potential_postcode = f"{parts[-2]} {parts[-1]}"
                if any(c.isdigit() for c in potential_postcode) and any(c.isalpha() for c in potential_postcode):
                    return potential_postcode
        
        # If no postcode pattern found, return the last part or empty string
        return parts[-1] if parts else ""
    
    def _determine_region(self, postcode: str) -> str:
        """Determine UK region based on postcode"""
        postcode = postcode.upper()
        
        # Map first one or two characters of postcode to regions
        # This is a simplified version - a real implementation would be more comprehensive
        region_map = {
            'B': 'Birmingham',
            'BA': 'Bath',
            'BB': 'Blackburn',
            'BD': 'Bradford',
            'BH': 'Bournemouth',
            'BL': 'Bolton',
            'BN': 'Brighton',
            'BR': 'Bromley',
            'BS': 'Bristol',
            'CA': 'Carlisle',
            'CB': 'Cambridge',
            'CF': 'Cardiff',
            'CH': 'Chester',
            'CM': 'Chelmsford',
            'CO': 'Colchester',
            'CR': 'Croydon',
            'CT': 'Canterbury',
            'CV': 'Coventry',
            'CW': 'Crewe',
            'DA': 'Dartford',
            'DD': 'Dundee',
            'DE': 'Derby',
            'DG': 'Dumfries',
            'DH': 'Durham',
            'DL': 'Darlington',
            'DN': 'Doncaster',
            'DT': 'Dorchester',
            'DY': 'Dudley',
            'E': 'East London',
            'EC': 'East Central London',
            'EH': 'Edinburgh',
            'EN': 'Enfield',
            'EX': 'Exeter',
            'FK': 'Falkirk',
            'FY': 'Blackpool',
            'G': 'Glasgow',
            'GL': 'Gloucester',
            'GU': 'Guildford',
            'HA': 'Harrow',
            'HD': 'Huddersfield',
            'HG': 'Harrogate',
            'HP': 'Hemel Hempstead',
            'HR': 'Hereford',
            'HS': 'Outer Hebrides',
            'HU': 'Hull',
            'HX': 'Halifax',
            'IG': 'Ilford',
            'IP': 'Ipswich',
            'IV': 'Inverness',
            'KA': 'Kilmarnock',
            'KT': 'Kingston upon Thames',
            'KW': 'Kirkwall',
            'KY': 'Kirkcaldy',
            'L': 'Liverpool',
            'LA': 'Lancaster',
            'LD': 'Llandrindod Wells',
            'LE': 'Leicester',
            'LL': 'Llandudno',
            'LN': 'Lincoln',
            'LS': 'Leeds',
            'LU': 'Luton',
            'M': 'Manchester',
            'ME': 'Medway',
            'MK': 'Milton Keynes',
            'ML': 'Motherwell',
            'N': 'North London',
            'NE': 'Newcastle upon Tyne',
            'NG': 'Nottingham',
            'NN': 'Northampton',
            'NP': 'Newport',
            'NR': 'Norwich',
            'NW': 'North West London',
            'OL': 'Oldham',
            'OX': 'Oxford',
            'PA': 'Paisley',
            'PE': 'Peterborough',
            'PH': 'Perth',
            'PL': 'Plymouth',
            'PO': 'Portsmouth',
            'PR': 'Preston',
            'RG': 'Reading',
            'RH': 'Redhill',
            'RM': 'Romford',
            'S': 'Sheffield',
            'SA': 'Swansea',
            'SE': 'South East London',
            'SG': 'Stevenage',
            'SK': 'Stockport',
            'SL': 'Slough',
            'SM': 'Sutton',
            'SN': 'Swindon',
            'SO': 'Southampton',
            'SP': 'Salisbury',
            'SR': 'Sunderland',
            'SS': 'Southend-on-Sea',
            'ST': 'Stoke-on-Trent',
            'SW': 'South West London',
            'SY': 'Shrewsbury',
            'TA': 'Taunton',
            'TD': 'Galashiels',
            'TF': 'Telford',
            'TN': 'Tunbridge Wells',
            'TQ': 'Torquay',
            'TR': 'Truro',
            'TS': 'Cleveland',
            'TW': 'Twickenham',
            'UB': 'Southall',
            'W': 'West London',
            'WA': 'Warrington',
            'WC': 'West Central London',
            'WD': 'Watford',
            'WF': 'Wakefield',
            'WN': 'Wigan',
            'WR': 'Worcester',
            'WS': 'Walsall',
            'WV': 'Wolverhampton',
            'YO': 'York',
            'ZE': 'Lerwick'
        }
        
        # Try to match the first one or two characters
        if len(postcode) >= 2:
            prefix = postcode[:2]
            if prefix in region_map:
                return region_map[prefix]
            
            # Try just the first character
            prefix = postcode[0]
            if prefix in region_map:
                return region_map[prefix]
        
        # Default to UK if no match found
        return "United Kingdom"


class EvaluationAgent(SimpleAgent):
    """Agent responsible for evaluating property data and generating valuations"""
    
    def __init__(self):
        super().__init__("Evaluation Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate property data and generate valuations"""
        address = input_data.get("address", "")
        property_data = input_data.get("property_data", {})
        postcode = input_data.get("postcode", "")
        region = input_data.get("region", "")
        
        logger.info(f"[{self.name}] Evaluating property: {address}")
        
        # Create system prompt
        system_prompt = """You are a property evaluation agent specializing in the UK market. Your task is to analyze property research data and generate realistic valuations, development scenarios, and investment analysis.
Focus on the following aspects:
1. Current market valuation based on comparables and local data.
2. Realistic development scenarios with plausible costs, value uplifts (typically 50-80% of cost), and ROI.
3. Accurate rental analysis and yield calculations (Gross and Net).
4. Nuanced investment risk assessment specific to the property and location.
5. Identification of planning opportunities and constraints.

Format your response as a structured JSON object with these sections."""
        
        # Create user prompt with property data
        user_prompt = f"""Evaluate the following UK property based on the provided research data:

Address: {address}
Postcode: {postcode}
Region: {region}

Property Research Data: {json.dumps(property_data, indent=2)}

Generate realistic evaluations, valuations, and analysis consistent with UK property market norms. Pay close attention to the following:
- Ensure development scenario ROIs are plausible (value uplift should typically be 50-80% of the cost).
- Calculate Gross Yield accurately based on market value and annual rent.
- Provide a Net Yield estimate considering typical operational costs (e.g., management, maintenance, insurance).
- Base risk assessments on specific factors identified in the research data.

Return your evaluation as a JSON object with the following structure:
{{
  "current_valuation": {{
    "market_value": "£...",
    "valuation_basis": "Comparable sales analysis and local market data",
    "confidence_level": "High/Medium/Low",
    "value_range": {{
      "lower": "£...",
      "upper": "£..."
    }}
  }},
  "development_scenarios": [
    {{
      "name": "Scenario Name (e.g., Kitchen Refurbishment)",
      "description": "Detailed description of the work",
      "cost": "£... (Estimated cost)",
      "value_uplift": "£... (Plausible uplift, typically 50-80% of cost)",
      "new_value": "£... (Original Value + Uplift)",
      "roi": "...% (Calculated as (Value Uplift / Cost) * 100)",
      "timeframe": "... (e.g., 3-6 months)"
    }},
    ...
  ],
  "rental_analysis": {{
    "monthly_rental_income": "£... (Estimated based on market data)",
    "annual_rental_income": "£... (Monthly * 12)",
    "gross_yield": "...% (Calculated as (Annual Rent / Market Value) * 100)",
    "net_yield": "...% (Estimated Gross Yield minus typical operational costs, e.g., 15-25%)",
    "rental_demand": "High/Medium/Low",
    "rental_growth_forecast": "...% (Annual forecast based on local trends)"
  }},
  "investment_risk_assessment": {{
    "risk_profile": "High/Medium/Low",
    "key_risks": [
        "Specific risk 1 (e.g., Market downturn in {region})", 
        "Specific risk 2 (e.g., Potential planning restrictions)"
    ],
    "risk_mitigation": [
        "Mitigation strategy 1", 
        "Mitigation strategy 2"
    ]
  }},
  "planning_opportunities": {{
    "potential_developments": [
        "Specific opportunity 1 (e.g., Loft conversion)", 
        "Specific opportunity 2 (e.g., Rear extension)"
    ],
    "planning_constraints": [
        "Specific constraint 1 (e.g., Conservation area restrictions)", 
        "Specific constraint 2 (e.g., Limited garden space)"
    ],
    "recommended_approach": "Recommendation on pursuing planning"
  }}
}}

Ensure all financial figures are realistic for the UK property market and the specific location. Double-check calculations for ROI and Yields."""
        
        # Call OpenAI API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_content = self.call_openai(messages)
            
            # Parse JSON response
            try:
                evaluation_data = json.loads(response_content)
                logger.info(f"[{self.name}] Successfully parsed evaluation data")
                
                # Save raw response to file for inspection
                with open("evaluation_output_refined.json", "w") as f:
                    json.dump(evaluation_data, f, indent=2)
                    
                return {
                    "address": address,
                    "postcode": postcode,
                    "region": region,
                    "property_data": property_data,
                    "evaluation_data": evaluation_data
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"[{self.name}] Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response_content}")
                
                # Save problematic response for debugging
                with open("evaluation_error_output.txt", "w") as f:
                    f.write(response_content)
                    
                raise ValueError(f"Failed to parse evaluation data: {str(e)}")
                
        except Exception as e:
            logger.error(f"[{self.name}] Error in evaluation process: {str(e)}")
            raise


class AccessorAgent(SimpleAgent):
    """Agent responsible for reviewing and approving property evaluations"""
    
    def __init__(self):
        super().__init__("Accessor Agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review and approve property evaluations"""
        address = input_data.get("address", "")
        property_data = input_data.get("property_data", {})
        evaluation_data = input_data.get("evaluation_data", {})
        postcode = input_data.get("postcode", "")
        region = input_data.get("region", "")
        
        logger.info(f"[{self.name}] Reviewing evaluation for: {address}")
        
        # Create system prompt
        system_prompt = """You are a property accessor agent specializing in UK property market validation. Your task is to review property research and evaluation data, verify its accuracy and consistency, and provide an executive summary.
Focus on the following aspects:
1. Verify that valuations are consistent with market data and comparable properties
2. Check that development scenarios have realistic costs, value uplifts, and ROI calculations
3. Validate rental projections against market norms and ensure yield calculations are accurate
4. Cross-check all financial figures for mathematical consistency
5. Assess the overall investment potential based on verified data

Format your response as a structured JSON object."""
        
        # Create user prompt with property and evaluation data
        user_prompt = f"""Review the following UK property research and evaluation data:

Address: {address}
Postcode: {postcode}
Region: {region}

Property Research Data: {json.dumps(property_data, indent=2)}

Property Evaluation Data: {json.dumps(evaluation_data, indent=2)}

Perform a thorough validation focusing on:
1. Mathematical consistency - verify all calculations (yields, ROIs, etc.)
2. Market realism - check if values align with the specific location
3. Development scenario plausibility - ensure value uplifts are realistic (typically 50-80% of costs)
4. Data consistency - check for contradictions between research and evaluation data

Return your review as a JSON object with the following structure:
{{
  "data_quality_assessment": {{
    "research_data_quality": "High/Medium/Low",
    "evaluation_data_quality": "High/Medium/Low",
    "consistency_issues": [
      "Specific issue 1 (e.g., 'Rental yield calculation is incorrect: should be X% not Y%')",
      "Specific issue 2 (e.g., 'Development ROI is unrealistic at 120%, should be 50-80%')"
    ] or [],
    "accuracy_issues": [
      "Specific issue 1 (e.g., 'Property value appears high compared to comparables')",
      "Specific issue 2 (e.g., 'EPC rating unlikely for property of this age without improvements')"
    ] or []
  }},
  "valuation_assessment": {{
    "valuation_accuracy": "Accurate/Overvalued/Undervalued",
    "recommended_adjustments": {{
      "market_value": "£..." or null,
      "development_costs": "..." or null,
      "rental_income": "..." or null
    }}
  }},
  "investment_assessment": {{
    "btr_potential": "High/Medium/Low",
    "investment_grade": "A/B/C/D",
    "recommended_strategy": "Specific strategy based on verified data"
  }},
  "executive_summary": {{
    "overview": "Concise summary of the property's investment potential",
    "key_findings": [
      "Specific finding 1",
      "Specific finding 2"
    ],
    "recommendations": [
      "Specific recommendation 1",
      "Specific recommendation 2"
    ]
  }}
}}

If you find any inconsistencies, mathematical errors, or unrealistic figures, note them specifically in your assessment and suggest corrections. Be particularly vigilant about:
1. Yield calculations (Annual Rent / Property Value)
2. ROI calculations for development scenarios (Value Uplift / Cost)
3. Consistency between property features and valuation
4. Alignment of data with the specific location ({region}, {postcode})"""
        
        # Call OpenAI API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_content = self.call_openai(messages)
            
            # Parse JSON response
            try:
                accessor_data = json.loads(response_content)
                logger.info(f"[{self.name}] Successfully parsed accessor data")
                
                # Save raw response to file for inspection
                with open("accessor_output_refined.json", "w") as f:
                    json.dump(accessor_data, f, indent=2)
                    
                return {
                    "address": address,
                    "postcode": postcode,
                    "region": region,
                    "property_data": property_data,
                    "evaluation_data": evaluation_data,
                    "accessor_data": accessor_data
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"[{self.name}] Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response_content}")
                
                # Save problematic response for debugging
                with open("accessor_error_output.txt", "w") as f:
                    f.write(response_content)
                    
                raise ValueError(f"Failed to parse accessor data: {str(e)}")
                
        except Exception as e:
            logger.error(f"[{self.name}] Error in accessor process: {str(e)}")
            raise


class ReportGenerator(SimpleAgent):
    """Agent responsible for generating the final property valuation report"""
    
    def __init__(self):
        super().__init__("Report Generator")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the final property valuation report"""
        address = input_data.get("address", "")
        property_data = input_data.get("property_data", {})
        evaluation_data = input_data.get("evaluation_data", {})
        accessor_data = input_data.get("accessor_data", {})
        postcode = input_data.get("postcode", "")
        region = input_data.get("region", "")
        
        logger.info(f"[{self.name}] Generating report for: {address}")
        
        # Create system prompt
        system_prompt = """You are a property report generator specializing in UK BTR (Build to Rent) property valuation reports. Your task is to create a comprehensive, accurate, and professional report based on validated research, evaluation, and accessor data.
The report should:
1. Incorporate any corrections or adjustments identified by the accessor
2. Present financial data with consistent calculations and realistic figures
3. Highlight specific location-based factors affecting the property
4. Provide actionable insights for property investors
5. Maintain a professional, evidence-based tone throughout"""
        
        # Create user prompt with all data
        user_prompt = f"""Generate a comprehensive BTR property valuation report for the following UK property:

Address: {address}
Postcode: {postcode}
Region: {region}

Based on the following data:

Property Research Data: {json.dumps(property_data, indent=2)}

Property Evaluation Data: {json.dumps(evaluation_data, indent=2)}

Accessor Review Data: {json.dumps(accessor_data, indent=2)}

Create a professional report that:
1. Incorporates any corrections identified by the accessor agent
2. Ensures all financial calculations are mathematically consistent
3. Provides location-specific insights relevant to {region} and {postcode}
4. Highlights any inconsistencies or areas requiring further investigation
5. Delivers clear, actionable recommendations for property investors

Format your report as a JSON object with the following structure:
{{
  "title": "BTR Property Valuation Report: {address}",
  "date": "May 30, 2025",
  "executive_summary": {{
    "overview": "Concise summary of the property's investment potential",
    "valuation": "Final valuation figure with any accessor adjustments",
    "btr_potential": "Assessment of BTR potential with supporting evidence",
    "key_recommendations": ["Specific recommendation 1", "Specific recommendation 2"]
  }},
  "property_appraisal": {{
    "address": "{address}",
    "description": "Detailed property description",
    "key_features": ["Feature 1", "Feature 2"],
    "condition": "Assessment of property condition",
    "market_value": "£... (Final valuation figure)",
    "valuation_basis": "Explanation of valuation methodology"
  }},
  "local_market_analysis": {{
    "area_overview": "Specific insights about {region} and {postcode}",
    "market_trends": "Current and projected trends in this specific location",
    "comparable_properties": "Analysis of comparable properties in the immediate area",
    "rental_market": "Detailed rental market analysis for this location",
    "tenant_demographics": "Typical tenant profile for this area"
  }},
  "development_potential": {{
    "current_planning_status": "Summary of existing planning permissions/constraints",
    "recommended_scenarios": "Prioritized development options with realistic ROIs",
    "cost_analysis": "Detailed breakdown of development costs",
    "value_uplift_potential": "Realistic value uplift projections (50-80% of costs)",
    "planning_considerations": "Location-specific planning factors"
  }},
  "investment_analysis": {{
    "rental_income_potential": "Projected rental income with supporting evidence",
    "yield_analysis": "Accurate gross and net yield calculations",
    "cash_flow_projections": "5-year cash flow forecast",
    "roi_analysis": "Realistic ROI projections for different scenarios",
    "risk_assessment": "Location and property-specific risk factors"
  }},
  "btr_strategy": {{
    "target_market": "Specific tenant demographic for this property",
    "positioning": "Recommended market positioning",
    "amenity_recommendations": "Suggested amenities based on local demand",
    "management_approach": "Recommended property management strategy",
    "exit_strategy": "Options for eventual sale or refinancing"
  }},
  "conclusion": {{
    "summary": "Final assessment of investment potential",
    "final_recommendation": "Clear, actionable recommendation"
  }}
}}

Ensure all financial figures are accurate, consistent with each other, and realistic for {postcode} in {region}. If the accessor identified any issues, incorporate the corrections in your report."""
        
        # Call OpenAI API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_content = self.call_openai(messages)
            
            # Parse JSON response
            try:
                report_data = json.loads(response_content)
                logger.info(f"[{self.name}] Successfully generated report")
                
                # Save raw response to file for inspection
                with open("report_output_refined.json", "w") as f:
                    json.dump(report_data, f, indent=2)
                
                # Also save a formatted text version for easy reading
                with open("report_output_refined.txt", "w") as f:
                    f.write(f"# {report_data.get('title', 'BTR Property Valuation Report')}\n")
                    f.write(f"Date: {report_data.get('date', 'May 30, 2025')}\n\n")
                    
                    # Executive Summary
                    f.write("## EXECUTIVE SUMMARY\n\n")
                    exec_summary = report_data.get('executive_summary', {})
                    f.write(f"{exec_summary.get('overview', '')}\n\n")
                    f.write(f"Valuation: {exec_summary.get('valuation', '')}\n")
                    f.write(f"BTR Potential: {exec_summary.get('btr_potential', '')}\n\n")
                    
                    f.write("Key Recommendations:\n")
                    for rec in exec_summary.get('key_recommendations', []):
                        f.write(f"- {rec}\n")
                    f.write("\n")
                    
                    # Property Appraisal
                    f.write("## PROPERTY APPRAISAL\n\n")
                    prop_appraisal = report_data.get('property_appraisal', {})
                    f.write(f"Address: {prop_appraisal.get('address', '')}\n\n")
                    f.write(f"{prop_appraisal.get('description', '')}\n\n")
                    
                    f.write("Key Features:\n")
                    for feature in prop_appraisal.get('key_features', []):
                        f.write(f"- {feature}\n")
                    f.write("\n")
                    
                    f.write(f"Condition: {prop_appraisal.get('condition', '')}\n")
                    f.write(f"Market Value: {prop_appraisal.get('market_value', '')}\n")
                    f.write(f"Valuation Basis: {prop_appraisal.get('valuation_basis', '')}\n\n")
                    
                    # Local Market Analysis
                    f.write("## LOCAL MARKET ANALYSIS\n\n")
                    market = report_data.get('local_market_analysis', {})
                    f.write(f"{market.get('area_overview', '')}\n\n")
                    f.write(f"Market Trends: {market.get('market_trends', '')}\n\n")
                    f.write(f"Comparable Properties: {market.get('comparable_properties', '')}\n\n")
                    f.write(f"Rental Market: {market.get('rental_market', '')}\n\n")
                    f.write(f"Tenant Demographics: {market.get('tenant_demographics', '')}\n\n")
                    
                    # Development Potential
                    f.write("## DEVELOPMENT POTENTIAL\n\n")
                    dev = report_data.get('development_potential', {})
                    f.write(f"Current Planning Status: {dev.get('current_planning_status', '')}\n\n")
                    f.write(f"Recommended Scenarios: {dev.get('recommended_scenarios', '')}\n\n")
                    f.write(f"Cost Analysis: {dev.get('cost_analysis', '')}\n\n")
                    f.write(f"Value Uplift Potential: {dev.get('value_uplift_potential', '')}\n\n")
                    f.write(f"Planning Considerations: {dev.get('planning_considerations', '')}\n\n")
                    
                    # Investment Analysis
                    f.write("## INVESTMENT ANALYSIS\n\n")
                    inv = report_data.get('investment_analysis', {})
                    f.write(f"Rental Income Potential: {inv.get('rental_income_potential', '')}\n\n")
                    f.write(f"Yield Analysis: {inv.get('yield_analysis', '')}\n\n")
                    f.write(f"Cash Flow Projections: {inv.get('cash_flow_projections', '')}\n\n")
                    f.write(f"ROI Analysis: {inv.get('roi_analysis', '')}\n\n")
                    f.write(f"Risk Assessment: {inv.get('risk_assessment', '')}\n\n")
                    
                    # BTR Strategy
                    f.write("## BTR STRATEGY\n\n")
                    btr = report_data.get('btr_strategy', {})
                    f.write(f"Target Market: {btr.get('target_market', '')}\n\n")
                    f.write(f"Positioning: {btr.get('positioning', '')}\n\n")
                    f.write(f"Amenity Recommendations: {btr.get('amenity_recommendations', '')}\n\n")
                    f.write(f"Management Approach: {btr.get('management_approach', '')}\n\n")
                    f.write(f"Exit Strategy: {btr.get('exit_strategy', '')}\n\n")
                    
                    # Conclusion
                    f.write("## CONCLUSION\n\n")
                    conclusion = report_data.get('conclusion', {})
                    f.write(f"{conclusion.get('summary', '')}\n\n")
                    f.write(f"Final Recommendation: {conclusion.get('final_recommendation', '')}\n")
                    
                return {
                    "address": address,
                    "postcode": postcode,
                    "region": region,
                    "report_data": report_data,
                    "report_file": "report_output_refined.txt",
                    "json_file": "report_output_refined.json"
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"[{self.name}] Failed to parse JSON response: {str(e)}")
                logger.debug(f"Raw response: {response_content}")
                
                # Save problematic response for debugging
                with open("report_error_output.txt", "w") as f:
                    f.write(response_content)
                    
                raise ValueError(f"Failed to parse report data: {str(e)}")
                
        except Exception as e:
            logger.error(f"[{self.name}] Error in report generation process: {str(e)}")
            raise


def run_workflow(address: str) -> Dict[str, Any]:
    """Run the complete agent workflow for a given address"""
    logger.info(f"Starting workflow for address: {address}")
    
    try:
        # 1. Research Agent
        research_agent = ResearchAgent()
        research_result = research_agent.process({"address": address})
        logger.info("Research stage completed successfully")
        
        # 2. Evaluation Agent
        evaluation_agent = EvaluationAgent()
        evaluation_result = evaluation_agent.process(research_result)
        logger.info("Evaluation stage completed successfully")
        
        # 3. Accessor Agent
        accessor_agent = AccessorAgent()
        accessor_result = accessor_agent.process(evaluation_result)
        logger.info("Accessor stage completed successfully")
        
        # 4. Report Generator
        report_generator = ReportGenerator()
        report_result = report_generator.process(accessor_result)
        logger.info("Report generation completed successfully")
        
        logger.info(f"Workflow completed successfully for address: {address}")
        return {
            "success": True,
            "address": address,
            "report_file": report_result.get("report_file"),
            "json_file": report_result.get("json_file")
        }
        
    except Exception as e:
        logger.error(f"Error in workflow: {str(e)}")
        return {
            "success": False,
            "address": address,
            "error": str(e)
        }


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OpenAI API key not found. Please add it to your .env file.")
        print("Create a .env file with the following content:")
        print("OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Get address from command line or use default
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = input("Enter UK property address: ")
    
    if not address:
        print("ERROR: No address provided")
        sys.exit(1)
    
    print(f"Running workflow for address: {address}")
    print("This will use your OpenAI API key to generate a property valuation report.")
    print("Check agent_output.log for detailed progress and output files for results.")
    print()
    
    result = run_workflow(address)
    
    if result["success"]:
        print(f"Workflow completed successfully for: {address}")
        print(f"Report saved to: {result['report_file']}")
        print(f"JSON data saved to: {result['json_file']}")
        print("\nYou can examine these files to see the output of each agent and the final report.")
        print("The log file agent_output.log contains detailed information about the process.")
    else:
        print(f"Workflow failed for: {address}")
        print(f"Error: {result['error']}")
        print("\nCheck agent_output.log for more details on what went wrong.")
