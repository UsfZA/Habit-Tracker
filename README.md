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

3. Install dependencies:
```
pip install -r requirements.txt
```
  ### Database configuration ###
I'm using Mysql as database so i included mysqlclient in requirements

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

# Features #
### User Authentication and Registration: ###
  * Users can create accounts and log in to track their habits.
### Habit Tracking: ###
  * Add, update, and delete habits.
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
     * Update habits to modify details such as name, frequency, period, or goal.
# Acknowledgments #
We would like to thank the Django community for their excellent documentation and support.
