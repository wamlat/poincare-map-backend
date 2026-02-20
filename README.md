# Poincaré Map Backend

A high-performance backend for generating Poincaré maps of the Rössler system using C++ computation.

## Requirements

- Python 3.6+
- g++ compiler (for C++ compilation)
- Flask

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/poincare-map-backend.git
   cd poincare-map-backend
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

```
python app.py
```

The server will start on port 5000 by default. You can change this by setting the PORT environment variable.

## API Endpoints

### GET /

Returns a simple message to confirm the server is running.

### POST /generate

Generates a Poincaré map for the Rössler system with the given parameters.

**Request Body:**
```json
{
  "a": 0.2,
  "b": 0.2,
  "c": 5.7
}
```

**Response:**
```json
[
  {"x": 1.234, "z": 5.678},
  {"x": 2.345, "z": 6.789},
  ...
]
```

## Performance

The backend uses a C++ implementation for numerical integration, which provides significantly better performance than pure Python solutions. If C++ compilation fails, the system will automatically fall back to a Python implementation.