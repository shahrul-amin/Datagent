# Datagent

A powerful AI-driven data analysis platform that combines the intelligence of Google's Gemini AI with an intuitive chat interface for comprehensive dataset analysis and visualization.

## Features

### AI-Powered Data Analysis
- **Intelligent Data Science Agent**: Powered by Google Gemini 2.0 Flash model
- **Comprehensive Dataset Analysis**: Automatic data exploration, cleaning, and statistical insights
- **Natural Language Queries**: Ask questions about your data in plain English
- **Interactive Chat Interface**: Gemini-inspired conversational UI

### Advanced Visualizations
- **Multiple Chart Types**: Bar charts, line plots, scatter plots, heatmaps, and more
- **Interactive Plots**: Plotly.js integration for dynamic visualizations
- **Matplotlib Support**: Static plots with high-quality rendering
- **Real-time Plot Generation**: Instant visualization based on your queries

### File Support & Data Handling
- **Multiple File Formats**: CSV, XLSX, JSON, SQL, XML support
- **Drag & Drop Upload**: Intuitive file upload interface
- **Image Attachments**: Support for image analysis and processing
- **File Preview**: Visual preview of uploaded files

### Modern Tech Stack
- **Frontend**: React 18 with modern hooks and MVVM architecture
- **Backend**: Flask with clean MVC structure
- **Styling**: TailwindCSS for responsive, modern UI
- **Code Highlighting**: Syntax highlighting for generated code
- **Markdown Rendering**: Rich text formatting for responses

### Performance & UX
- **Real-time Streaming**: Live response generation
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Error Handling**: Comprehensive error management and user feedback
- **Loading States**: Smooth loading animations and progress indicators

## Project Structure

```
datagent/
├── client/                 # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── ChatInput.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── ChatMessageList.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── services/       # API and storage services
│   │   │   ├── ApiService.js
│   │   │   └── StorageService.js
│   │   ├── viewmodels/     # Business logic layer
│   │   │   └── ChatViewModel.js
│   │   └── views/          # Main view components
│   │       └── ChatView.jsx
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
│
└── server/                 # Flask backend application
    ├── controllers/        # Request handlers
    │   ├── chat_controller.py
    │   └── file_controller.py
    ├── models/             # Data models
    │   └── chat_models.py
    ├── services/           # Business logic services
    │   ├── gemini_service.py
    │   ├── file_service.py
    │   ├── plot_context_service.py
    │   ├── response_service.py
    │   └── sequential_workflow_service.py
    ├── utils/              # Utility functions
    │   ├── code_executor.py
    │   ├── dataset_manager.py
    │   ├── gemini_factory.py
    │   ├── prompts.py
    │   └── response_formatter.py
    ├── datasets/           # Sample datasets
    └── requirements.txt    # Backend dependencies
```

## Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **npm** (v7 or higher)
- **Google Gemini API Key** ([Get it here](https://makersuite.google.com/app/apikey))

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/shahrul-amin/Datagent
   cd datagent
   ```

2. **Backend Setup**
   ```bash
   cd server
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd client
   npm install
   ```

4. **Environment Variables**
   
   **API Configuration** - Create `server/.env`:
   ```json
   "GEMINI_API_KEY": "your_gemini_api_key_here"
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd server
   python app.py
   ```
   The Flask server will run on `http://localhost:5000`

2. **Start the Frontend Development Server**
   ```bash
   cd client
   npm run dev
   ```

3. **Access the Application**
   Open your browser and navigate to link that given to you after starting frontend development server

## Usage Guide

### Basic Data Analysis

1. **Upload a Dataset**
   - Click the file upload area or drag & drop your CSV/XLSX file
   - Supported formats: CSV, XLSX, JSON, SQL, XML
   - Maximum file size: 20MB

2. **Ask Questions**
   - Type natural language questions about your data
   - Examples:
     - "Show me the distribution of sales by region"
     - "Create a correlation matrix for numerical columns"
     - "What are the top 10 products by revenue?"

3. **Interactive Analysis**
   - Review generated insights and visualizations
   - Ask follow-up questions based on the results
   - Export or save generated charts

### Advanced Features

- **Code Generation**: View the Python code used for analysis
- **Multiple Datasets**: Upload and analyze multiple files simultaneously
- **Image Analysis**: Upload images for AI-powered analysis
- **Export Results**: Save generated visualizations and insights

## Development

### Frontend Development

```bash
cd client

# Development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

### Backend Development

```bash
cd server

# Run with development settings
python app.py

# Run tests
python -m pytest

# Install new dependencies
pip install <package-name>
pip freeze > requirements.txt
```

### Key Technologies

**Frontend:**
- React 18 with Hooks
- Vite for build tooling
- TailwindCSS for styling
- Plotly.js for interactive charts
- React Markdown for rich text
- Syntax highlighting for code blocks

**Backend:**
- Flask web framework
- Google Generative AI (Gemini)
- Pandas for data manipulation
- Matplotlib & Plotly for visualizations
- Flask-CORS for cross-origin requests

## Configuration

### Customizing the AI Agent

Edit `server/utils/prompts.py` to customize the AI agent's behavior:
- System prompts
- Response formatting
- Analysis workflow
- Visualization preferences

### API Endpoints

- `GET /health` - Health check
- `POST /chat` - Main chat interface
- `POST /upload` - File upload
- `GET /query/text` - Text-only queries
- `GET /query/code` - Code generation
- `GET /history` - Chat history

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your Gemini API key is valid and properly configured
   - Check both backend config.json and frontend .env files

2. **File Upload Issues**
   - Verify file format is supported
   - Check file size (max 20MB)
   - Ensure server has write permissions for uploads directory

3. **Import Errors**
   - Activate virtual environment before running
   - Install all requirements: `pip install -r requirements.txt`

4. **CORS Issues**
   - Ensure Flask-CORS is installed
   - Check if both frontend and backend are running on correct ports

### Performance Tips

- Use smaller datasets for faster analysis
- Clear chat history periodically
- Close browser tabs not in use for better performance

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for powerful language model capabilities
- Plotly.js for interactive visualizations
- React community for excellent tooling and libraries
- Flask community for lightweight web framework

## Support

For support, issues, or feature requests:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the documentation and examples

---

**Built with ❤️ using React, Flask, and Google Gemini AI**
