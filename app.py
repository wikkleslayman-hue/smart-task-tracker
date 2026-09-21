from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from ai import suggest_task_improvement
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SECRET_KEY'] = 'supersecret'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.Date)
    done = db.Column(db.Boolean, default=False)

@app.route("/")
def index():
    tasks = Task.query.all()
    completed = sum(1 for t in tasks if t.done)
    progress = int((completed / len(tasks)) * 100) if tasks else 0
    current_date = date.today()
    return render_template("index.html", tasks=tasks, progress=progress, current_date=current_date)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")
    category = request.form.get("category")
    end_date_str = request.form.get("end_date")

    if not title:
        flash("Task must have a title!", "danger")
        return redirect(url_for("index"))

    end_date = None
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            end_date = None

    new_task = Task(title=title, category=category, end_date=end_date)
    db.session.add(new_task)
    db.session.commit()
    flash("Task added successfully!", "success")
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.done = True
    db.session.commit()
    flash("Task marked as completed!", "info")
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "warning")
    return redirect(url_for("index"))
# Try a new AI like groqe #
@app.route("/ai_suggest/<int:task_id>")
def ai_suggest(task_id):
    task = Task.query.get_or_404(task_id)
    suggestion = suggest_task_improvement(task.title, task.category)
    return render_template("index.html",
                           tasks=Task.query.all(),
                           progress=0,
                           current_date=date.today(),
                           ai_suggestion=suggestion)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
