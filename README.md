# UK Property Valuation

![UK Property Valuation](https://private-us-east-1.manuscdn.com/sessionFile/fPKRSNtsIYtUPQcl4oiPve/sandbox/J8AOUqZ8OTCdBxdJJeWpEw-images_1748870787639_na1fn_L2hvbWUvdWJ1bnR1L3VrX3Byb3BlcnR5X3ZhbHVhdGlvbl9iYW5uZXI.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvZlBLUlNOdHNJWXRVUFFjbDRvaVB2ZS9zYW5kYm94L0o4QU9VcVo4T1RDZEJ4ZEpKZVdwRXctaW1hZ2VzXzE3NDg4NzA3ODc2MzlfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwzVnJYM0J5YjNCbGNuUjVYM1poYkhWaGRHbHZibDlpWVc1dVpYSS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3NjcyMjU2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=aSf2mqStNVUks9woRbS25xjtIodNgYOnmLo41kvFd1EDpoqnXLTuwW8VSvdb2VY2-V-jw6FbKFxzoMyEhbM2I6~GLCI-rQKPlpWh~cIeaL602x8tKRvabWevfdcFCftoGGHgu97MquhzvZqlwQlkFLJIncIN5PiCKwta0VT4oh0pQZivhZPr8P1UlM8uNWZkFq-yxk3U~hIp-uN-mNVeBbqakVscF1kq69ig-0ZXzRRweKbu0Loddox0raLVSrbnDma3rk2OZ27cTxNTFI3hUZqHZl6PJXk47~39vcm~JLA9SLF9~28d7xDB9dY8JDOZWLEoK-iUV2buaFPVigs5dg__)

## Overview

The UK Property Valuation application is a sophisticated desktop tool that generates detailed property valuation reports for UK addresses. Leveraging an agentic AI system, the application gathers, analyses, and presents property information in a professional format, providing valuable insights for homeowners, investors, and real estate professionals.

## Key Features

- **UK Address Validation**: Accurately validates and standardises UK property addresses
- **Multi-Agent AI System**: Employs a coordinated team of AI agents to gather and analyse property data
- **Comprehensive Reports**: Generates detailed valuation reports with multiple sections
- **Data-Driven Analysis**: Collects information from reliable sources including Land Registry, VOA, and local council records
- **PDF Export**: Exports professional reports in PDF format for sharing and archiving
- **Interactive Interface**: Provides a responsive web-based interface for desktop and mobile use

## System Architecture

The application implements a sophisticated multi-agent architecture:

### Agentic AI System

- **Accessor Agent (Coordinator)**: Validates information and makes final decisions on report content
- **Research Agent**: Gathers property data from reliable sources and local market information
- **Evaluation Agent**: Analyses collected data and performs valuation calculations
- **Report Generation Agent**: Creates the formatted report with visualisations and tables

### Technical Implementation

- **Frontend**: HTML, CSS, and JavaScript with responsive design
- **Backend**: Python-based application server using Flask framework
- **Data Processing**: Specialised modules for property information analysis
- **PDF Generation**: WeasyPrint for high-quality PDF exports

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

### 1. Enter a UK Address

- Type a complete UK address in the input field
- Click "Generate Report" to start the process

### 2. Report Generation

The application will show the progress of each agent in the workflow:
- Research Agent gathers property data from various sources
- Evaluation Agent analyses the data and performs valuations
- Accessor Agent reviews and approves the information
- Report Generator creates the formatted report

### 3. View the Report

Once generation is complete, the report will be displayed with sections including:
- Executive Summary
- Property Appraisal and Valuation
- Renovation Scenarios
- Rental Forecast
- Comparable Properties

### 4. Export Options

- Download the report as a PDF
- Print directly from the browser
- Save for future reference

## System Requirements

- Python 3.8 or higher
- Flask web framework
- WeasyPrint for PDF generation
- Modern web browser (Chrome, Firefox, Edge, or Safari)

## Development

The application is built with a modular architecture that separates concerns:
- `app.py`: Main application entry point
- `agents/`: Contains the AI agent implementation
- `static/`: CSS, JavaScript, and image assets
- `templates/`: HTML templates for the web interface

## Future Enhancements

- Integration with additional data sources
- Machine learning models for more accurate valuations
- User accounts for saving and comparing multiple reports
- Mobile application version

## Credits

Developed by Ishan Yash as a portfolio project demonstrating AI integration, data analysis, and web application development skills.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
