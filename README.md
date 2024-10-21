# Convin Assignment - Daily Expenses Sharing Application

This project is part of the backend intern task for Convin. It is a daily-expenses sharing application that allows users to split expenses using three methods: exact amounts, percentages, and equal splits. The project manages user and expense details, validates inputs, and generates downloadable balance sheets.

## Tech Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL
- **API**: Django REST Framework (DRF)
- **Environment**: Docker for containerization
- **PDF Generation**: ReportLab for balance sheets

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/MeetK208/convin-expense-tracker.git
```

### 2. Create a Virtual Environment

```bash
python -m venv convinEnv
```

### 3. Activate the Virtual Environment

- For Windows:

  ```bash
  .\convinEnv\Scripts\Activate
  ```

- For macOS/Linux:

  ```bash
  source convinEnv/bin/activate
  ```

### 4. Install Project Dependencies

```bash
pip install -r requirements.txt
```

### 5. Navigate to the Main Application Folder

```bash
cd expense-sharing-app
```

### 6. Apply Database Migrations

Run the migrations to set up the database:

```bash
python manage.py migrate
```

### 8. Run the Application

Start the Django server:

```bash
python manage.py runserver
```

## Features

- **User Management**: Create users with email, name, and mobile number.
- **Expense Management**: Add expenses and split them by equal, exact, or percentage methods.
- **Balance Sheet**: Generate a downloadable balance sheet for individual or overall expenses.

## API Documentation

    API Documentation Link[APIs Doc](/API_DOC.md).

## Screenshots

    APIs Screesnhots[APIs Output ScreenShots](output.md)

## Notes

- Ensure that Python 3.8+ is installed.

---

This setup file should help you run and test your Convin assignment with clear instructions.
