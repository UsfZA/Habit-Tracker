# Django Habit Tracker

Django Habit Tracker is a web application designed to help users track their habits, manage tasks, and monitor progress towards their goals.
This README provides an overview of the project's features, installation instructions, usage guidelines, and contribution guidelines.

## Installation

To install and run Django Habit Tracker locally, follow these steps:

1. clone the repository
```
git clone https://github.com/UsfZA/habit_project.git
cd habit_project
```

3. Install dependencies:
```
pip install -r requirements.txt
```
  ### Database configuration

3. copy the '**local_settings.example.py**' and rename it to local_settings.py.
4. Update the database configuration in '**local_settings.py**' with your own database credentials.


5. Apply database migrations:
```
python manage.py migrate
```

6. Run the development server:
```
python manage.py runserver
```

7. Access the application in your web browser at [http://localhost:8000](url)

## Features
### 1. User Authentication and Registration: ###
  * Users can create accounts and log in to track their habits.
### 2. Habit Tracking: ###
  * Add, update, and delete habits.
  * Tasks are automatically generated based on habit goal, frequency and period.
  * Track streaks for each habit to maintain consistency.
  * Earn achievements for hitting streak milestones or completing habits.
### 3. Analytics: ###
  * View detailed analytics on habit tracking, including active habits, streak lengths, and progress towards goals.
  * Visualize habit data to gain insights into behavior patterns.
### 4. User Profile: ###
  * Users have personalized profiles displaying their active habits and other relevant information.

## Usage ##
Once the application is running, you can perform the following actions: 

### * Register/Login: ###
  * Create an account or log in with existing credentials.
### * View and Mark tasks as completed : ###
  * View due today tasks and active tasks.
  * Mark tasks as completed by clicking on them
### 


Navigate to the "Add Habit" page and input details such as habit name, frequency, period, and goal.
