class ReportGenerationAgent:
    """
    Report Generation Agent - Creates the final property valuation report
    
    This agent creates the final report based on approved content, formats information
    according to the report template, generates visualizations and tables, and prepares
    the report for PDF export.
    """
    
    def __init__(self):
        self.name = "Report Generation Agent"
        self.role = "Report Creator"
        self.report_date = "May 29, 2025"
    
    def generate_report(self, approved_data):
        """
        Generate a property valuation report
        
        Args:
            approved_data (dict): Approved data from the Accessor Agent
            
        Returns:
            str: HTML report content
        """
        # Extract key data sections
        address = approved_data['address']
        executive_summary = approved_data['executive_summary']
        property_appraisal = approved_data['property_appraisal']
        feasibility_study = approved_data['feasibility_study']
        planning_analysis = approved_data['planning_analysis']
        risk_assessment = approved_data['risk_assessment']
        local_market_analysis = approved_data['local_market_analysis']
        conclusion = approved_data['conclusion']
        
        # Generate HTML report
        html = f"""
        <div class="report-container">
            <div class="report-header">
                <h1>BTR REPORT GENERATED {self.report_date}</h1>
                <h2>The BTR Potential of</h2>
                <h2 class="property-address">{address}</h2>
                <h2 class="btr-potential">is {conclusion['btr_potential']}.</h2>
            </div>
            
            <div class="disclaimer">
                <p><strong>Data Disclaimer:</strong> This report is generated based on available Land Registry, EPC ratings, and OpenStreetMap amenities
                data only. Rental estimates are based on typical yield calculations from property values, not actual rental statistics. Planning
                application data is not available, so growth potential is estimated from historical price trends.</p>
            </div>
            
            <div class="property-specs">
                <table class="specs-table">
                    <tr>
                        <th>Current Specs</th>
                        <th>Estimated Value</th>
                    </tr>
                    <tr>
                        <td>
                            <p>{property_appraisal['property_details']['bedrooms']} Bed / {property_appraisal['property_details']['bathrooms']} Bath</p>
                            <p>{property_appraisal['property_details']['floor_area']}</p>
                            <p>{property_appraisal['current_valuation']['formatted_price_per_sqft']} per sqft</p>
                        </td>
                        <td>
                            <p class="property-value">{property_appraisal['current_valuation']['formatted_value']}</p>
                        </td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>BTR SCORE</h2>
                <p class="note">Note: Some scores are based on base (default), efficiency (default), rental (estimated), growth (estimated).</p>
                <p>{conclusion['summary']}</p>
            </div>
            
            <div class="section">
                <h2>Investment Advice</h2>
                <p>{executive_summary['investment_strategy']}: {executive_summary['strategy_rationale']}.</p>
            </div>
            
            <div class="section">
                <h2>Market Commentary</h2>
                <p>{local_market_analysis['local_area_info']['transport']['transport_links']} transport links, which is a key driver for rental demand.</p>
                <p>Rental growth in {local_market_analysis['local_area_info']['transport']['nearest_station']} is stable at around {feasibility_study['rental_analysis']['formatted_rental_growth_rate']} annually, in line with London averages.</p>
                <p>Properties in this area have shown {local_market_analysis['market_data']['sales_demand']} demand from renters, particularly for {property_appraisal['property_details']['property_type']} properties.</p>
            </div>
            
            <div class="section">
                <h2>RENOVATION SCENARIOS</h2>
                <p>Explore renovation scenarios that could increase the value of this property:</p>
                
                <div class="scenarios">
                    {self._generate_scenario_html(feasibility_study['development_scenarios'][0])}
                    {self._generate_scenario_html(feasibility_study['development_scenarios'][1])}
                </div>
                
                <div class="renovation-advice">
                    <h3>Renovation Advice</h3>
                    <p>A {feasibility_study['development_scenarios'][0]['name'].lower()} focusing on quality finishes in the kitchen and bathroom would likely yield
                    the best returns. For this {property_appraisal['property_details']['property_type'].lower()}, emphasize modern styling to attract premium tenants.</p>
                </div>
            </div>
            
            <div class="section">
                <h2>RENTAL FORECAST</h2>
                <p class="note">Note: Rental values are estimated based on property value and London rental averages.</p>
                
                <table class="rental-table">
                    <tr>
                        <th>Year</th>
                        <th>Monthly Rent</th>
                        <th>Annual Rent</th>
                        <th>Growth</th>
                    </tr>
                    {self._generate_rental_forecast_rows(feasibility_study['rental_analysis']['rental_forecast'])}
                </table>
            </div>
            
            <div class="section">
                <h2>COMPARABLE PROPERTIES</h2>
                <p>{property_appraisal['comparable_analysis']['analysis']}</p>
                
                <table class="comparables-table">
                    <tr>
                        <th>Address</th>
                        <th>Sale Price</th>
                        <th>Property Type</th>
                        <th>Size</th>
                        <th>Price per sqft</th>
                        <th>Comp Rating</th>
                    </tr>
                    {self._generate_comparables_rows(property_appraisal['comparable_analysis']['comparables'])}
                </table>
            </div>
            
            <div class="section">
                <h2>PLANNING ASSESSMENT</h2>
                <p><strong>Current Use Class:</strong> {planning_analysis['current_use_class']}</p>
                
                <h3>Opportunities</h3>
                <ul>
                    {self._generate_list_items(planning_analysis['opportunities'])}
                </ul>
                
                <h3>Constraints</h3>
                <ul>
                    {self._generate_list_items(planning_analysis['constraints'])}
                </ul>
                
                <h3>Recommendations</h3>
                <ul>
                    {self._generate_list_items(planning_analysis['recommendations'])}
                </ul>
            </div>
            
            <div class="section">
                <h2>RISK ASSESSMENT</h2>
                <p><strong>Overall Risk Profile:</strong> {risk_assessment['risk_profile']}</p>
                
                <table class="risks-table">
                    <tr>
                        <th>Category</th>
                        <th>Description</th>
                        <th>Impact</th>
                        <th>Mitigation</th>
                    </tr>
                    {self._generate_risks_rows(risk_assessment['identified_risks'])}
                </table>
            </div>
            
            <div class="section conclusion">
                <h2>CONCLUSION</h2>
                <p>{conclusion['recommendation']}</p>
            </div>
            
            <div class="report-footer">
                <p>Report generated by Property Valuation App on {self.report_date}</p>
                <p>© 2025 Property Valuation App</p>
            </div>
        </div>
        """
        
        return html
    
    def _generate_scenario_html(self, scenario):
        """Generate HTML for a development scenario"""
        return f"""
        <div class="scenario">
            <h3>{scenario['name']}</h3>
            <p><strong>Cost:</strong> {scenario['formatted_cost']}</p>
            <p><strong>New Value:</strong> {scenario['formatted_new_value']}</p>
            <p><strong>Description:</strong> {scenario['description']}</p>
            <p><strong>Value uplift:</strong> {scenario['formatted_value_uplift']} ({scenario['value_uplift_percentage']})</p>
            <p><strong>ROI:</strong> {scenario['formatted_roi']}</p>
        </div>
        """
    
    def _generate_rental_forecast_rows(self, forecast):
        """Generate HTML table rows for rental forecast"""
        rows = ""
        for year_data in forecast:
            rows += f"""
            <tr>
                <td>{year_data['year']}</td>
                <td>{year_data['formatted_monthly_rent']}</td>
                <td>{year_data['formatted_annual_rent']}</td>
                <td>{year_data['growth']}</td>
            </tr>
            """
        return rows
    
    def _generate_comparables_rows(self, comparables):
        """Generate HTML table rows for comparable properties"""
        rows = ""
        for comp in comparables:
            rows += f"""
            <tr>
                <td>{comp['address']}</td>
                <td>{comp['sale_price']}</td>
                <td>{comp['property_type']}</td>
                <td>{comp['floor_area']}</td>
                <td>{comp['price_per_sqft']}</td>
                <td>{comp['comp_rating']}</td>
            </tr>
            """
        return rows
    
    def _generate_risks_rows(self, risks):
        """Generate HTML table rows for risks"""
        rows = ""
        for risk in risks:
            rows += f"""
            <tr>
                <td>{risk['category']}</td>
                <td>{risk['description']}</td>
                <td>{risk['impact']}</td>
                <td>{risk['mitigation']}</td>
            </tr>
            """
        return rows
    
    def _generate_list_items(self, items):
        """Generate HTML list items"""
        list_items = ""
        for item in items:
            list_items += f"<li>{item}</li>\n"
        return list_items
