# Virtual Interview Platform

A web-based platform for conducting virtual interviews with speech recognition capabilities.

## Features
- Interactive interview interface
- Speech-to-text functionality
- Real-time question generation
- Interview results analysis

## File Structure
```
.
├── app.py                # Main Flask application
├── main.py               # Application entry point
├── groq_service.py       # Integration with Groq service
├── speech_service.py     # Speech recognition service
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── static/               # Static assets
│   ├── css/
│   │   └── style.css     # Stylesheets
│   └── js/
│       ├── main.js       # Main application logic
│       ├── interview.js  # Interview page logic
│       └── speech.js     # Speech recognition logic
└── templates/            # HTML templates
    ├── index.html        # Home page
    ├── interview.html    # Interview page
    └── results.html      # Results page
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Vishal2053/Virtual-Interview-Platform.git
cd Vertual-Interview-Platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys and configuration:
```bash
cp .env.example .env
```

## Usage

1. Start the development server:
```bash
python main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Configuration

Required environment variables (set in `.env`):
- `GROQ_API_KEY`: API key for Groq service
- `SPEECH_API_KEY`: API key for speech recognition service
- `FLASK_SECRET_KEY`: Secret key for Flask sessions

## Dependencies

See `requirements.txt` for complete list of Python dependencies.

## License

[MIT License](LICENSE) (if applicable)
