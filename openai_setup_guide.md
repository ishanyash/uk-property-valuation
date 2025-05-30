# OpenAI-Powered Property Valuation App - Setup Guide

## Overview
This guide will help you set up and run the OpenAI-powered Property Valuation App. This version uses the OpenAI API to create a true agentic workflow that generates detailed property valuation reports for UK addresses.

## Prerequisites
- Python 3.8 or higher
- OpenAI API key (required for the agentic functionality)
- Basic understanding of command line operations

## Setup Instructions

### 1. Extract the Application Files
1. Extract the `property_valuation_app_openai.zip` file to a directory of your choice

### 2. Create a Virtual Environment
```bash
# Navigate to the extracted directory
cd path/to/property_valuation_app

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install flask fpdf2 python-dotenv openai requests
```

### 4. Set Up Your OpenAI API Key
Create a `.env` file in the root directory of the application with the following content:
```
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=any_random_string_for_session_security
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Running the Application

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:8000
```

3. Enter a UK address in the input field and click "Generate Report"

4. The application will use the following agentic workflow:
   - Research Agent: Gathers property data from various sources
   - Evaluation Agent: Analyzes data and performs valuations
   - Accessor Agent: Reviews and approves information
   - Report Generator: Creates formatted reports

5. Once complete, you can view the report and export it as a PDF

## Troubleshooting

### API Key Issues
If you see an error about the OpenAI API key:
1. Verify that your `.env` file exists in the root directory
2. Check that the API key is correctly formatted
3. Restart the application after making changes

### Port Already in Use
If port 8000 is already in use:
1. Open `app.py`
2. Change the port number in the last line:
   ```python
   app.run(host='0.0.0.0', port=8001, debug=True)  # Change 8000 to another port
   ```

### OpenAI API Rate Limits
If you encounter rate limit errors:
1. Wait a few minutes before generating another report
2. Consider upgrading your OpenAI API plan for higher rate limits

## Understanding the Agent System

The application uses four specialized OpenAI-powered agents:

1. **Research Agent** (`agents/openai_research_agent.py`)
   - Gathers property data from various sources
   - Parses and standardizes UK addresses
   - Collects property details, market data, and local area information

2. **Evaluation Agent** (`agents/openai_evaluation_agent.py`)
   - Analyzes the gathered property data
   - Performs property valuation calculations
   - Generates development scenarios and rental analysis
   - Assesses planning opportunities and risks

3. **Accessor Agent** (`agents/openai_accessor_agent.py`)
   - Reviews and validates information from other agents
   - Ensures accuracy and consistency
   - Makes final approval decisions on report content
   - Provides feedback on areas needing improvement

4. **Report Generation Agent** (`agents/openai_report_generator.py`)
   - Creates professional, contextual report content
   - Generates natural language descriptions
   - Formats data for presentation
   - Produces the final HTML and PDF reports

## Customization

### Modifying Agent Behavior
Each agent can be customized by editing its system prompt in the corresponding file:
- `agents/openai_research_agent.py`
- `agents/openai_evaluation_agent.py`
- `agents/openai_accessor_agent.py`
- `agents/openai_report_generator.py`

Look for the `get_system_prompt()` method in each file.

### Changing Report Styling
To modify the report appearance:
- Edit `templates/report.html` for the web view
- Modify the `_generate_report_html()` method in `agents/openai_report_generator.py` for HTML reports
- Update the `generate_pdf_content()` function in `app.py` for PDF exports

## Security Considerations

- The OpenAI API key is stored in a `.env` file which should not be committed to version control
- API calls are made securely using the official OpenAI Python client
- User data is stored temporarily in memory and not persisted between application restarts
- No sensitive data is logged or stored permanently

## Next Steps for Production Deployment

For a production environment:
1. Set `debug=False` in the `app.run()` call
2. Use a production WSGI server like Gunicorn
3. Consider adding user authentication
4. Implement proper database storage for reports
5. Add monitoring and error tracking

## Support

If you encounter any issues or have questions, please refer to:
- OpenAI API documentation: https://platform.openai.com/docs/
- Flask documentation: https://flask.palletsprojects.com/
- FPDF2 documentation: https://py-pdf.github.io/fpdf2/
