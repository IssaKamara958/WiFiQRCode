# WiFi QR Code Scanner

## Overview

A Flask-based web application that scans WiFi QR codes from uploaded images or webcam input and extracts network credentials. The application provides a user-friendly interface for uploading QR code images, parsing WiFi network information (SSID, password, security type), and on Windows systems, can automatically configure WiFi profiles using netsh commands. The app features a responsive Bootstrap frontend with drag-and-drop file upload capabilities and real-time scanning feedback.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

**Frontend Architecture:**
- Single-page application using vanilla JavaScript with Bootstrap 5 for UI components
- Responsive design with drag-and-drop file upload interface
- Real-time progress feedback and toast notifications
- Webcam integration for live QR code scanning (browser-based)

**Backend Architecture:**
- Flask web framework serving as the main application server
- Modular design with separate WiFiQRScanner class for QR code processing
- RESTful API endpoints for file upload and processing
- File upload handling with security validation and unique filename generation

**QR Code Processing:**
- OpenCV (cv2) for image processing and computer vision operations
- pyzbar library for QR code detection and decoding
- Custom WiFi QR code parser that handles standard WIFI: format strings
- Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP, WebP)

**Platform Integration:**
- Windows-specific netsh integration for automatic WiFi profile creation
- XML profile generation for Windows network configuration
- Cross-platform compatibility with feature detection

**Security Measures:**
- File type validation using allowed extensions whitelist
- Secure filename generation using werkzeug.utils.secure_filename
- UUID-based unique filename generation to prevent conflicts
- File size limits (16MB maximum)
- Server-side validation for all uploaded content

**Error Handling:**
- Comprehensive exception handling with user-friendly error messages
- Input validation for QR code format verification
- Graceful fallback for unsupported platforms or operations

## External Dependencies

**Core Web Framework:**
- Flask - Python web framework for server-side application logic
- Werkzeug - WSGI utilities for secure file handling

**Computer Vision & QR Processing:**
- OpenCV (cv2) - Image processing and computer vision operations
- pyzbar - QR code and barcode detection library

**Frontend Libraries:**
- Bootstrap 5.1.3 - CSS framework for responsive UI design
- Font Awesome 6.0.0 - Icon library for user interface elements

**File Handling:**
- tempfile - Temporary file management for processing
- uuid - Unique identifier generation for uploaded files
- xml.etree.ElementTree - XML parsing and generation for Windows profiles

**System Integration:**
- subprocess - System command execution for netsh operations
- platform - Operating system detection for Windows-specific features

**Standard Libraries:**
- os - File system operations and environment variable handling
- re - Regular expression processing for QR data parsing
- json - Data serialization for API responses