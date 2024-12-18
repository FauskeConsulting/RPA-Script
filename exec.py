import tkinter as tk
from tkinter import messagebox
import threading
import time
from datetime import datetime, timedelta
import schedule
import io
from main import main, log_message
# Global variables
is_running = False
logs = io.StringIO()
execution_start_time = None
successful_runs = 0
failed_runs = 0  


def main_with_logging():
    """Main function with logging."""
    global execution_start_time,successful_runs,failed_runs
    execution_start_time = datetime.now()
    log_message("Execution started.",logs)
    try:
        exec = main(logs)  # Call the main script
        if exec==0:
            log_message("Execution failed",logs)
            update_run_counters()  # Update GUI labels

            failed_runs=failed_runs+1
        else:
            log_message("Execution completed successfully.",logs)
            update_run_counters()  # Update GUI labels
            successful_runs = successful_runs+1
    except Exception as e:
        log_message(f"Error during execution: {e}",logs)
    execution_start_time = None

def start_scheduler():
    """Start the scheduler."""
    global is_running
    is_running = True
    log_message("Scheduler started.",logs)
    while is_running:
        schedule.run_pending()
        time.sleep(1)

def toggle_scheduler():
    """Start or stop the scheduler."""
    global is_running, scheduler_thread

    if not is_running:
        # Start the scheduler
        schedule.every(2).minutes.do(run_if_within_window)
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
        start_button.config(text="Stop")
        log_message("Scheduler started.",logs)
    else:
        # Stop the scheduler
        is_running = False
        start_button.config(text="Start")
        log_message("Scheduler stopped.",logs)
def update_run_counters():
    """Update the run counters displayed in the GUI."""
    successful_label.config(text=f"Successful Runs: {successful_runs}")
    failed_label.config(text=f"Failed Runs: {failed_runs}")

def run_if_within_window():
    """Check if within time window and execute the script."""
    log_message("Checking if scheduler is within the 5 minute time window...",logs)
    if is_within_time_window():
        log_message("Check complete. Inside the time window. Execution starting....",logs)
        main_with_logging()
    else:
        log_message("Skipped execution: Outside the time window.",logs)

def is_within_time_window():
    """Check if the current time is between 7 AM GMT and 5 AM GMT the next day."""
    now = datetime.utcnow()
    start_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=5, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    if now < start_time:  # If it's before 7 AM, consider yesterday's window
        start_time -= timedelta(days=1)
    return start_time <= now <= end_time

def show_logs():
    """Display the logs in a new window."""
    log_content = logs.getvalue()
    log_window = tk.Toplevel(root)
    log_window.title("Logs")
    log_text = tk.Text(log_window, wrap="word", width=80, height=20)
    log_text.insert("1.0", log_content)
    log_text.config(state="disabled")  # Make logs read-only
    log_text.pack(fill="both", expand=True)

def update_timer():
    """Update the timer display."""
    if execution_start_time:
        elapsed_time = datetime.now() - execution_start_time
        elapsed_label.config(text=f"Time since execution: {str(elapsed_time).split('.')[0]}")
    else:
        elapsed_label.config(text="Time since execution: N/A")
    root.after(1000, update_timer)
# GUI Setup
root = tk.Tk()
root.title("Scheduler GUI")

start_button = tk.Button(root, text="Start", command=toggle_scheduler, width=20)
start_button.pack(pady=10)

log_button = tk.Button(root, text="Show Logs", command=show_logs, width=20)
log_button.pack(pady=10)

elapsed_label = tk.Label(root, text="Time since execution: N/A")
elapsed_label.pack(pady=10)

successful_label = tk.Label(root, text=f"Successful Runs: {successful_runs}", font=("Arial", 12))
successful_label.pack(pady=5)

failed_label = tk.Label(root, text=f"Failed Runs: {failed_runs}", font=("Arial", 12))
failed_label.pack(pady=5)
# Start the timer updater
update_timer()

root.mainloop()
