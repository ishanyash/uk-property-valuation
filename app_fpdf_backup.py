from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import uuid
from datetime import datetime
import tempfile
from fpdf import FPDF

# Import agent modules
from agents.accessor import AccessorAgent
from agents.research import ResearchAgent
from agents.evaluation import EvaluationAgent
from agents.report_generator import ReportGenerationAgent

app = Flask(__name__)

# Store reports temporarily in memory
reports = {}

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/validate-address', methods=['POST'])
def validate_address():
    """Validate a UK address"""
    address = request.json.get('address', '')
    
    # In a real implementation, this would use a UK address validation API
    # For the prototype, we'll do basic validation
    if not address or len(address) < 10:
        return jsonify({'valid': False, 'message': 'Please enter a complete UK address'})
    
    # Simple validation passed
    return jsonify({'valid': True, 'formatted_address': address})

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """Generate a property valuation report using the agent system"""
    address = request.json.get('address', '')
    
    # Generate a unique ID for this report
    report_id = str(uuid.uuid4())
    
    # Initialize the agent system
    accessor = AccessorAgent()
    research = ResearchAgent()
    evaluation = EvaluationAgent()
    report_generator = ReportGenerationAgent()
    
    # Execute the agent workflow
    # 1. Research agent gathers data
    property_data = research.gather_property_data(address)
    
    # 2. Evaluation agent analyzes the data
    evaluation_results = evaluation.evaluate_property(property_data)
    
    # 3. Accessor agent reviews and approves
    approved_data = accessor.review_and_approve(evaluation_results)
    
    # 4. Report generator creates the report
    report_html = report_generator.generate_report(approved_data)
    
    # Store the report
    reports[report_id] = {
        'address': address,
        'html': report_html,
        'date': datetime.now().strftime('%B %d, %Y'),
        'data': approved_data
    }
    
    return jsonify({
        'success': True,
        'report_id': report_id
    })

@app.route('/view-report/<report_id>')
def view_report(report_id):
    """View a generated report"""
    if report_id not in reports:
        return render_template('error.html', message='Report not found')
    
    report = reports[report_id]
    return render_template('report.html', report=report)

@app.route('/export-pdf/<report_id>')
def export_pdf(report_id):
    """Export a report as PDF using FPDF2 instead of WeasyPrint"""
    if report_id not in reports:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    report = reports[report_id]
    approved_data = report['data']
    
    # Create a PDF using FPDF2
    pdf = PDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Generate the PDF content
    generate_pdf_content(pdf, approved_data)
    
    # Create a temporary file for the PDF
    fd, path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    
    # Save the PDF
    pdf.output(path)
    
    # Send the file
    return send_file(path, as_attachment=True, 
                    download_name=f"Property_Valuation_{report_id[:8]}.pdf",
                    mimetype='application/pdf')

class PDF(FPDF):
    """Custom PDF class with header and footer"""
    def header(self):
        # Set font
        self.set_font('Arial', 'B', 12)
        # Title
        self.cell(0, 10, 'BTR REPORT GENERATED ' + datetime.now().strftime('%B %d, %Y').upper(), 0, 1, 'C')
        # Line break
        self.ln(5)
        
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_pdf_content(pdf, data):
    """Generate PDF content from the approved data"""
    # Extract key data sections
    address = data['address']
    executive_summary = data['executive_summary']
    property_appraisal = data['property_appraisal']
    feasibility_study = data['feasibility_study']
    planning_analysis = data['planning_analysis']
    risk_assessment = data['risk_assessment']
    local_market_analysis = data['local_market_analysis']
    conclusion = data['conclusion']
    
    # Set font
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    pdf.cell(0, 10, 'The BTR Potential of', 0, 1, 'C')
    pdf.cell(0, 10, address, 0, 1, 'C')
    pdf.cell(0, 10, f"is {conclusion['btr_potential']}.", 0, 1, 'C')
    
    # Disclaimer
    pdf.set_font('Arial', '', 8)
    pdf.ln(5)
    pdf.multi_cell(0, 5, 'Data Disclaimer: This report is generated based on available Land Registry, EPC ratings, and OpenStreetMap amenities data only. Rental estimates are based on typical yield calculations from property values, not actual rental statistics. Planning application data is not available, so growth potential is estimated from historical price trends.')
    
    # Property Specs
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Current Specs', 1, 1, 'C', fill=True)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(95, 10, f"{property_appraisal['property_details']['bedrooms']} Bed / {property_appraisal['property_details']['bathrooms']} Bath", 1, 0)
    pdf.cell(95, 10, property_appraisal['current_valuation']['formatted_value'], 1, 1, 'R')
    
    pdf.cell(95, 10, property_appraisal['property_details']['floor_area'], 1, 0)
    pdf.cell(95, 10, '', 1, 1)
    
    pdf.cell(95, 10, property_appraisal['current_valuation']['formatted_price_per_sqft'] + ' per sqft', 1, 0)
    pdf.cell(95, 10, '', 1, 1)
    
    # BTR Score
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'BTR SCORE', 0, 1)
    
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 5, 'Note: Some scores are based on base (default), efficiency (default), rental (estimated), growth (estimated).', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.ln(5)
    pdf.multi_cell(0, 5, conclusion['summary'])
    
    # Investment Advice
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Investment Advice', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"{executive_summary['investment_strategy']}: {executive_summary['strategy_rationale']}.")
    
    # Market Commentary
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Market Commentary', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"{local_market_analysis['local_area_info']['transport']['transport_links']} transport links, which is a key driver for rental demand.")
    pdf.ln(3)
    pdf.multi_cell(0, 5, f"Rental growth in {local_market_analysis['local_area_info']['transport']['nearest_station']} is stable at around {feasibility_study['rental_analysis']['formatted_rental_growth_rate']} annually, in line with London averages.")
    pdf.ln(3)
    pdf.multi_cell(0, 5, f"Properties in this area have shown {local_market_analysis['market_data']['sales_demand']} demand from renters, particularly for {property_appraisal['property_details']['property_type']} properties.")
    
    # Add a new page for renovation scenarios
    pdf.add_page()
    
    # Renovation Scenarios
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'RENOVATION SCENARIOS', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, 'Explore renovation scenarios that could increase the value of this property:', 0, 1)
    
    # Scenario 1
    pdf.ln(5)
    scenario1 = feasibility_study['development_scenarios'][0]
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, scenario1['name'], 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 6, 'Cost:', 0, 0)
    pdf.cell(0, 6, scenario1['formatted_cost'], 0, 1)
    
    pdf.cell(50, 6, 'New Value:', 0, 0)
    pdf.cell(0, 6, scenario1['formatted_new_value'], 0, 1)
    
    pdf.cell(50, 6, 'Description:', 0, 0)
    pdf.cell(0, 6, scenario1['description'], 0, 1)
    
    pdf.cell(50, 6, 'Value uplift:', 0, 0)
    pdf.cell(0, 6, f"{scenario1['formatted_value_uplift']} ({scenario1['value_uplift_percentage']})", 0, 1)
    
    pdf.cell(50, 6, 'ROI:', 0, 0)
    pdf.cell(0, 6, scenario1['formatted_roi'], 0, 1)
    
    # Scenario 2
    pdf.ln(5)
    scenario2 = feasibility_study['development_scenarios'][1]
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, scenario2['name'], 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 6, 'Cost:', 0, 0)
    pdf.cell(0, 6, scenario2['formatted_cost'], 0, 1)
    
    pdf.cell(50, 6, 'New Value:', 0, 0)
    pdf.cell(0, 6, scenario2['formatted_new_value'], 0, 1)
    
    pdf.cell(50, 6, 'Description:', 0, 0)
    pdf.cell(0, 6, scenario2['description'], 0, 1)
    
    pdf.cell(50, 6, 'Value uplift:', 0, 0)
    pdf.cell(0, 6, f"{scenario2['formatted_value_uplift']} ({scenario2['value_uplift_percentage']})", 0, 1)
    
    pdf.cell(50, 6, 'ROI:', 0, 0)
    pdf.cell(0, 6, scenario2['formatted_roi'], 0, 1)
    
    # Renovation Advice
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Renovation Advice', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, f"A {feasibility_study['development_scenarios'][0]['name'].lower()} focusing on quality finishes in the kitchen and bathroom would likely yield the best returns. For this {property_appraisal['property_details']['property_type'].lower()}, emphasize modern styling to attract premium tenants.")
    
    # Rental Forecast
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'RENTAL FORECAST', 0, 1)
    
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 5, 'Note: Rental values are estimated based on property value and London rental averages.', 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, 'Year', 1, 0, 'C')
    pdf.cell(50, 8, 'Monthly Rent', 1, 0, 'C')
    pdf.cell(50, 8, 'Annual Rent', 1, 0, 'C')
    pdf.cell(40, 8, 'Growth', 1, 1, 'C')
    
    pdf.set_font('Arial', '', 10)
    for forecast in feasibility_study['rental_analysis']['rental_forecast']:
        pdf.cell(40, 8, forecast['year'], 1, 0, 'C')
        pdf.cell(50, 8, forecast['formatted_monthly_rent'], 1, 0, 'C')
        pdf.cell(50, 8, forecast['formatted_annual_rent'], 1, 0, 'C')
        pdf.cell(40, 8, forecast['growth'], 1, 1, 'C')
    
    # Add a new page for comparable properties
    pdf.add_page()
    
    # Comparable Properties
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'COMPARABLE PROPERTIES', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, property_appraisal['comparable_analysis']['analysis'], 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(70, 8, 'Address', 1, 0, 'C')
    pdf.cell(30, 8, 'Sale Price', 1, 0, 'C')
    pdf.cell(30, 8, 'Property Type', 1, 0, 'C')
    pdf.cell(30, 8, 'Size', 1, 0, 'C')
    pdf.cell(30, 8, 'Comp Rating', 1, 1, 'C')
    
    pdf.set_font('Arial', '', 9)
    for comp in property_appraisal['comparable_analysis']['comparables']:
        pdf.cell(70, 8, comp['address'][:30], 1, 0)
        pdf.cell(30, 8, comp['sale_price'], 1, 0, 'C')
        pdf.cell(30, 8, comp['property_type'][:10], 1, 0, 'C')
        pdf.cell(30, 8, comp['floor_area'], 1, 0, 'C')
        pdf.cell(30, 8, comp['comp_rating'], 1, 1, 'C')
    
    # Planning Assessment
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'PLANNING ASSESSMENT', 0, 1)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 6, 'Current Use Class:', 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, planning_analysis['current_use_class'], 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Opportunities', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    for opportunity in planning_analysis['opportunities']:
        pdf.cell(10, 6, '•', 0, 0)
        pdf.multi_cell(0, 6, opportunity)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Constraints', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    for constraint in planning_analysis['constraints']:
        pdf.cell(10, 6, '•', 0, 0)
        pdf.multi_cell(0, 6, constraint)
    
    # Risk Assessment
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'RISK ASSESSMENT', 0, 1)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 6, 'Overall Risk Profile:', 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, risk_assessment['risk_profile'], 0, 1)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(30, 8, 'Category', 1, 0, 'C')
    pdf.cell(80, 8, 'Description', 1, 0, 'C')
    pdf.cell(30, 8, 'Impact', 1, 0, 'C')
    pdf.cell(50, 8, 'Mitigation', 1, 1, 'C')
    
    pdf.set_font('Arial', '', 9)
    for risk in risk_assessment['identified_risks']:
        # Calculate height needed for description (which might be longer)
        description_lines = len(risk['description']) // 40 + 1
        mitigation_lines = len(risk['mitigation']) // 25 + 1
        line_height = max(description_lines, mitigation_lines) * 6
        
        pdf.cell(30, line_height, risk['category'], 1, 0)
        pdf.multi_cell(80, line_height / description_lines, risk['description'], 1, 0)
        pdf.set_xy(pdf.get_x() + 110, pdf.get_y() - line_height)
        pdf.cell(30, line_height, risk['impact'], 1, 0, 'C')
        pdf.multi_cell(50, line_height / mitigation_lines, risk['mitigation'], 1, 1)
    
    # Conclusion
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'CONCLUSION', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, conclusion['recommendation'])
    
    # Footer
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 5, f"Report generated by Property Valuation App on {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
    pdf.cell(0, 5, "© 2025 Property Valuation App", 0, 1, 'C')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
