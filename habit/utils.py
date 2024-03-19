def periodicty_number(period):
        """
        Function to transform period to number of days
        args: periodicity string
        return: corresponding number of days
        """
        if period == 'daily':
            num_of_period = 1
        elif period == 'weekly':
            num_of_period = 7
        elif period == 'monthly':
            num_of_period = 30
        elif period == 'annual':
            num_of_period = 365
        
        return num_of_period

def calculate_progress(habits):
    # Calculate progress percentage for each active habit
    for habit in habits:
        if habit.num_of_tasks > 0:
            habit.progress_percentage = round((habit.num_of_completed_tasks / habit.num_of_tasks) * 100, 2)
        else:
            habit.progress_percentage = 0.0