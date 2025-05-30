# Property Valuation App Architecture

## Overview
This document outlines the architecture for a property valuation application that allows users to enter UK addresses and generate detailed valuation reports with the help of an agentic AI system.

## System Components

### 1. User Interface
- **Address Input Form**: Allows users to enter and validate UK addresses
- **Report Viewer**: Displays the generated property valuation report
- **Export Controls**: Provides options to export the report as PDF
- **Status Indicators**: Shows progress during report generation

### 2. Agentic AI System
The system will implement a multi-agent architecture with the following agents:

#### 2.1 Accessor Agent (Coordinator)
- Acts as the main coordinator and approver
- Validates information from other agents
- Makes final decisions on what to include in the report
- Ensures report quality and accuracy

#### 2.2 Research Agent
- Searches the internet for property information
- Gathers data from reliable sources (Land Registry, VOA, local council records)
- Collects market data, comparable properties, and local area information
- Provides raw data to the Evaluation Agent

#### 2.3 Evaluation Agent
- Analyzes data collected by the Research Agent
- Compares and validates information from multiple sources
- Performs calculations for valuations, ROI, and development scenarios
- Prepares structured data for report generation

#### 2.4 Report Generation Agent
- Creates the final report based on approved content
- Formats information according to the report template
- Generates visualizations and tables
- Prepares the report for PDF export

### 3. Data Processing Layer
- **Address Validation**: Validates and standardizes UK addresses
- **Data Storage**: Temporarily stores collected information
- **Calculation Engine**: Performs financial calculations for valuations and scenarios
- **Template System**: Manages report templates and formatting

### 4. Output Generation
- **HTML Report Renderer**: Creates the on-screen report
- **PDF Generator**: Converts the report to PDF format
- **Export Module**: Handles file saving and sharing options

## Technical Implementation

### Frontend
- Web-based interface using HTML, CSS, and JavaScript
- Responsive design for desktop and mobile compatibility
- Form validation for address input
- Dynamic report rendering

### Backend
- Python-based application server
- Flask web framework for API endpoints and serving the application
- Data processing modules for property information analysis
- PDF generation using WeasyPrint

### AI Integration
- Agent communication through structured JSON messages
- Web search capabilities for the Research Agent
- Data validation and cross-referencing for the Evaluation Agent
- Approval workflow managed by the Accessor Agent

### Data Flow
1. User enters UK property address
2. Address is validated and standardized
3. Research Agent collects property and market data
4. Evaluation Agent analyzes and validates the data
5. Accessor Agent reviews and approves the information
6. Report Generation Agent creates the formatted report
7. User views the report and can export as PDF

## Security Considerations
- Input validation to prevent injection attacks
- Secure handling of property data
- No permanent storage of sensitive information
- Transparent AI decision-making process

## Deployment Options
- Local desktop application
- Web-based application with local server
- Containerized deployment for portability
