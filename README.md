# Debatix - AI-Powered Debate Platform

Debatix is an innovative platform that facilitates structured debates between Large Language Models (LLMs). It provides a modern interface for conducting Oxford-style debates with AI-generated arguments, evidence, and judgments.

## Features

- **Turn-based Debate System**: Engage in structured debates with alternating pro and con arguments
- **Evidence-based Arguments**: AI-generated arguments with proper citations and references
- **Professional Judging**: Comprehensive evaluation of debate performance
- **Document Support**: Upload and debate based on PDF or DOCX documents
- **Modern UI**: Clean, responsive interface with real-time updates
- **Web Search Integration**: Access to current information for more relevant arguments

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI**: Google Gemini 1.5 Pro
- **Document Processing**: PyPDF2, python-docx
- **Styling**: Custom CSS with Discord-inspired theme

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Aditya-54/Debatrix--LLM-S-debate.git
cd Debatrix--LLM-S-debate
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python app.py
```

## Usage

1. **Start a Debate**:
   - Enter a debate topic
   - Click "Start Debate" to begin

2. **Generate Arguments**:
   - Use "Pro Argument" and "Con Argument" buttons to generate responses
   - Each argument includes evidence and citations

3. **Get Judgment**:
   - Click "Final Judgment" to receive a comprehensive evaluation
   - The judgment includes scores, analysis, and suggestions

4. **Document-based Debate**:
   - Upload a PDF or DOCX file
   - Select your role (proponent/opponent)
   - Enter a prompt
   - Engage in a debate based on the document content

## Project Structure

```
Debatrix/
├── app.py              # Main Flask application
├── main.py             # Core debate system
├── summary.py          # Document processing and debate
├── debate_context.py   # Debate state management
├── static/             # Static files
│   ├── css/           # Stylesheets
│   └── uploads/       # Document uploads
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── debate.html    # Debate interface
│   └── document_debate.html  # Document debate interface
└── requirements.txt    # Dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- Flask framework for web application
- Bootstrap for UI components
- PyPDF2 and python-docx for document processing