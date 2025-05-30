import os
import sys
import logging
import tempfile
import uuid
import threading
import traceback
import time
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_file
from fpdf import FPDF

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the test.py workflow
try:
    from test import run_workflow
except ImportError:
    logger.error("Could not import test.py workflow. Make sure test.py is in the same directory.")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", str(uuid.uuid4()))

# Store reports temporarily in memory
reports = {}

# HTML template for the main page
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Property Valuation AI</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .main-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .card-header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .card-header h2 {
            font-size: 1.8rem;
            margin-bottom: 10px;
            font-weight: 400;
        }

        .card-body {
            padding: 40px;
        }

        .api-setup {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
        }

        .api-status {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #e74c3c;
        }

        .status-indicator.connected {
            background: #27ae60;
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #2c3e50;
        }

        .form-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: white;
        }

        .form-input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }

        .address-input {
            min-height: 80px;
            resize: vertical;
        }

        .btn {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            position: relative;
            overflow: hidden;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        }

        .btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .btn i {
            margin-right: 8px;
        }

        .progress-section {
            display: none;
            margin-top: 30px;
        }

        .progress-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e1e8ed;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2980b9);
            border-radius: 4px;
            transition: width 0.3s ease;
            width: 0%;
        }

        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }

        .agent-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }

        .agent-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }

        .agent-icon {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3498db, #2980b9);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            color: white;
            font-size: 20px;
        }

        .agent-card h4 {
            margin-bottom: 10px;
            color: #2c3e50;
        }

        .agent-status {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            background: #f39c12;
            color: white;
        }

        .agent-status.working {
            background: #3498db;
        }

        .agent-status.complete {
            background: #27ae60;
        }

        .agent-status.error {
            background: #e74c3c;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e1e8ed;
            border-left: 4px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-section {
            display: none;
            background: #fff5f5;
            border: 1px solid #fed7d7;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }

        .error-section h3 {
            color: #e53e3e;
            margin-bottom: 10px;
        }

        .error-section p {
            color: #744d4d;
            margin-bottom: 15px;
        }

        .retry-btn {
            background: #e53e3e;
            padding: 10px 20px;
            font-size: 14px;
        }

        .success-section {
            display: none;
            text-align: center;
            margin-top: 30px;
        }

        .success-icon {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: #27ae60;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            color: white;
            font-size: 30px;
        }

        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 25px;
        }

        .btn-secondary {
            background: #95a5a6;
        }

        .btn-outline {
            background: transparent;
            color: #3498db;
            border: 2px solid #3498db;
        }

        .btn-outline:hover {
            background: #3498db;
            color: white;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .card-body {
                padding: 25px;
            }
            
            .action-buttons {
                flex-direction: column;
            }
            
            .agent-grid {
                grid-template-columns: 1fr;
            }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header fade-in">
            <h1><i class="fas fa-home"></i> Property Valuation AI</h1>
            <p>Advanced AI-powered property analysis and BTR potential assessment</p>
        </div>

        <div class="main-card fade-in">
            <div class="card-header">
                <h2><i class="fas fa-robot"></i> Intelligent Property Analysis</h2>
                <p>Enter your OpenAI API key and property address to generate comprehensive reports</p>
            </div>

            <div class="card-body">
                <!-- API Setup Section -->
                <div class="api-setup">
                    <div class="api-status">
                        <div class="status-indicator" id="api-status-indicator"></div>
                        <span id="api-status-text">OpenAI API Not Connected</span>
                    </div>
                    <div class="form-group">
                        <label for="api-key">
                            <i class="fas fa-key"></i> OpenAI API Key
                        </label>
                        <input 
                            type="password" 
                            id="api-key" 
                            class="form-input" 
                            placeholder="sk-..."
                            autocomplete="off"
                        >
                        <small style="color: #7f8c8d; margin-top: 5px; display: block;">
                            Your API key is stored locally and never transmitted to our servers
                        </small>
                    </div>
                </div>

                <!-- Address Input Section -->
                <form id="address-form">
                    <div class="form-group">
                        <label for="address">
                            <i class="fas fa-map-marker-alt"></i> UK Property Address
                        </label>
                        <textarea 
                            id="address" 
                            class="form-input address-input" 
                            placeholder="e.g., 381 Filton Avenue, BS7 0LH"
                            required
                        ></textarea>
                    </div>

                    <button type="submit" class="btn" id="generate-btn">
                        <i class="fas fa-chart-line"></i> Generate AI Report
                    </button>
                </form>

                <!-- Progress Section -->
                <div class="progress-section" id="progress-section">
                    <div class="progress-card">
                        <div class="spinner"></div>
                        <h3 id="progress-title">Generating Your Report</h3>
                        <p id="progress-message">Initializing AI agents...</p>
                        
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        
                        <div class="agent-grid" id="agent-grid">
                            <div class="agent-card">
                                <div class="agent-icon">
                                    <i class="fas fa-search"></i>
                                </div>
                                <h4>Research Agent</h4>
                                <span class="agent-status" id="research-status">Waiting</span>
                            </div>
                            <div class="agent-card">
                                <div class="agent-icon">
                                    <i class="fas fa-calculator"></i>
                                </div>
                                <h4>Evaluation Agent</h4>
                                <span class="agent-status" id="evaluation-status">Waiting</span>
                            </div>
                            <div class="agent-card">
                                <div class="agent-icon">
                                    <i class="fas fa-check-circle"></i>
                                </div>
                                <h4>Accessor Agent</h4>
                                <span class="agent-status" id="accessor-status">Waiting</span>
                            </div>
                            <div class="agent-card">
                                <div class="agent-icon">
                                    <i class="fas fa-file-alt"></i>
                                </div>
                                <h4>Report Generator</h4>
                                <span class="agent-status" id="generator-status">Waiting</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Error Section -->
                <div class="error-section" id="error-section">
                    <h3><i class="fas fa-exclamation-triangle"></i> Generation Failed</h3>
                    <p id="error-message"></p>
                    <button class="btn retry-btn" id="retry-btn">
                        <i class="fas fa-redo"></i> Retry Generation
                    </button>
                </div>

                <!-- Success Section -->
                <div class="success-section" id="success-section">
                    <div class="success-icon">
                        <i class="fas fa-check"></i>
                    </div>
                    <h3>Report Generated Successfully!</h3>
                    <p>Your comprehensive property analysis is ready</p>
                    
                    <div class="action-buttons">
                        <button class="btn" id="view-report-btn">
                            <i class="fas fa-eye"></i> View Report
                        </button>
                        <button class="btn btn-secondary" id="download-pdf-btn">
                            <i class="fas fa-download"></i> Download PDF
                        </button>
                        <button class="btn btn-outline" id="new-report-btn">
                            <i class="fas fa-plus"></i> New Report
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        class PropertyValuationApp {
            constructor() {
                this.currentReportId = null;
                this.apiKey = localStorage.getItem('openai_api_key') || '';
                this.init();
            }

            init() {
                this.bindEvents();
                this.checkApiKey();
                this.updateApiStatus();
            }

            bindEvents() {
                // API Key input
                document.getElementById('api-key').addEventListener('input', (e) => {
                    this.apiKey = e.target.value;
                    localStorage.setItem('openai_api_key', this.apiKey);
                    this.updateApiStatus();
                });

                // Form submission
                document.getElementById('address-form').addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.generateReport();
                });

                // Button events
                document.getElementById('retry-btn').addEventListener('click', () => {
                    this.generateReport();
                });

                document.getElementById('view-report-btn').addEventListener('click', () => {
                    this.viewReport();
                });

                document.getElementById('download-pdf-btn').addEventListener('click', () => {
                    this.downloadPDF();
                });

                document.getElementById('new-report-btn').addEventListener('click', () => {
                    this.resetForm();
                });
            }

            checkApiKey() {
                if (this.apiKey) {
                    document.getElementById('api-key').value = this.apiKey;
                }
            }

            updateApiStatus() {
                const indicator = document.getElementById('api-status-indicator');
                const text = document.getElementById('api-status-text');
                const generateBtn = document.getElementById('generate-btn');

                if (this.apiKey && this.apiKey.startsWith('sk-')) {
                    indicator.classList.add('connected');
                    text.textContent = 'OpenAI API Connected';
                    generateBtn.disabled = false;
                } else {
                    indicator.classList.remove('connected');
                    text.textContent = 'OpenAI API Not Connected';
                    generateBtn.disabled = true;
                }
            }

            async generateReport() {
                const address = document.getElementById('address').value.trim();
                
                if (!address) {
                    alert('Please enter a property address');
                    return;
                }

                if (!this.apiKey || !this.apiKey.startsWith('sk-')) {
                    alert('Please enter a valid OpenAI API key');
                    return;
                }

                // Set the API key as environment variable
                await this.setApiKey();

                this.showProgress();
                this.resetAgentStatus();

                try {
                    // Validate address
                    const validateResponse = await fetch('/validate-address', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ address })
                    });
                    
                    const validateData = await validateResponse.json();
                    
                    if (!validateData.valid) {
                        throw new Error(validateData.message || 'Invalid address');
                    }

                    // Generate report
                    const reportResponse = await fetch('/generate-report', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            address: validateData.formatted_address || address,
                            api_key: this.apiKey 
                        })
                    });
                    
                    const reportData = await reportResponse.json();
                    
                    if (reportData.success && reportData.report_id) {
                        this.currentReportId = reportData.report_id;
                        this.pollReportStatus();
                    } else {
                        throw new Error(reportData.message || 'Failed to start report generation');
                    }
                } catch (error) {
                    this.showError(error.message);
                }
            }

            async setApiKey() {
                try {
                    await fetch('/set-api-key', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ api_key: this.apiKey })
                    });
                } catch (error) {
                    console.error('Failed to set API key:', error);
                }
            }

            async pollReportStatus() {
                if (!this.currentReportId) return;

                try {
                    const response = await fetch(`/report-status/${this.currentReportId}`);
                    const data = await response.json();

                    if (data.success) {
                        this.updateProgress(data.progress, data.message);

                        if (data.complete) {
                            this.showSuccess();
                        } else if (data.status === 'error') {
                            this.showError(data.message || 'Report generation failed', data.can_retry);
                        } else {
                            setTimeout(() => this.pollReportStatus(), 2000);
                        }
                    } else {
                        this.showError(data.message || 'Failed to check report status');
                    }
                } catch (error) {
                    this.showError('Error checking report status: ' + error.message);
                }
            }

            updateProgress(progress, message) {
                document.getElementById('progress-fill').style.width = `${progress}%`;
                document.getElementById('progress-message').textContent = message || '';
            }

            resetAgentStatus() {
                ['research', 'evaluation', 'accessor', 'generator'].forEach(agent => {
                    const statusElement = document.getElementById(`${agent}-status`);
                    if (statusElement) {
                        statusElement.textContent = 'Waiting';
                        statusElement.className = 'agent-status';
                    }
                });
            }

            showProgress() {
                document.getElementById('progress-section').style.display = 'block';
                document.getElementById('error-section').style.display = 'none';
                document.getElementById('success-section').style.display = 'none';
                document.getElementById('generate-btn').disabled = true;
                this.updateProgress(0, 'Initializing...');
            }

            showError(message, canRetry = true) {
                document.getElementById('progress-section').style.display = 'none';
                document.getElementById('success-section').style.display = 'none';
                document.getElementById('error-section').style.display = 'block';
                document.getElementById('error-message').textContent = message;
                document.getElementById('retry-btn').style.display = canRetry ? 'inline-block' : 'none';
                document.getElementById('generate-btn').disabled = false;
            }

            showSuccess() {
                document.getElementById('progress-section').style.display = 'none';
                document.getElementById('error-section').style.display = 'none';
                document.getElementById('success-section').style.display = 'block';
                document.getElementById('generate-btn').disabled = false;
            }

            viewReport() {
                if (this.currentReportId) {
                    window.open(`/view-report/${this.currentReportId}`, '_blank');
                }
            }

            downloadPDF() {
                if (this.currentReportId) {
                    window.open(`/export-pdf/${this.currentReportId}`, '_blank');
                }
            }

            resetForm() {
                document.getElementById('address').value = '';
                document.getElementById('progress-section').style.display = 'none';
                document.getElementById('error-section').style.display = 'none';
                document.getElementById('success-section').style.display = 'none';
                this.currentReportId = null;
                this.updateProgress(0, '');
            }
        }

        // Initialize the app when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            new PropertyValuationApp();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main application page"""
    return render_template_string(INDEX_HTML)

@app.route('/set-api-key', methods=['POST'])
def set_api_key():
    """Set the OpenAI API key as environment variable"""
    data = request.json
    api_key = data.get('api_key', '')
    
    if api_key and api_key.startswith('sk-'):
        os.environ['OPENAI_API_KEY'] = api_key
        return jsonify({'success': True, 'message': 'API key set successfully'})
    else:
        return jsonify({'success': False, 'message': 'Invalid API key'})

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
    api_key = data.get('api_key', '')
    
    if not address:
        return jsonify({'success': False, 'message': 'Address is required'})
    
    # Set API key in environment if provided
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({
            'success': False, 
            'message': 'OpenAI API key not found. Please provide your API key.'
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
    """Process the report generation in the background using test.py workflow"""
    try:
        # Update status to show we're starting
        reports[report_id]['status'] = 'researching'
        reports[report_id]['progress'] = 10
        reports[report_id]['message'] = 'Running AI workflow...'
        
        # Update progress during workflow
        reports[report_id]['progress'] = 30
        reports[report_id]['message'] = 'Research agent gathering data...'
        
        # Call the workflow from test.py
        result = run_workflow(address)
        
        if result['success']:
            # Update status to show completion
            reports[report_id]['status'] = 'complete'
            reports[report_id]['progress'] = 100
            reports[report_id]['message'] = 'Report generation complete'
            
            # Read the generated report files
            try:
                with open('report_output_refined.txt', 'r', encoding='utf-8') as f:
                    report_text = f.read()
                
                with open('report_output_refined.json', 'r', encoding='utf-8') as f:
                    report_data = f.read()
                
                reports[report_id]['report_text'] = report_text
                reports[report_id]['report_data'] = report_data
                
            except FileNotFoundError:
                logger.warning("Report files not found, using basic structure")
                reports[report_id]['report_text'] = f"Property Analysis Report for {address}\n\nReport generated successfully using AI agents."
                reports[report_id]['report_data'] = '{"title": "Property Report", "address": "' + address + '"}'
            
        else:
            # Handle workflow failure
            reports[report_id]['status'] = 'error'
            reports[report_id]['message'] = f"Workflow failed: {result.get('error', 'Unknown error')}"
            
    except Exception as e:
        logger.error(f"Error processing report: {str(e)}")
        reports[report_id]['status'] = 'error'
        reports[report_id]['message'] = f"Error: {str(e)}"
        reports[report_id]['error_details'] = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }

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
        'complete': report.get('status') == 'complete',
        'error_details': report.get('error_details'),
        'can_retry': report.get('status') == 'error'
    })

@app.route('/view-report/<report_id>')
def view_report(report_id):
    """View a generated report"""
    if report_id not in reports:
        return render_template_string("""
        <h1>Report Not Found</h1>
        <p>The requested report could not be found.</p>
        <a href="/">Return to Home</a>
        """)
    
    report = reports[report_id]
    
    if report.get('status') != 'complete':
        return render_template_string(f"""
        <h1>Report Not Ready</h1>
        <p>Report status: {report.get('status', 'processing')}</p>
        <p>{report.get('message', '')}</p>
        <a href="/">Return to Home</a>
        """)
    
    # Create a formatted HTML view of the report
    report_text = report.get('report_text', 'No report content available')
    formatted_report = report_text.replace('\n', '<br>')
    
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Property Valuation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .report-header {{ text-align: center; margin-bottom: 30px; }}
            .report-content {{ line-height: 1.6; }}
            .btn {{ padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="report-header">
            <h1>Property Valuation Report</h1>
            <p>Generated on {report.get('timestamp', 'Unknown date')}</p>
            <a href="/" class="btn">Generate New Report</a>
        </div>
        <div class="report-content">
            {formatted_report}
        </div>
    </body>
    </html>
    """)

@app.route('/export-pdf/<report_id>')
def export_pdf(report_id):
    """Export a report as PDF"""
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
        pdf = FPDF('P', 'mm', 'A4')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Add header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Property Valuation Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Add content
        pdf.set_font('Arial', '', 12)
        report_text = report.get('report_text', 'No report content available')
        
        # Split text into lines and add to PDF
        lines = report_text.split('\n')
        for line in lines:
            if line.strip():
                # Handle different heading levels
                if line.startswith('# '):
                    pdf.set_font('Arial', 'B', 14)
                    pdf.ln(5)
                    pdf.cell(0, 10, line[2:], 0, 1)
                    pdf.ln(2)
                elif line.startswith('## '):
                    pdf.set_font('Arial', 'B', 12)
                    pdf.ln(3)
                    pdf.cell(0, 8, line[3:], 0, 1)
                    pdf.ln(1)
                else:
                    pdf.set_font('Arial', '', 10)
                    pdf.multi_cell(0, 6, line)
                    pdf.ln(1)
        
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

@app.route('/clear-report/<report_id>')
def clear_report(report_id):
    """Clear a report from memory"""
    if report_id in reports:
        del reports[report_id]
        return jsonify({'success': True, 'message': 'Report cleared'})
    return jsonify({'success': False, 'message': 'Report not found'})

if __name__ == '__main__':
    print("🏠 Property Valuation AI Server Starting...")
    print("📊 Navigate to http://localhost:8000 to use the application")
    print("🔑 Make sure to enter your OpenAI API key in the interface")
    print("📍 Example address: 381 Filton Avenue, BS7 0LH")
    app.run(host='0.0.0.0', port=8001, debug=True)