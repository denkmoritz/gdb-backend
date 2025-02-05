# Backend Setup

## Prerequisites
- Python 3.11
- pip3
- Docker & Docker Compose

## Database Setup
1. Download the database from the following link:
   [Database Download](https://drive.google.com/file/d/1bZi7EonNZ9Knj2d9J0x06zdat4YWGszP/view?usp=sharing)
2. Place the downloaded database file in the appropriate folder.
3. Navigate to the folder in your terminal and run the following commands:
   ```sh
   docker compose build
   docker compose up
   ```

## Backend Setup
1. Create a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. Install dependencies:
   ```sh
   pip3 install -r requirements.txt
   ```
3. Run the `add_adm.py` file once before starting the backend:
   ```sh
   python3 add_adm.py
   ```
4. Start the backend:
   ```sh
   python3 app.py
   ```

## Dependencies
The backend relies on the following packages (as listed in `requirements.txt`):
- Flask
- flask-cors
- psycopg2
- geopandas
- sqlalchemy
- geoalchemy2

## Notes
- Ensure Docker is running before starting the backend.
- If you encounter issues with database connection, verify that the database is correctly set up in Docker.
- The backend is developed using Python 3.11, so ensure compatibility with your environment.