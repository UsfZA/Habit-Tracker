### Django Habit Tracker

Django Habit Tracker is a web application designed to help users track their habits, manage tasks, and monitor progress towards their goals.
This README provides an overview of the project's features, installation instructions, usage guidelines, and contribution guidelines.

### Installation

To install and run Django Habit Tracker locally, follow these steps:

1. clone the repository
git clone https://github.com/UsfZA/habit_project.git
cd habit_project

2. Install dependencies:
pip install -r requirements.txt

## Database configuration

3. copy the local_settings.example.py and rename it to local_settings.py.
4. Update the database configuration in 'local_settings.py' with your own database credentials.


5. Apply database migrations:
python manage.py migrate

6. Run the development server:
python manage.py runserver

7. Access the application in your web browser at http://localhost:8000
