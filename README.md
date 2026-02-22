# FitLog

A workout tracking web application built with Django. Log your workouts, track exercises by muscle group, monitor personal records, and visualise your progress over time.

> **Note for judges:** User authentication has been disabled for this submission to make evaluation easier. The app is fully accessible without logging in.

## Features

- Create and manage workouts with exercises and sets
- Filter exercises by muscle group when building a workout
- Automatic set numbering and order management
- Personal record detection per exercise
- Estimated 1-rep max (Epley formula) displayed per set and per exercise
- Exercise progress chart (best weight over time)
- GitHub-style workout contribution grid with streak tracking (2-day rest allowed)
- Browse 57 pre-loaded exercises across 13 muscle groups
- Add and delete custom exercises

## Tech Stack

- Python 3.12
- Django 5.x
- PostgreSQL
- Bootstrap 5
- Chart.js
- jQuery

---

## Setup Guide

### Prerequisites

Make sure you have the following installed:

- Python 3.12
- PostgreSQL
- Git

---

### 1. Clone the repository

```bash
git clone https://github.com/cukurigu/fitlog.git
cd fitlog
git checkout no-auth
```

---

### 2. Create and activate a virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file in the project root with the following:

```env
SECRET_KEY=your_secret_key_here
DEBUG=True
DB_NAME=fitlog
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

---

### 5. Set up the database

Create a PostgreSQL database:

```sql
CREATE DATABASE fitlog;
```

---

### 6. Apply migrations

```bash
python manage.py migrate
```

---

### 7. Load exercise and muscle data

```bash
python manage.py loaddata exercises/fixtures/exercises_and_muscles.json
```

This loads 13 muscle groups and 57 exercises into the database.

---

### 8. Run the development server

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Using the App

1. **Log a workout** using the `+ New Workout` button
2. Select a **muscle group** to filter the exercise dropdown, then pick an exercise
3. Add **sets** with weight and reps for each exercise
4. View your **workout history** on the home page, including the contribution grid and streak
5. Click a workout to see the **detail view** with 1RM estimates and PR badges
6. Click **📈 Progress** on any exercise to see your weight progression chart
7. Browse or add custom exercises via the **Exercises** page in the navbar

---

## Project Structure

```
fitlog/
├── accounts/         # Authentication (disabled for exam)
├── exercises/        # Exercise model, views, fixtures
├── muscles/          # Muscle group model
├── workouts/         # Workout, WorkoutExercise, WorkoutSet models and views
├── templates/        # Global base template
├── static/css/       # Static files
├── fitlog_project/   # Django project settings and URLs
├── manage.py
├── requirements.txt
└── .env              # Environment variables (create this file locally)
```
