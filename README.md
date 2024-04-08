# Django Habit Tracker

Django Habit Tracker is a web application designed to help users track their habits, manage tasks, and monitor progress towards their goals.
This README provides an overview of the project's features, installation instructions, usage guidelines, and contribution guidelines.

# Installation #

To install and run Django Habit Tracker locally, follow these steps:

1. clone the repository
```
git clone https://github.com/UsfZA/Habit-Tracker.git
cd Habit-Tracker
```

2. Install dependencies:
```
pip install -r requirements.txt
```
  ### Database configuration ###
I'm using MySQL as the database, so I've included `mysqlclient` in the requirements.
If you don't have MySQL installed, you can use the built-in SQLite configuration. Follow these steps:
 
  3. Ensure you have SQLite installed on your system.
  4. Copy the '**local_settings.example.py**' file and rename it to `local_settings.py`.
  5. Update the database configuration in '**local_settings.py**' with your own database credentials.


6. Apply database migrations:
```
python manage.py migrate
```

7. Run the development server:
```
python manage.py runserver
```

8. Access the application in your web browser at [http://localhost:8000](url)

# Features #
### User Authentication and Registration: ###
  * Users can create accounts and log in to track their habits.
### Habit Tracking: ###
  * Add, and delete habits.
  * Tasks are automatically generated based on habit goal, frequency and period.
  * Track streaks for each habit to maintain consistency.
  * Earn achievements for hitting streak milestones or completing habits.
### Analytics: ###
  * View detailed analytics on habit tracking, including active habits, streak lengths, and progress towards goals.
  * Visualize habit data to gain insights into behavior patterns.
### User Profile: ###
  * Users have personalized profiles displaying their active habits and other relevant information.

# Usage #
Once the application is running, you can perform the following actions: 

### Register/Login: ###
  * Create an account or log in with existing credentials.
### Add Habits: ###
  * Navigate to the "Add Habit" page and input details such as habit name, frequency, period, and goal.
### View and Mark tasks as completed In Home page: ###
  * View due today tasks and active tasks.
  * Mark tasks as completed by clicking on them.
### Monitor Progress: ###
  * Check your analytics regularly to monitor streak lengths, progress percentages, and achievements.
### Habit Manager: ###
  * Navigate to the "Habit Manager" :
     * View all tracked habits and access their details including tasks journal and streak log for each habit
     * Delete habits along with associated tasks, streaks, and achievements.
