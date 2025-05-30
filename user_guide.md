# Property Valuation App - User Guide

## Overview

The Property Valuation App is a desktop application that allows users to generate detailed property valuation reports for UK addresses. The application uses an agentic AI system to gather, analyze, and present property information in a professional format.

## Features

- UK address input and validation
- Detailed property valuation reports
- Multi-agent AI system for data gathering and analysis
- PDF export functionality
- Professional report formatting

## System Requirements

- Python 3.8 or higher
- Flask web framework
- WeasyPrint for PDF generation
- Modern web browser (Chrome, Firefox, Edge, or Safari)

## Installation

1. Unzip the `property_valuation_app.zip` file to a directory of your choice
2. Install the required dependencies:
   ```
   pip install flask weasyprint
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Using the Application

1. **Enter a UK Address**
   - Type a complete UK address in the input field
   - Click "Generate Report" to start the process

2. **Report Generation**
   - The application will show the progress of each agent in the workflow
   - Research Agent: Gathers property data from various sources
   - Evaluation Agent: Analyzes the data and performs valuations
   - Accessor Agent: Reviews and approves the information
   - Report Generator: Creates the formatted report

3. **View the Report**
   - Once generation is complete, the report will be displayed
   - The report includes:
     - Executive Summary
     - Property Appraisal and Valuation
     - Renovation Scenarios
     - Rental Forecast
     - Comparable Properties
     - Planning Assessment
     - Risk Assessment
     - Conclusion

4. **Export as PDF**
   - Click the "Export as PDF" button to download the report
   - The PDF can be shared with clients or colleagues

5. **Start a New Report**
   - Click the "New Report" button to generate another report

## Agentic AI System

The application uses a multi-agent system to generate accurate and comprehensive property valuation reports:

1. **Research Agent**
   - Gathers property information from various sources
   - Collects market data, comparable properties, and local area information

2. **Evaluation Agent**
   - Analyzes data collected by the Research Agent
   - Performs calculations for valuations, ROI, and development scenarios

3. **Accessor Agent**
   - Acts as the main coordinator and approver
   - Validates information from other agents
   - Makes final decisions on what to include in the report

4. **Report Generation Agent**
   - Creates the final report based on approved content
   - Formats information according to the report template
   - Prepares the report for PDF export

## Customization

The application can be customized by modifying the following files:

- `templates/index.html`: Main application interface
- `templates/report.html`: Report display template
- `templates/pdf_template.html`: PDF export template
- `static/css/styles.css`: Application styling
- `agents/*.py`: Agent logic and behavior

## Troubleshooting

- **Address Validation Issues**: Ensure you're entering a complete UK address with postcode
- **PDF Export Problems**: Check that WeasyPrint is properly installed
- **Slow Performance**: The application simulates agent processing time for demonstration purposes

## Security Considerations

- The application does not store sensitive information permanently
- All data processing happens locally on your machine
- No external API calls are made with real property data in this prototype

## Future Enhancements

- Integration with real property data APIs
- User accounts and saved reports
- Advanced filtering and search options
- Mobile application version
