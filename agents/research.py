class ResearchAgent:
    """
    Research Agent - Gathers property information from various sources
    
    This agent searches the internet for property information, gathers data from
    reliable sources (Land Registry, VOA, local council records), collects market
    data, comparable properties, and local area information, and provides raw data
    to the Evaluation Agent.
    """
    
    def __init__(self):
        self.name = "Research Agent"
        self.role = "Data Gatherer"
        self.sources = [
            "Land Registry",
            "Valuation Office Agency (VOA)",
            "Local council records",
            "Rightmove",
            "Zoopla",
            "OpenStreetMap"
        ]
    
    def gather_property_data(self, address):
        """
        Gather property data from various sources
        
        Args:
            address (str): The UK property address
            
        Returns:
            dict: Collected property data
        """
        # In a real implementation, this would make API calls and web searches
        # For the prototype, we'll simulate the data gathering process
        
        # Parse the address (in a real implementation, this would use a UK address parsing API)
        address_parts = self._parse_address(address)
        
        # Simulate gathering property data
        property_data = {
            'address': address,
            'parsed_address': address_parts,
            'property_details': self._get_property_details(address_parts),
            'market_data': self._get_market_data(address_parts),
            'comparable_properties': self._get_comparable_properties(address_parts),
            'local_area_info': self._get_local_area_info(address_parts),
            'planning_history': self._get_planning_history(address_parts),
            'sources': self.sources
        }
        
        return property_data
    
    def _parse_address(self, address):
        """Parse a UK address into its components"""
        # In a real implementation, this would use a UK address parsing API
        # For the prototype, we'll do a simple parse
        
        # Example address: "10 Downing Street, London, SW1A 2AA"
        parts = address.split(',')
        
        address_parts = {
            'street_address': parts[0].strip() if len(parts) > 0 else '',
            'city': parts[1].strip() if len(parts) > 1 else '',
            'postcode': parts[2].strip() if len(parts) > 2 else ''
        }
        
        return address_parts
    
    def _get_property_details(self, address_parts):
        """Get property details from Land Registry and VOA"""
        # Simulate property details
        return {
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
    
    def _get_market_data(self, address_parts):
        """Get market data for the area"""
        # Simulate market data
        return {
            'average_price_per_sqft': '£689',
            'price_trend_1yr': '+3.2%',
            'price_trend_5yr': '+12.8%',
            'average_rental_yield': '4.5%',
            'rental_demand': 'High',
            'sales_demand': 'Medium',
            'average_time_on_market': '45 days',
            'market_sentiment': 'Stable'
        }
    
    def _get_comparable_properties(self, address_parts):
        """Get comparable properties in the area"""
        # Simulate comparable properties
        return [
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
                'comp_rating': 'High'
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
                'comp_rating': 'Medium'
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
                'comp_rating': 'High'
            }
        ]
    
    def _get_local_area_info(self, address_parts):
        """Get information about the local area"""
        # Simulate local area information
        return {
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
    
    def _get_planning_history(self, address_parts):
        """Get planning history for the property and area"""
        # Simulate planning history
        return {
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
