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
├── .git/                   # Git version control
├── .gitignore             # Git ignore rules
├── .vscode/               # VS Code workspace settings
├── LICENSE                # Project license
├── README.md              # Project documentation
│
├── client/                 # React frontend application
│   ├── src/
│   │   ├── App.jsx        # Main application component
│   │   ├── main.jsx       # Application entry point
│   │   ├── index.css      # Global styles
│   │   ├── components/    # Reusable UI components
│   │   │   ├── ChatInput.jsx
│   │   │   ├── ChatMessage.jsx
│   │   │   ├── ChatMessageList.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── StorageStats.jsx
│   │   ├── models/        # Data models
│   │   │   └── ChatModels.js
│   │   ├── services/      # API and storage services
│   │   │   ├── ApiService.js
│   │   │   └── StorageService.js
│   │   ├── viewmodels/    # Business logic layer
│   │   │   └── ChatViewModel.js
│   │   └── views/         # Main view components
│   │       └── ChatView.jsx
│   ├── public/            # Static assets
│   │   ├── gemini_icon.png
│   │   ├── logo.png
│   │   └── user_icon.png
│   ├── package.json       # Frontend dependencies
│   ├── vite.config.js     # Vite configuration
│   ├── eslint.config.js   # ESLint configuration
│   └── index.html         # HTML template
│
└── server/                 # Flask backend application
    ├── .env               # Environment variables (create this file)
    ├── app.py             # Main Flask application
    ├── config.py          # Configuration management
    ├── requirements.txt   # Backend dependencies
    ├── controllers/       # Request handlers
    │   ├── __init__.py
    │   ├── chat_controller.py
    │   └── file_controller.py
    ├── models/            # Data models
    │   ├── __init__.py
    │   └── chat_models.py
    ├── services/          # Business logic services
    │   ├── __init__.py
    │   ├── gemini_service.py
    │   ├── file_service.py
    │   ├── plot_context_service.py
    │   ├── response_service.py
    │   └── sequential_workflow_service.py
    ├── utils/             # Utility functions
    │   ├── __init__.py
    │   ├── code_executor.py
    │   ├── dataset_manager.py
    │   ├── file_upload_cache.py
    │   ├── gemini_factory.py
    │   ├── prompts.py
    │   ├── response_formatter.py
    │   └── cache/         # Cache directory
    └── datasets/          # Sample datasets
        ├── Iris.csv
        ├── test_data.csv
        └── train.csv
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
   
   **Backend Configuration** - Create `server/.env`:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd server
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Run the Flask application
   python app.py
   ```
   The Flask server will run on `http://localhost:5000`

2. **Start the Frontend Development Server**
   ```bash
   cd client
   npm run dev
   ```

3. **Access the Application**
   Open your browser and navigate to the link provided by Vite (usually `http://localhost:5173`)

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
- React 18 with Hooks and modern JSX
- Vite for fast build tooling and development
- TailwindCSS 4.x for modern styling
- Plotly.js for interactive charts and visualizations
- React Markdown for rich text rendering
- React Syntax Highlighter for code blocks
- Axios for HTTP requests

**Backend:**
- Flask 3.x web framework
- Google Generative AI (Gemini 2.0 Flash)
- Python-dotenv for environment management
- Pandas for data manipulation and analysis
- Matplotlib & Plotly for static and interactive visualizations
- Seaborn for statistical data visualization
- Flask-CORS for cross-origin requests
- Pillow for image processing

## Configuration

### Customizing the AI Agent

Edit `server/utils/prompts.py` to customize the AI agent's behavior:
- System prompts
- Response formatting
- Analysis workflow
- Visualization preferences

### Configuration Management

The application uses `server/config.py` for centralized configuration management:
- Environment variables loading
- API key management
- Application settings
- File upload configurations

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
   - Ensure your Gemini API key is valid and properly configured in `server/.env`
   - Check that the `.env` file is in the correct location
   - Verify the environment variables are being loaded correctly

2. **File Upload Issues**
   - Verify file format is supported (CSV, XLSX, JSON, SQL, XML)
   - Check file size (max 20MB)
   - Ensure server has write permissions for uploads directory
   - Check the `cache/` directory in `server/utils/`

3. **Import Errors**
   - Activate virtual environment before running: `venv\Scripts\activate` (Windows)
   - Install all requirements: `pip install -r requirements.txt`
   - Verify Python version compatibility (3.8+)

4. **CORS Issues**
   - Ensure Flask-CORS is installed and configured
   - Check if both frontend (port 5173) and backend (port 5000) are running
   - Verify CORS settings in Flask application

5. **Build Issues**
   - Clear node_modules and reinstall: `npm ci`
   - Check Node.js version (v16+)
   - Clear Vite cache: `npm run dev -- --force`

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
