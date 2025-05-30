class EvaluationAgent:
    """
    Evaluation Agent - Analyzes property data and performs valuations
    
    This agent analyzes data collected by the Research Agent, compares and validates
    information from multiple sources, performs calculations for valuations, ROI, and
    development scenarios, and prepares structured data for report generation.
    """
    
    def __init__(self):
        self.name = "Evaluation Agent"
        self.role = "Data Analyzer"
        self.refurbishment_cost_benchmarks = {
            'light': {'cost_per_sqft': 70, 'description': 'Painting, decorating, minor works'},
            'medium': {'cost_per_sqft': 180, 'description': 'New kitchen, bathroom, and cosmetic work'},
            'heavy': {'cost_per_sqft': 225, 'description': 'Structural changes, extensions, full renovation'},
            'hmo': {'cost_per_room': 30000, 'description': 'Conversion to HMO (House in Multiple Occupation)'}
        }
    
    def evaluate_property(self, property_data):
        """
        Evaluate property data and generate valuation analysis
        
        Args:
            property_data (dict): Data collected by the Research Agent
            
        Returns:
            dict: Evaluation results including valuations and scenarios
        """
        # Extract key property details
        property_details = property_data['property_details']
        market_data = property_data['market_data']
        comparables = property_data['comparable_properties']
        local_info = property_data['local_area_info']
        
        # Calculate current valuation
        current_valuation = self._calculate_valuation(property_details, market_data, comparables)
        
        # Generate development scenarios
        development_scenarios = self._generate_development_scenarios(property_details, current_valuation)
        
        # Calculate rental income and yield
        rental_analysis = self._calculate_rental_analysis(property_details, market_data, current_valuation)
        
        # Assess planning opportunities
        planning_assessment = self._assess_planning_opportunities(property_data)
        
        # Perform risk assessment
        risk_assessment = self._assess_risks(property_data)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            property_details, 
            current_valuation, 
            development_scenarios, 
            rental_analysis,
            planning_assessment,
            risk_assessment
        )
        
        # Compile evaluation results
        evaluation_results = {
            'address': property_data['address'],
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
            'conclusion': self._generate_conclusion(
                property_details,
                current_valuation,
                development_scenarios,
                rental_analysis
            )
        }
        
        return evaluation_results
    
    def _calculate_valuation(self, property_details, market_data, comparables):
        """Calculate the current property valuation"""
        # Extract property size
        size_str = property_details['floor_area']
        size = int(size_str.split(' ')[0])  # Extract numeric part
        
        # Extract price per sqft
        price_per_sqft_str = market_data['average_price_per_sqft']
        price_per_sqft = int(price_per_sqft_str.replace('£', ''))
        
        # Calculate base valuation
        base_valuation = size * price_per_sqft
        
        # Adjust based on comparables
        comparable_adjustment = 0
        if comparables:
            comparable_values = []
            for comp in comparables:
                if comp['comp_rating'] == 'High':
                    weight = 0.5
                elif comp['comp_rating'] == 'Medium':
                    weight = 0.3
                else:
                    weight = 0.2
                
                comp_price = int(comp['sale_price'].replace('£', '').replace(',', ''))
                comparable_values.append(comp_price * weight)
            
            weighted_comp_value = sum(comparable_values) / len(comparable_values)
            comparable_adjustment = (weighted_comp_value - base_valuation) * 0.3
        
        # Final valuation
        final_valuation = round(base_valuation + comparable_adjustment, -3)  # Round to nearest thousand
        
        return {
            'value': final_valuation,
            'formatted_value': f'£{final_valuation:,}',
            'price_per_sqft': price_per_sqft,
            'formatted_price_per_sqft': f'£{price_per_sqft}',
            'valuation_date': 'May 29, 2025',
            'confidence_level': 'Medium',
            'methodology': 'Comparable analysis with market data adjustment'
        }
    
    def _generate_development_scenarios(self, property_details, current_valuation):
        """Generate development scenarios for the property"""
        # Extract property size
        size_str = property_details['floor_area']
        size = int(size_str.split(' ')[0])  # Extract numeric part
        
        # Current value
        current_value = current_valuation['value']
        
        # Calculate scenarios
        scenarios = []
        
        # Cosmetic Refurbishment
        light_cost = size * self.refurbishment_cost_benchmarks['light']['cost_per_sqft']
        light_value_uplift = current_value * 0.10  # 10% increase
        light_new_value = current_value + light_value_uplift
        light_roi = (light_value_uplift / light_cost) * 100
        
        scenarios.append({
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
        })
        
        # Medium Refurbishment
        medium_cost = size * self.refurbishment_cost_benchmarks['medium']['cost_per_sqft']
        medium_value_uplift = current_value * 0.15  # 15% increase
        medium_new_value = current_value + medium_value_uplift
        medium_roi = (medium_value_uplift / medium_cost) * 100
        
        scenarios.append({
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
        })
        
        return scenarios
    
    def _calculate_rental_analysis(self, property_details, market_data, current_valuation):
        """Calculate rental income and yield"""
        # Current value
        current_value = current_valuation['value']
        
        # Calculate monthly rental income based on yield
        yield_percentage = float(market_data['average_rental_yield'].replace('%', '')) / 100
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
            'rental_demand': market_data['rental_demand'],
            'rental_forecast': rental_forecast,
            'rental_growth_rate': rental_growth_rate,
            'formatted_rental_growth_rate': f'{rental_growth_rate*100:.1f}%'
        }
    
    def _assess_planning_opportunities(self, property_data):
        """Assess planning opportunities for the property"""
        property_details = property_data['property_details']
        planning_history = property_data['planning_history']
        
        # Determine current use class
        current_use_class = property_details.get('current_use_class', 'Unknown')
        
        # Analyze planning history
        property_planning = planning_history.get('property_planning', [])
        area_planning = planning_history.get('area_planning', [])
        
        # Determine planning opportunities
        opportunities = []
        constraints = []
        
        # Add default opportunities and constraints
        opportunities.append('Potential for internal reconfiguration within existing use class')
        
        if current_use_class == 'C3 (Residential)':
            constraints.append('Change of use from residential may require planning permission')
        
        # Add area-specific opportunities based on local development plans
        local_development_plans = planning_history.get('local_development_plans', '')
        if 'regeneration zone' in local_development_plans.lower():
            opportunities.append('Located in regeneration zone with potential for enhanced value growth')
        
        return {
            'current_use_class': current_use_class,
            'planning_history': {
                'property': property_planning,
                'area': area_planning
            },
            'opportunities': opportunities,
            'constraints': constraints,
            'recommendations': [
                'Consult with local planning authority for specific guidance',
                'Consider pre-application advice for major alterations',
                'Review local development plan for future area changes'
            ]
        }
    
    def _assess_risks(self, property_data):
        """Assess risks associated with the property investment"""
        property_details = property_data['property_details']
        market_data = property_data['market_data']
        
        # Identify risks
        risks = []
        
        # Market risks
        if market_data['market_sentiment'] != 'Strong':
            risks.append({
                'category': 'Market',
                'description': 'Market sentiment is not strong, which may affect future value growth',
                'impact': 'Medium',
                'mitigation': 'Consider longer-term hold strategy to ride out market fluctuations'
            })
        
        # Property-specific risks
        if property_details['tenure'] == 'Leasehold':
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
    
    def _analyze_comparables(self, comparables):
        """Analyze comparable properties"""
        if not comparables:
            return {
                'count': 0,
                'analysis': 'No comparable properties available for analysis'
            }
        
        # Calculate average values
        total_price = 0
        total_price_per_sqft = 0
        
        for comp in comparables:
            price = int(comp['sale_price'].replace('£', '').replace(',', ''))
            price_per_sqft = int(comp['price_per_sqft'].replace('£', ''))
            
            total_price += price
            total_price_per_sqft += price_per_sqft
        
        avg_price = total_price / len(comparables)
        avg_price_per_sqft = total_price_per_sqft / len(comparables)
        
        return {
            'count': len(comparables),
            'comparables': comparables,
            'average_price': avg_price,
            'formatted_average_price': f'£{avg_price:,.0f}',
            'average_price_per_sqft': avg_price_per_sqft,
            'formatted_average_price_per_sqft': f'£{avg_price_per_sqft:.0f}',
            'analysis': f'Based on {len(comparables)} comparable properties within 0.5 miles'
        }
    
    def _generate_executive_summary(self, property_details, current_valuation, 
                                   development_scenarios, rental_analysis,
                                   planning_assessment, risk_assessment):
        """Generate an executive summary for the property"""
        # Determine best development scenario based on ROI
        best_scenario = max(development_scenarios, key=lambda x: x['roi'])
        
        # Determine investment strategy
        if rental_analysis['gross_yield'] > 0.05:  # 5% yield
            if best_scenario['roi'] > 100:  # High ROI on refurbishment
                strategy = 'Refurbish to let'
                rationale = 'High rental yield combined with good refurbishment returns'
            else:
                strategy = 'Buy to let'
                rationale = 'Strong rental yield in current condition'
        else:
            if best_scenario['roi'] > 50:  # Decent ROI on refurbishment
                strategy = 'Refurbish to sell'
                rationale = 'Moderate rental yield but good potential for capital growth after refurbishment'
            else:
                strategy = 'Hold for capital growth'
                rationale = 'Limited immediate returns but potential for long-term appreciation'
        
        return {
            'property_type': property_details['property_type'],
            'current_valuation': current_valuation['formatted_value'],
            'best_development_scenario': {
                'name': best_scenario['name'],
                'cost': best_scenario['formatted_cost'],
                'new_value': best_scenario['formatted_new_value'],
                'roi': best_scenario['formatted_roi']
            },
            'rental_income': rental_analysis['formatted_monthly_rental_income'],
            'gross_yield': rental_analysis['formatted_gross_yield'],
            'planning_opportunities': planning_assessment['opportunities'],
            'planning_constraints': planning_assessment['constraints'],
            'risk_profile': risk_assessment['risk_profile'],
            'investment_strategy': strategy,
            'strategy_rationale': rationale
        }
    
    def _generate_conclusion(self, property_details, current_valuation, 
                            development_scenarios, rental_analysis):
        """Generate a conclusion for the property report"""
        # Determine best development scenario based on ROI
        best_scenario = max(development_scenarios, key=lambda x: x['roi'])
        
        # Generate conclusion text
        if rental_analysis['gross_yield'] > 0.15:  # Very high yield
            btr_potential = 'excellent'
        elif rental_analysis['gross_yield'] > 0.08:  # Good yield
            btr_potential = 'good'
        elif rental_analysis['gross_yield'] > 0.05:  # Average yield
            btr_potential = 'moderate'
        else:
            btr_potential = 'poor'
        
        return {
            'btr_potential': btr_potential,
            'summary': f"This {property_details['floor_area']} {property_details['property_type']} property has {btr_potential} BTR potential. The estimated value is {current_valuation['formatted_value']} with a potential monthly rental income of {rental_analysis['formatted_monthly_rental_income']}, giving a gross yield of {rental_analysis['formatted_gross_yield']}.",
            'recommendation': f"The recommended strategy is to {best_scenario['name'].lower()} with an estimated cost of {best_scenario['formatted_cost']}, potentially increasing the property value to {best_scenario['formatted_new_value']} (ROI: {best_scenario['formatted_roi']})."
        }
