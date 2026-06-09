from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory task store (persists for container lifetime)
tasks = []

def get_task_by_id(task_id):
    return next((t for t in tasks if t['id'] == task_id), None)

@app.route('/')
def index():
    filter_by = request.args.get('filter', 'all')
    if filter_by == 'active':
        filtered = [t for t in tasks if not t['done']]
    elif filter_by == 'completed':
        filtered = [t for t in tasks if t['done']]
    else:
        filtered = tasks

    stats = {
        'total': len(tasks),
        'active': sum(1 for t in tasks if not t['done']),
        'completed': sum(1 for t in tasks if t['done']),
    }
    return render_template('index.html', tasks=filtered, filter=filter_by, stats=stats)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title', '').strip()
    priority = request.form.get('priority', 'medium')
    if title:
        tasks.append({
            'id': str(uuid.uuid4()),
            'title': title,
            'priority': priority,
            'done': False,
            'created_at': datetime.now().strftime('%b %d, %Y · %H:%M'),
        })
    return redirect(url_for('index'))

@app.route('/toggle/<task_id>', methods=['POST'])
def toggle_task(task_id):
    task = get_task_by_id(task_id)
    if task:
        task['done'] = not task['done']
    return redirect(request.referrer or url_for('index'))

@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t['id'] != task_id]
    return redirect(request.referrer or url_for('index'))

@app.route('/clear-completed', methods=['POST'])
def clear_completed():
    global tasks
    tasks = [t for t in tasks if not t['done']]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)