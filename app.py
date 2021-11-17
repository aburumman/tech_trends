import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from flask import Response
from werkzeug.exceptions import abort


logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Function to get a database connection.
# This function connects to database with the name `database.db`

db_connection = 0

def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection
    db_connection += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    global db_connection
    db_connection += 1
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

 
@app.route('/blogs')
def blog():
    app.logger.info('Info level log')
    app.logger.warning('Warning level log')
    return f"Welcome to the Blog"
 
#app.run(host='localhost', debug=True)


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    global db_connection
    db_connection += 1
    connection.close()
    return render_template('index.html', posts=posts)


@app.route('/metrics')
def numpost():
    connection = get_db_connection()
    posts = connection.execute('SELECT count(*) FROM posts').fetchone()
    posts = posts[0]
    global db_connection
    response = app.response_class(
            response=json.dumps({"status":"success","post_count": posts, "db_connection_count": str(db_connection)}),
            status=200, mimetype='application/json')
    #rsp = " Total Number of Post: {} \n   Total Number of DB Connections is {}".format(posts[0], db_connection )
    return response 
    

# The healthz endpoint
@app.route('/healthz')
def healthz(): 
    response = app.response_class(response=json.dumps({'result': 'OK - healthy'}),
                                  status=200,
                                  mimetype='application/json')
    return response

    
# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    
    if post is None:
      return render_template('404.html'), 404
      app.logger.info(404)
    else:
      return render_template('post.html', post=post)
      app.logger.info("Logged the Title: " + post['title'])

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The About Us page is retieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            global db_connection
            db_connection += 1
            app.logger.info(title)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   #app.run(host='0.0.0.0', port='3111')
   app.run(debug = True, host='0.0.0.0', port='3111')
