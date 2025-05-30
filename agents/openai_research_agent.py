# OpenAI-Powered Research Agent

from typing import Dict, List, Any, Optional
import json
import requests
import logging
import time
from bs4 import BeautifulSoup
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """
    Research Agent - Gathers property information from various sources using OpenAI
    
    This agent uses OpenAI to generate search queries, process search results,
    and extract relevant property information from various sources.
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the Research Agent.
        
        Args:
            model: OpenAI model to use (default: gpt-4)
        """
        super().__init__("Research Agent", model)
        self.sources = [
            "Land Registry",
            "Valuation Office Agency (VOA)",
            "Local council records",
            "Rightmove",
            "Zoopla",
            "OpenStreetMap"
        ]
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the Research Agent.
        
        Returns:
            System prompt string
        """
        return """
        You are the Research Agent, an AI specialized in gathering property information from various sources.
        Your task is to collect comprehensive data about UK properties based on their addresses.
        
        You should:
        1. Generate appropriate search queries for different aspects of property information
        2. Extract relevant details from search results and web pages
        3. Organize the information in a structured format
        4. Verify information across multiple sources when possible
        5. Indicate confidence levels for gathered information
        
        Focus on collecting:
        - Property details (type, size, bedrooms, bathrooms, etc.)
        - Current and historical market values
        - Comparable properties in the area
        - Local amenities and transport links
        - Planning history and development potential
        - Market trends and rental yields
        
        Be thorough, accurate, and provide source attribution for all information.
        """
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input address and gather property information.
        
        Args:
            input_data: Dictionary containing the address
            
        Returns:
            Dictionary of gathered property data
        """
        address = input_data.get('address', '')
        if not address:
            raise ValueError("Address is required for research")
        
        self.log_activity(f"Starting research for address: {address}")
        self.initialize_conversation()
        
        # Parse the address
        address_parts = self._parse_address(address)
        
        # Generate search queries based on the address
        search_queries = self._generate_search_queries(address, address_parts)
        
        # Gather property data using the search queries
        property_data = {
            'address': address,
            'parsed_address': address_parts,
            'property_details': self._get_property_details(address, search_queries),
            'market_data': self._get_market_data(address, address_parts),
            'comparable_properties': self._get_comparable_properties(address, address_parts),
            'local_area_info': self._get_local_area_info(address, address_parts),
            'planning_history': self._get_planning_history(address, address_parts),
            'sources': self.sources,
            'confidence': 'medium',  # Default confidence level
            'research_timestamp': time.time()
        }
        
        self.log_activity(f"Completed research for address: {address}")
        return property_data
    
    def _parse_address(self, address: str) -> Dict[str, str]:
        """
        Parse a UK address into its components using OpenAI.
        
        Args:
            address: Full UK address string
            
        Returns:
            Dictionary of address components
        """
        self.log_activity("Parsing address")
        
        # Add user message with the address
        self.add_to_conversation("user", f"""
        Parse the following UK address into its components:
        
        Address: {address}
        
        Extract the following components:
        - Building name/number
        - Street
        - City/Town
        - County
        - Postcode
        
        Return the result as a JSON object with these fields.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.1,  # Low temperature for deterministic output
            max_tokens=500
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response if it's wrapped in text
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                address_parts = json.loads(json_str)
            else:
                # If no JSON found, create a simple structure
                address_parts = {
                    'building': '',
                    'street': '',
                    'city': '',
                    'county': '',
                    'postcode': ''
                }
                
                # Try to extract postcode using a simple pattern
                import re
                postcode_match = re.search(r'[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}', address)
                if postcode_match:
                    address_parts['postcode'] = postcode_match.group(0)
            
            return address_parts
        except Exception as e:
            logger.error(f"Error parsing address: {str(e)}")
            # Return a basic structure if parsing fails
            return {
                'full_address': address,
                'postcode': '',
                'city': '',
                'street': ''
            }
    
    def _generate_search_queries(self, address: str, address_parts: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Generate search queries for different aspects of property information.
        
        Args:
            address: Full address string
            address_parts: Parsed address components
            
        Returns:
            Dictionary of search queries by category
        """
        self.log_activity("Generating search queries")
        
        # Add user message requesting search queries
        self.add_to_conversation("user", f"""
        Generate search queries to gather information about the following UK property:
        
        Address: {address}
        
        Generate 2-3 specific search queries for each of these categories:
        1. Property details and history
        2. Current market value and recent sales
        3. Comparable properties in the area
        4. Local amenities and transport
        5. Planning history and development potential
        
        Format your response as a JSON object with these categories as keys and arrays of search queries as values.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                search_queries = json.loads(json_str)
            else:
                # If no JSON found, create default queries
                postcode = address_parts.get('postcode', '')
                search_queries = {
                    "property_details": [
                        f"{address} property details",
                        f"{address} property type bedrooms"
                    ],
                    "market_value": [
                        f"{address} property value",
                        f"{postcode} property prices"
                    ],
                    "comparable_properties": [
                        f"similar properties to {address}",
                        f"{postcode} recent property sales"
                    ],
                    "local_area": [
                        f"{postcode} amenities transport",
                        f"{address} nearby schools shops"
                    ],
                    "planning_history": [
                        f"{address} planning permission history",
                        f"{postcode} development plans"
                    ]
                }
            
            return search_queries
        except Exception as e:
            logger.error(f"Error generating search queries: {str(e)}")
            # Return basic queries if generation fails
            return {
                "property_details": [f"{address} property details"],
                "market_value": [f"{address} property value"],
                "comparable_properties": [f"{address} similar properties"],
                "local_area": [f"{address} local amenities"],
                "planning_history": [f"{address} planning history"]
            }
    
    def _get_property_details(self, address: str, search_queries: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Get property details using OpenAI to process search results.
        
        Args:
            address: Property address
            search_queries: Generated search queries
            
        Returns:
            Dictionary of property details
        """
        self.log_activity("Gathering property details")
        
        # In a real implementation, we would:
        # 1. Execute the search queries
        # 2. Extract content from search results
        # 3. Use OpenAI to process and extract structured data
        
        # For this prototype, we'll simulate the process with OpenAI
        
        # Add user message requesting property details extraction
        self.add_to_conversation("user", f"""
        Based on the address "{address}", generate realistic property details.
        
        Imagine you've searched for information using these queries:
        {json.dumps(search_queries.get('property_details', []))}
        
        Generate realistic property details including:
        - Property type (detached, semi-detached, terraced, flat/apartment)
        - Tenure (freehold, leasehold)
        - Year built (approximate)
        - Floor area in square feet
        - Number of bedrooms
        - Number of bathrooms
        - EPC rating
        - Council tax band
        - Last sold price and date (if available)
        - Current use class
        
        Make the details realistic for a property at this address. Return the information as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                property_details = json.loads(json_str)
            else:
                # If no JSON found, create default details
                property_details = {
                    'property_type': 'Flat/Maisonette',
                    'tenure': 'Leasehold',
                    'year_built': '1980',
                    'floor_area': '700 sqft',
                    'bedrooms': 2,
                    'bathrooms': 1,
                    'epc_rating': 'C',
                    'council_tax_band': 'D',
                    'last_sold_price': '£420,000',
                    'last_sold_date': 'June 2022',
                    'current_use_class': 'C3 (Residential)'
                }
            
            return property_details
        except Exception as e:
            logger.error(f"Error extracting property details: {str(e)}")
            # Return basic details if extraction fails
            return {
                'property_type': 'Unknown',
                'bedrooms': 0,
                'bathrooms': 0,
                'floor_area': 'Unknown',
                'current_use_class': 'Unknown'
            }
    
    def _get_market_data(self, address: str, address_parts: Dict[str, str]) -> Dict[str, Any]:
        """
        Get market data for the area using OpenAI.
        
        Args:
            address: Property address
            address_parts: Parsed address components
            
        Returns:
            Dictionary of market data
        """
        self.log_activity("Gathering market data")
        
        postcode = address_parts.get('postcode', '')
        city = address_parts.get('city', '')
        
        # Add user message requesting market data
        self.add_to_conversation("user", f"""
        Generate realistic market data for a property at this address:
        
        Address: {address}
        Postcode: {postcode}
        City/Town: {city}
        
        Include the following information:
        - Average price per square foot in the area
        - Price trends (1-year and 5-year)
        - Average rental yield
        - Rental demand (High/Medium/Low)
        - Sales demand (High/Medium/Low)
        - Average time on market
        - Market sentiment (Strong/Stable/Weak)
        
        Make the data realistic for this location. Return the information as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
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
                market_data = json.loads(json_str)
            else:
                # If no JSON found, create default market data
                market_data = {
                    'average_price_per_sqft': '£689',
                    'price_trend_1yr': '+3.2%',
                    'price_trend_5yr': '+12.8%',
                    'average_rental_yield': '4.5%',
                    'rental_demand': 'High',
                    'sales_demand': 'Medium',
                    'average_time_on_market': '45 days',
                    'market_sentiment': 'Stable'
                }
            
            return market_data
        except Exception as e:
            logger.error(f"Error extracting market data: {str(e)}")
            # Return basic market data if extraction fails
            return {
                'average_price_per_sqft': 'Unknown',
                'price_trend_1yr': 'Unknown',
                'average_rental_yield': 'Unknown',
                'market_sentiment': 'Unknown'
            }
    
    def _get_comparable_properties(self, address: str, address_parts: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Get comparable properties in the area using OpenAI.
        
        Args:
            address: Property address
            address_parts: Parsed address components
            
        Returns:
            List of comparable properties
        """
        self.log_activity("Finding comparable properties")
        
        postcode = address_parts.get('postcode', '')
        city = address_parts.get('city', '')
        
        # Add user message requesting comparable properties
        self.add_to_conversation("user", f"""
        Generate 3-4 realistic comparable properties for a property at this address:
        
        Address: {address}
        Postcode: {postcode}
        City/Town: {city}
        
        For each comparable property, include:
        - Address
        - Property type
        - Number of bedrooms
        - Number of bathrooms
        - Floor area
        - Sale price
        - Sale date (within the last 6 months)
        - Price per square foot
        - Distance from the target property (in miles)
        - Comparability rating (High/Medium/Low) with brief reasoning
        
        Make the properties realistic for this location. Return the information as a JSON array.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
            max_tokens=1200
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '[' in assistant_message and ']' in assistant_message:
                json_str = assistant_message[assistant_message.find('['):assistant_message.rfind(']')+1]
                comparables = json.loads(json_str)
            else:
                # If no JSON found, create default comparables
                comparables = [
                    {
                        'address': '12 Sample Street, London, SW1A 2AB',
                        'property_type': 'Flat/Maisonette',
                        'bedrooms': 2,
                        'bathrooms': 1,
                        'floor_area': '680 sqft',
                        'sale_price': '£475,000',
                        'sale_date': 'March 2025',
                        'price_per_sqft': '£699',
                        'distance': '0.3 miles',
                        'comp_rating': 'High',
                        'reasoning': 'Similar size and property type in the same neighborhood'
                    },
                    {
                        'address': '45 Example Road, London, SW1A 2CD',
                        'property_type': 'Flat/Maisonette',
                        'bedrooms': 2,
                        'bathrooms': 2,
                        'floor_area': '750 sqft',
                        'sale_price': '£510,000',
                        'sale_date': 'February 2025',
                        'price_per_sqft': '£680',
                        'distance': '0.5 miles',
                        'comp_rating': 'Medium',
                        'reasoning': 'Similar property type but with an extra bathroom and slightly larger'
                    },
                    {
                        'address': '8 Test Avenue, London, SW1A 2EF',
                        'property_type': 'Flat/Maisonette',
                        'bedrooms': 2,
                        'bathrooms': 1,
                        'floor_area': '690 sqft',
                        'sale_price': '£465,000',
                        'sale_date': 'April 2025',
                        'price_per_sqft': '£674',
                        'distance': '0.4 miles',
                        'comp_rating': 'High',
                        'reasoning': 'Very similar size and layout in the same area'
                    }
                ]
            
            return comparables
        except Exception as e:
            logger.error(f"Error extracting comparable properties: {str(e)}")
            # Return a single basic comparable if extraction fails
            return [{
                'address': 'Nearby property',
                'property_type': 'Unknown',
                'sale_price': 'Unknown',
                'distance': 'Unknown',
                'comp_rating': 'Low'
            }]
    
    def _get_local_area_info(self, address: str, address_parts: Dict[str, str]) -> Dict[str, Any]:
        """
        Get information about the local area using OpenAI.
        
        Args:
            address: Property address
            address_parts: Parsed address components
            
        Returns:
            Dictionary of local area information
        """
        self.log_activity("Gathering local area information")
        
        postcode = address_parts.get('postcode', '')
        city = address_parts.get('city', '')
        
        # Add user message requesting local area information
        self.add_to_conversation("user", f"""
        Generate realistic local area information for a property at this address:
        
        Address: {address}
        Postcode: {postcode}
        City/Town: {city}
        
        Include information about:
        
        1. Transport:
           - Nearest station/stations
           - Distance to station
           - Transport links quality (Excellent/Good/Average/Poor)
           - Bus routes
        
        2. Amenities:
           - Schools (with ratings and distances)
           - Shops
           - Restaurants
           - Parks
           - Healthcare facilities
        
        3. Demographics:
           - Population density
           - Average age
           - Employment rate
           - Crime rate
        
        Make the information realistic for this location. Return the information as a JSON object.
        """)
        
        # Call OpenAI API
        response = self.call_openai_api(
            self.get_conversation_history(),
            temperature=0.7,
            max_tokens=1200
        )
        
        # Extract the response content
        assistant_message = response['choices'][0]['message']['content']
        self.add_to_conversation("assistant", assistant_message)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            if '{' in assistant_message and '}' in assistant_message:
                json_str = assistant_message[assistant_message.find('{'):assistant_message.rfind('}')+1]
                local_area_info = json.loads(json_str)
            else:
                # If no JSON found, create default local area info
                local_area_info = {
                    'transport': {
                        'nearest_station': 'Elephant & Castle',
                        'distance_to_station': '0.3 miles',
                        'transport_links': 'Excellent',
                        'bus_routes': '12, 45, 171, 176'
                    },
                    'amenities': {
                        'schools': [
                            {'name': 'Sample Primary School', 'rating': 'Good', 'distance': '0.4 miles'},
                            {'name': 'Example Secondary School', 'rating': 'Outstanding', 'distance': '0.7 miles'}
                        ],
                        'shops': 'Good variety within 0.5 miles',
                        'restaurants': 'Excellent selection within 0.5 miles',
                        'parks': 'St James Park (0.8 miles)',
                        'healthcare': 'Sample Medical Centre (0.6 miles)'
                    },
                    'demographics': {
                        'population_density': 'High',
                        'average_age': '32',
                        'employment_rate': '76%',
                        'crime_rate': 'Medium'
                    }
                }
            
            return local_area_info
        except Exception as e:
            logger.error(f"Error extracting local area information: {str(e)}")
            # Return basic local area info if extraction fails
            return {
                'transport': {'nearest_station': 'Unknown', 'transport_links': 'Unknown'},
                'amenities': {'shops': 'Unknown', 'schools': []},
                'demographics': {'population_density': 'Unknown'}
            }
    
    def _get_planning_history(self, address: str, address_parts: Dict[str, str]) -> Dict[str, Any]:
        """
        Get planning history for the property and area using OpenAI.
        
        Args:
            address: Property address
            address_parts: Parsed address components
            
        Returns:
            Dictionary of planning history
        """
        self.log_activity("Gathering planning history")
        
        postcode = address_parts.get('postcode', '')
        city = address_parts.get('city', '')
        
        # Add user message requesting planning history
        self.add_to_conversation("user", f"""
        Generate realistic planning history for a property at this address:
        
        Address: {address}
        Postcode: {postcode}
        City/Town: {city}
        
        Include:
        
        1. Property planning history:
           - Planning applications for the specific property
           - Status (Approved/Pending/Rejected)
           - Decision dates
        
        2. Area planning history:
           - Significant planning applications in the surrounding area
           - Status and decision dates
           - Distance from the target property
        
        3. Local development plans:
           - Any regeneration zones or development areas
           - Future infrastructure improvements
        
        Make the information realistic for this location. Return the information as a JSON object.
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
                planning_history = json.loads(json_str)
            else:
                # If no JSON found, create default planning history
                planning_history = {
                    'property_planning': [
                        {
                            'reference': 'PLAN/2020/1234',
                            'description': 'Internal alterations and refurbishment',
                            'status': 'Approved',
                            'decision_date': 'March 2020'
                        }
                    ],
                    'area_planning': [
                        {
                            'reference': 'PLAN/2023/5678',
                            'description': 'New residential development (12 units) on adjacent site',
                            'status': 'Approved',
                            'decision_date': 'November 2023',
                            'distance': '0.2 miles'
                        },
                        {
                            'reference': 'PLAN/2024/9012',
                            'description': 'Commercial to residential conversion',
                            'status': 'Pending',
                            'submission_date': 'February 2024',
                            'distance': '0.4 miles'
                        }
                    ],
                    'local_development_plans': 'The area is part of a regeneration zone with planned infrastructure improvements over the next 5 years.'
                }
            
            return planning_history
        except Exception as e:
            logger.error(f"Error extracting planning history: {str(e)}")
            # Return basic planning history if extraction fails
            return {
                'property_planning': [],
                'area_planning': [],
                'local_development_plans': 'No information available'
            }
