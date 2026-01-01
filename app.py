from flask import Flask, render_template, request, redirect, url_for
import smtplib
import schedule
import time
import threading
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
tasks = []
reminders = {}

sender_email = 'Your mail id'  
sender_password = 'Your app password' 

def send_email(to_email, subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Reminder email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_reminder():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    for (email, task_name), reminder_time in list(reminders.items()):
        if reminder_time == now:
            send_email(email, "Task Reminder", f"Reminder: It's time to do your task: {task_name}")
            del reminders[(email, task_name)] 

def schedule_reminders():
    while True:
        schedule.run_pending()
        time.sleep(60) 

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task')
    task_email = request.form.get('email')
    reminder_time = request.form.get('reminder_time')

    if task_name and task_email:
        tasks.append(task_name)
      
        if reminder_time:
            reminder_time_str = f"{datetime.now().strftime('%Y-%m-%d')} {reminder_time}"  
            reminders[(task_email, task_name)] = reminder_time_str
            schedule.every().day.at(reminder_time).do(send_email, task_email)

    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update_task():
    old_task_name = request.form.get('old_task')
    new_task_name = request.form.get('new_task')
    if old_task_name in tasks:
        tasks[tasks.index(old_task_name)] = new_task_name
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_task():
    task_name = request.form.get('task')
    if task_name in tasks:
        tasks.remove(task_name)
    return redirect(url_for('index'))

if __name__ == '__main__':
    threading.Thread(target=schedule_reminders, daemon=True).start()

    app.run(debug=True)
