import os
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from config import Config
from model import Todo, db
from flask_migrate import Migrate

app = Flask(__name__)

# SQLite Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "todos.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for flash messages

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Create tables within app context
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")
        if title and desc:
            new_todo = Todo(title=title, desc=desc, date_created=datetime.now())
            db.session.add(new_todo)
            db.session.commit()
            flash("Todo added successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Please provide both title and description.", "error")

    all_todos = Todo.query.order_by(Todo.date_created.desc()).all()
    return render_template("index.html", all_todos=all_todos)

@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    todo = Todo.query.get_or_404(sno)
    if request.method == "POST":
        title = request.form.get("title")
        desc = request.form.get("desc")
        if title and desc:
            todo.title = title
            todo.desc = desc
            db.session.commit()
            flash("Todo updated successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Please provide both title and description.", "error")

    return render_template("update.html", todo=todo)

@app.route("/toggle/<int:sno>")
def toggle(sno):
    todo = Todo.query.get_or_404(sno)
    todo.completed = not todo.completed
    db.session.commit()
    flash(f"Todo marked as {'completed' if todo.completed else 'incomplete'}!", "success")
    return redirect(url_for("index"))

@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.get_or_404(sno)
    db.session.delete(todo)
    db.session.commit()
    flash("Todo deleted successfully!", "success")
    return redirect(url_for("index"))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)

