# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| GET    | `/announcements`                                                  | Get active announcements for public display                         |
| GET    | `/announcements/manage?username=teacher_username`                 | Get all announcements for signed-in users                           |
| POST   | `/announcements?username=teacher_username&title=...&message=...&expiration_date=YYYY-MM-DD&start_date=YYYY-MM-DD(optional)` | Create an announcement |
| PUT    | `/announcements/{announcement_id}?username=teacher_username&title=...&message=...&expiration_date=YYYY-MM-DD&start_date=YYYY-MM-DD(optional)` | Update an announcement |
| DELETE | `/announcements/{announcement_id}?username=teacher_username`      | Delete an announcement                                              |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
