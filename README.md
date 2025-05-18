# String Reverser Application

A simple web application that demonstrates a React frontend communicating with a Python backend server. The application allows users to reverse strings using a Model Context Protocol (MCP) server.

## Prerequisites

- Python 3.10 or higher
- Node.js and npm
- pip (Python package manager)

## Installation

### Backend Setup

1. Install the required Python package:
```bash
pip install "mcp[cli]"
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
npm install
```

## Running the Application

### 1. Start the Backend Server

Run the Python MCP server:
```bash
python mcp_server.py
```
The server will start and be available at `http://localhost:8080`

### 2. Start the Frontend Development Server

In a new terminal window, run:
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`

## Accessing the Application

1. Open your web browser
2. Navigate to `http://localhost:5173`
3. The application should now be running with the frontend communicating with the backend server

## Server Status

- Backend Server: `http://localhost:8080`
- Frontend Server: `http://localhost:5173`

## Features

- String reversal functionality
- Real-time communication between frontend and backend
- CORS-enabled API endpoints
- Modern React frontend with Vite
- Python MCP server implementation 