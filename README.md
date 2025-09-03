Remove any leading whitespace from the very first line of README.md

This Flask-based web application provides interactive visualizations and analysis of COVID-19 data, including vaccination progress, case trends, and geographic comparisons.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone this repository or download the source code to your local machine.

2. Create a virtual environment (recommended):
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install the required packages using pip:
```bash
pip install -r requirements.txt
```

This will install all necessary dependencies including:
- Flask (web framework)
- Pandas (data manipulation)
- Matplotlib (data visualization)
- NumPy (numerical computations)
- Requests (HTTP requests)
- Plotly (interactive plots)
- Seaborn (statistical visualizations)

## Running the Application

1. Ensure you're in the project directory and your virtual environment is activated.

2. Start the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:8000
```

The application will automatically fetch the latest COVID-19 data and generate visualizations.

## Features

- Global COVID-19 case trends with 7-day moving average
- Vaccination progress comparison across countries
- Geographic comparison of cases vs GDP
- Interactive data visualizations
- Real-time data updates from Our World in Data

## Data Source

The application uses data from Our World in Data's COVID-19 dataset, which is automatically fetched when the application runs.

## Troubleshooting

If you encounter any issues:

1. Make sure all requirements are installed:
```bash
pip install -r requirements.txt --upgrade
```

2. Check if your Python version is compatible:
```bash
python --version
```

3. Ensure you have sufficient disk space for data storage and image generation.

4. If you see any matplotlib-related errors, try running:
```bash
python -c "import matplotlib.pyplot as plt"
```
to verify the installation.

## Contributing

Feel free to submit issues and enhancement requests!
