import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file, session
import tempfile
import uuid
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import agent modules
from agents.base_agent import BaseAgent, AgentOrchestrator
from agents.openai_research_agent import ResearchAgent
from agents.openai_evaluation_agent import EvaluationAgent
from agents.openai_accessor_agent import AccessorAgent
from agents.openai_report_generator import ReportGenerationAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", str(uuid.uuid4()))

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    logger.warning("OpenAI API key not found in environment variables. Please add it to your .env file.")

# Store reports temporarily in memory
reports = {}

# Initialize agent orchestrator
orchestrator = AgentOrchestrator()
orchestrator.register_agent("research", ResearchAgent())
orchestrator.register_agent("evaluation", EvaluationAgent())
orchestrator.register_agent("accessor", AccessorAgent())
orchestrator.register_agent("report_generator", ReportGenerationAgent())

@app.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@app.route('/validate-address', methods=['POST'])
def validate_address():
    """Validate a UK address"""
    data = request.json
    address = data.get('address', '')
    
    if not address or len(address) < 10:
        return jsonify({'valid': False, 'message': 'Please enter a complete UK address'})
    
    # Check for UK postcode pattern (basic validation)
    import re
    uk_postcode = re.search(r'[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}', address, re.IGNORECASE)
    
    if not uk_postcode:
        return jsonify({
            'valid': True,  # Still allow it but with a warning
            'warning': 'Address may not contain a valid UK postcode',
            'formatted_address': address
        })
    
    return jsonify({'valid': True, 'formatted_address': address})

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """Generate a property valuation report using the agent system"""
    data = request.json
    address = data.get('address', '')
    
    if not address:
        return jsonify({'success': False, 'message': 'Address is required'})
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({
            'success': False, 
            'message': 'OpenAI API key not found. Please add it to your .env file.'
        })
    
    try:
        # Generate a unique ID for this report
        report_id = str(uuid.uuid4())
        
        # Store initial status
        reports[report_id] = {
            'address': address,
            'status': 'processing',
            'progress': 0,
            'message': 'Starting research...',
            'timestamp': datetime.now().isoformat()
        }
        
        # Start the agent workflow in a background thread
        import threading
        thread = threading.Thread(target=process_report, args=(report_id, address))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'message': 'Report generation started'
        })
    
    except Exception as e:
        logger.error(f"Error starting report generation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error: {str(e)}"
        })

def process_report(report_id, address):
    """Process the report generation in the background"""
    try:
        # Update status
        reports[report_id]['status'] = 'researching'
        reports[report_id]['progress'] = 10
        reports[report_id]['message'] = 'Researching property data...'
        
        # 1. Research agent gathers data
        research_agent = orchestrator.agents['research']
        property_data = research_agent.process({'address': address})
        
        # Update status
        reports[report_id]['status'] = 'evaluating'
        reports[report_id]['progress'] = 30
        reports[report_id]['message'] = 'Evaluating property data...'
        
        # 2. Evaluation agent analyzes the data
        evaluation_agent = orchestrator.agents['evaluation']
        evaluation_results = evaluation_agent.process(property_data)
        
        # Update status
        reports[report_id]['status'] = 'reviewing'
        reports[report_id]['progress'] = 50
        reports[report_id]['message'] = 'Reviewing and approving data...'
        
        # 3. Accessor agent reviews and approves
        accessor_agent = orchestrator.agents['accessor']
        approved_data = accessor_agent.process({
            'address': address,
            'property_data': property_data,
            'evaluation_results': evaluation_results
        })
        
        # Update status
        reports[report_id]['status'] = 'generating'
        reports[report_id]['progress'] = 70
        reports[report_id]['message'] = 'Generating report...'
        
        # 4. Report generator creates the report
        report_generator = orchestrator.agents['report_generator']
        report_result = report_generator.process(approved_data)
        
        # Update status
        reports[report_id]['status'] = 'complete'
        reports[report_id]['progress'] = 100
        reports[report_id]['message'] = 'Report generation complete'
        reports[report_id]['html'] = report_result['report_html']
        reports[report_id]['content'] = report_result['report_content']
        reports[report_id]['date'] = datetime.now().strftime('%B %d, %Y')
        reports[report_id]['data'] = approved_data
        
    except Exception as e:
        logger.error(f"Error processing report: {str(e)}")
        reports[report_id]['status'] = 'error'
        reports[report_id]['message'] = f"Error: {str(e)}"

@app.route('/report-status/<report_id>')
def report_status(report_id):
    """Get the status of a report generation process"""
    if report_id not in reports:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    report = reports[report_id]
    return jsonify({
        'success': True,
        'status': report.get('status', 'unknown'),
        'progress': report.get('progress', 0),
        'message': report.get('message', ''),
        'complete': report.get('status') == 'complete'
    })

@app.route('/view-report/<report_id>')
def view_report(report_id):
    """View a generated report"""
    if report_id not in reports:
        return render_template('error.html', message='Report not found')
    
    report = reports[report_id]
    
    if report.get('status') != 'complete':
        return render_template('error.html', 
                              message=f"Report is not ready yet. Status: {report.get('status', 'processing')}")
    
    return render_template('report.html', report=report)

@app.route('/export-pdf/<report_id>')
def export_pdf(report_id):
    """Export a report as PDF using FPDF2"""
    if report_id not in reports:
        return jsonify({'success': False, 'message': 'Report not found'})
    
    report = reports[report_id]
    
    if report.get('status') != 'complete':
        return jsonify({
            'success': False, 
            'message': f"Report is not ready yet. Status: {report.get('status', 'processing')}"
        })
    
    try:
        from fpdf import FPDF
        
        # Create a PDF
        pdf = PDF('P', 'mm', 'A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Get report content
        report_content = report.get('content', {})
        
        # Generate the PDF content
        generate_pdf_content(pdf, report_content)
        
        # Create a temporary file for the PDF
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        # Save the PDF
        pdf.output(path)
        
        # Send the file
        return send_file(path, as_attachment=True, 
                        download_name=f"Property_Valuation_{report_id[:8]}.pdf",
                        mimetype='application/pdf')
    
    except Exception as e:
        logger.error(f"Error exporting PDF: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error exporting PDF: {str(e)}"
        })

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

def generate_pdf_content(pdf, report_content):
    """Generate PDF content from the report content"""
    # Extract key sections
    address = report_content.get('address', '')
    title = report_content.get('title', f"BTR Report: {address}")
    executive_summary = report_content.get('executive_summary', {})
    property_appraisal = report_content.get('property_appraisal', {})
    feasibility_study = report_content.get('feasibility_study', {})
    planning_analysis = report_content.get('planning_analysis', {})
    risk_assessment = report_content.get('risk_assessment', {})
    local_market_analysis = report_content.get('local_market_analysis', {})
    conclusion = report_content.get('conclusion', {})
    
    # Set font
    pdf.set_font('Arial', 'B', 16)
    
    # Title
    pdf.cell(0, 10, title, 0, 1, 'C')
    pdf.cell(0, 10, address, 0, 1, 'C')
    
    # Executive Summary
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'EXECUTIVE SUMMARY', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, executive_summary.get('overview', ''))
    pdf.ln(3)
    pdf.multi_cell(0, 5, executive_summary.get('development', ''))
    pdf.ln(3)
    pdf.multi_cell(0, 5, executive_summary.get('rental', ''))
    pdf.ln(3)
    pdf.multi_cell(0, 5, executive_summary.get('strategy', ''))
    
    # Property Appraisal
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'PROPERTY APPRAISAL', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, property_appraisal.get('description', ''))
    pdf.ln(3)
    pdf.multi_cell(0, 5, property_appraisal.get('valuation', ''))
    
    # Property Details
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Property Details', 0, 1)
    
    property_details = property_appraisal.get('data', {}).get('property_details', {})
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 6, 'Property Type:', 0, 0)
    pdf.cell(0, 6, property_details.get('property_type', 'N/A'), 0, 1)
    
    pdf.cell(50, 6, 'Bedrooms:', 0, 0)
    pdf.cell(0, 6, str(property_details.get('bedrooms', 'N/A')), 0, 1)
    
    pdf.cell(50, 6, 'Bathrooms:', 0, 0)
    pdf.cell(0, 6, str(property_details.get('bathrooms', 'N/A')), 0, 1)
    
    pdf.cell(50, 6, 'Floor Area:', 0, 0)
    pdf.cell(0, 6, property_details.get('floor_area', 'N/A'), 0, 1)
    
    pdf.cell(50, 6, 'Tenure:', 0, 0)
    pdf.cell(0, 6, property_details.get('tenure', 'N/A'), 0, 1)
    
    # Comparable Analysis
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Comparable Analysis', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, property_appraisal.get('comparables', ''))
    
    # Feasibility Study
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'FEASIBILITY STUDY', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, feasibility_study.get('overview', ''))
    
    # Development Scenarios
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Development Scenarios', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, feasibility_study.get('scenarios', ''))
    
    # Add scenarios table
    development_scenarios = feasibility_study.get('data', {}).get('development_scenarios', [])
    if development_scenarios:
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 8, 'Scenario', 1, 0, 'C')
        pdf.cell(30, 8, 'Cost', 1, 0, 'C')
        pdf.cell(40, 8, 'Value Uplift', 1, 0, 'C')
        pdf.cell(40, 8, 'New Value', 1, 0, 'C')
        pdf.cell(30, 8, 'ROI', 1, 1, 'C')
        
        pdf.set_font('Arial', '', 9)
        for scenario in development_scenarios:
            pdf.cell(40, 8, scenario.get('name', 'N/A'), 1, 0)
            pdf.cell(30, 8, scenario.get('formatted_cost', 'N/A'), 1, 0, 'R')
            pdf.cell(40, 8, f"{scenario.get('formatted_value_uplift', 'N/A')} ({scenario.get('value_uplift_percentage', 'N/A')})", 1, 0, 'R')
            pdf.cell(40, 8, scenario.get('formatted_new_value', 'N/A'), 1, 0, 'R')
            pdf.cell(30, 8, scenario.get('formatted_roi', 'N/A'), 1, 1, 'R')
    
    # Rental Analysis
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Rental Analysis', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, feasibility_study.get('rental_potential', ''))
    
    rental_analysis = feasibility_study.get('data', {}).get('rental_analysis', {})
    
    pdf.ln(3)
    pdf.cell(70, 6, 'Monthly Rental Income:', 0, 0)
    pdf.cell(0, 6, rental_analysis.get('formatted_monthly_rental_income', 'N/A'), 0, 1)
    
    pdf.cell(70, 6, 'Annual Rental Income:', 0, 0)
    pdf.cell(0, 6, rental_analysis.get('formatted_annual_rental_income', 'N/A'), 0, 1)
    
    pdf.cell(70, 6, 'Gross Yield:', 0, 0)
    pdf.cell(0, 6, rental_analysis.get('formatted_gross_yield', 'N/A'), 0, 1)
    
    # Rental Growth Forecast
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Rental Growth Forecast', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, feasibility_study.get('growth_forecast', ''))
    
    # Add forecast table
    rental_forecast = rental_analysis.get('rental_forecast', [])
    if rental_forecast:
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 8, 'Year', 1, 0, 'C')
        pdf.cell(50, 8, 'Monthly Rent', 1, 0, 'C')
        pdf.cell(50, 8, 'Annual Rent', 1, 0, 'C')
        pdf.cell(40, 8, 'Growth', 1, 1, 'C')
        
        pdf.set_font('Arial', '', 9)
        for forecast in rental_forecast:
            pdf.cell(40, 8, forecast.get('year', 'N/A'), 1, 0, 'C')
            pdf.cell(50, 8, forecast.get('formatted_monthly_rent', 'N/A'), 1, 0, 'R')
            pdf.cell(50, 8, forecast.get('formatted_annual_rent', 'N/A'), 1, 0, 'R')
            pdf.cell(40, 8, forecast.get('growth', 'N/A'), 1, 1, 'C')
    
    # Planning Analysis
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'PLANNING ANALYSIS', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, planning_analysis.get('current_use', ''))
    
    # Planning Opportunities
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Planning Opportunities', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, planning_analysis.get('opportunities', ''))
    
    opportunities = planning_analysis.get('data', {}).get('opportunities', [])
    for opportunity in opportunities:
        pdf.cell(10, 6, '•', 0, 0)
        pdf.multi_cell(0, 6, opportunity)
    
    # Planning Constraints
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Planning Constraints', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, planning_analysis.get('constraints', ''))
    
    constraints = planning_analysis.get('data', {}).get('constraints', [])
    for constraint in constraints:
        pdf.cell(10, 6, '•', 0, 0)
        pdf.multi_cell(0, 6, constraint)
    
    # Risk Assessment
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'RISK ASSESSMENT', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, risk_assessment.get('overview', ''))
    
    # Risk Profile
    pdf.ln(3)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(50, 6, 'Overall Risk Profile:', 0, 0)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, risk_assessment.get('data', {}).get('risk_profile', 'Medium'), 0, 1)
    
    # Key Risks
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Key Risks', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, risk_assessment.get('key_risks', ''))
    
    # Risk Table
    identified_risks = risk_assessment.get('data', {}).get('identified_risks', [])
    if identified_risks:
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(30, 8, 'Category', 1, 0, 'C')
        pdf.cell(80, 8, 'Description', 1, 0, 'C')
        pdf.cell(30, 8, 'Impact', 1, 0, 'C')
        pdf.cell(50, 8, 'Mitigation', 1, 1, 'C')
        
        pdf.set_font('Arial', '', 9)
        for risk in identified_risks:
            # Calculate height needed for description (which might be longer)
            description = risk.get('description', 'N/A')
            mitigation = risk.get('mitigation', 'N/A')
            description_lines = max(1, len(description) // 40)
            mitigation_lines = max(1, len(mitigation) // 25)
            line_height = max(description_lines, mitigation_lines) * 6
            
            pdf.cell(30, line_height, risk.get('category', 'N/A'), 1, 0)
            pdf.multi_cell(80, line_height / description_lines, description, 1, 0)
            pdf.set_xy(pdf.get_x() + 110, pdf.get_y() - line_height)
            pdf.cell(30, line_height, risk.get('impact', 'N/A'), 1, 0, 'C')
            pdf.multi_cell(50, line_height / mitigation_lines, mitigation, 1, 1)
    
    # Local Market Analysis
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'LOCAL MARKET ANALYSIS', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, local_market_analysis.get('market_overview', ''))
    
    # Price Trends
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Price Trends', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, local_market_analysis.get('price_trends', ''))
    
    market_data = local_market_analysis.get('data', {}).get('market_data', {})
    
    pdf.ln(3)
    pdf.cell(70, 6, 'Average Price per Sqft:', 0, 0)
    pdf.cell(0, 6, market_data.get('average_price_per_sqft', 'N/A'), 0, 1)
    
    pdf.cell(70, 6, '1-Year Price Trend:', 0, 0)
    pdf.cell(0, 6, market_data.get('price_trend_1yr', 'N/A'), 0, 1)
    
    pdf.cell(70, 6, '5-Year Price Trend:', 0, 0)
    pdf.cell(0, 6, market_data.get('price_trend_5yr', 'N/A'), 0, 1)
    
    # Rental Market
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Rental Market', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, local_market_analysis.get('rental_market', ''))
    
    # Amenities
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Local Amenities and Transport', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, local_market_analysis.get('amenities', ''))
    
    # Conclusion
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'CONCLUSION', 0, 1)
    
    # BTR Potential
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"BTR Potential: {conclusion.get('data', {}).get('btr_potential', 'Moderate').capitalize()}", 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, conclusion.get('btr_assessment', ''))
    
    # Key Findings
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Key Findings', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, conclusion.get('key_findings', ''))
    
    # Recommendation
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Investment Recommendation', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, conclusion.get('recommendation', ''))
    
    # Next Steps
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Next Steps', 0, 1)
    
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, conclusion.get('next_steps', ''))
    
    # Footer
    pdf.ln(15)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 5, f"Report generated by Property Valuation App on {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
    pdf.cell(0, 5, "© 2025 Property Valuation App", 0, 1, 'C')

@app.route('/clear-report/<report_id>')
def clear_report(report_id):
    """Clear a report from memory"""
    if report_id in reports:
        del reports[report_id]
        return jsonify({'success': True, 'message': 'Report cleared'})
    return jsonify({'success': False, 'message': 'Report not found'})

@app.route('/api-key-status')
def api_key_status():
    """Check if the OpenAI API key is configured"""
    api_key = os.getenv("OPENAI_API_KEY")
    return jsonify({
        'configured': bool(api_key),
        'message': 'OpenAI API key is configured' if api_key else 'OpenAI API key is not configured'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
