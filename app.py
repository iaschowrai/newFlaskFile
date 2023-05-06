from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user,UserMixin

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators,SelectField,SubmitField,  TextAreaField,EmailField
import requests
from enum import Enum

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mscs3150'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[validators.DataRequired(), validators.EqualTo('password', message='Passwords must match')])
    user_type = SelectField('User Type', choices=[('Employer', 'Employer'), ('JobSeeker', 'JobSeeker')])
    submit = SubmitField('Register')

class JobForm(FlaskForm):
    title = StringField('Title', validators=[validators.DataRequired()])
    salary = StringField('Salary')
    company = StringField('Company', validators=[validators.DataRequired()])
    category = SelectField('Category', choices=[('FullTime', 'FullTime'), ('PartTime', 'PartTime'),('Contract', 'Contract')])
    description = TextAreaField('Description', validators=[validators.DataRequired()])
    email = EmailField('Email', validators=[validators.DataRequired()])
    submit = SubmitField('AddPost')

#*******************************************************************************
#Authentication
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        # self.usertype = usertype

    def __repr__(self):
        return f'<User {self.id}>'


@login_manager.user_loader
def load_user(user_id):
    # Load the user from the database
    return User(user_id)



@app.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def profile(user_id):
    if request.method == 'GET':
        response = requests.get(f'http://localhost:5001/api/profile/{user_id}')
        user_data = response.json() # extract JSON data from response object
        print(user_data)  # print the JSON data
    return render_template('profile.html', title='Profile', user_data=user_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        response = requests.post('http://localhost:5001/api/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            user_id = response.json()['id']
            # usertype = response.json()['user_type']
            user = User(user_id)
            login_user(user)
            flash('Login successful!')
            return redirect('/')
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_type= form.user_type.data
        response = requests.post('http://localhost:5001/api/register', json={'username': username, 'password': password, 'user_type': user_type})
        if response.status_code == 201:
            flash('Registration successful! Please log in.')
            return redirect('/login')
        else:
            flash('Username already taken.')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))



#*******************************************************************************



@app.route('/jobs', methods=['GET', 'POST'])
def addpost():
    form = JobForm()
    if form.validate_on_submit():
        title = form.title.data
        salary = form.salary.data
        company = form.company.data
        category = form.category.data
        description = form.description.data
        email= form.email.data
        response = requests.post('http://localhost:5001/api/jobs', json={'title' :title, 'salary':  salary, 'company': company, 'category': category, 'description': description, 'email': email})
        if response.status_code == 201:
            flash('Job Posted!')
            return redirect('/aboutme')
        else:
            flash('Job Not Posted Something wrong!')
    return render_template('create.html', form=form)

@app.route('/jobs/<int:job_id>', methods=['GET','PUT', 'DELETE'])
def view(job_id):
    # if request.method == 'GET':
    #     response = requests.post('http://localhost:5001/api/jobs/'+ f'/{job_id}', json={'filled': True })
    # return render_template('view.html', title= 'view', form=response)
    if request.method == 'GET':
        response = requests.get(f'http://localhost:5001/api/jobs/{job_id}')
        job_data = response.json() # extract JSON data from response object
        return render_template('view.html', title='Job Details', job=job_data)
    elif request.method == 'PUT':
        response = requests.put(f'http://localhost:5001/api/jobs/{job_id}')
        job_data = response.json() # extract JSON data from response object
        return render_template('view.html', title='Job Details', job=job_data)        
    elif request.method == 'DELETE':
        # handle DELETE request
        pass    

@app.route('/jobs/<int:job_id>', methods=['PUT'])
def putview(job_id):   
    if request.method == 'PUT':
        response = requests.put(f'http://localhost:5001/api/jobs/{job_id}')
        job_data = response.json() # extract JSON data from response object
        return render_template('view.html', title='Job Details', job=job_data)           


@app.route('/aboutme', methods=['GET', 'POST'])
def aboutme():
    if request.method == 'GET':
        response = requests.get('http://localhost:5001/api/jobs')
        jobs = response.json()
        keyword = request.args.get('search_key', '').lower()
        print(keyword)
        # keyword = 'vfj'
        results = []
        for job in jobs:
            if keyword in job['title'].lower() or keyword in job['description'].lower():
                results.append(job)
        print(results)
        if len(results) > 0:
            jobs = results
        # print(jobs)
        return render_template('aboutme.html', forms = jobs)                      

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        response = requests.get('http://localhost:5001/api/jobs')
        jobs = response.json()
        keyword = request.args.get('search_key', '').lower()
        print(keyword)
        # keyword = 'vfj'
        results = []
        for job in jobs:
            if keyword in job['title'].lower() or keyword in job['description'].lower():
                results.append(job)
        print(results)
        if len(results) > 0:
            jobs = results
        # print(jobs)
        return render_template('index.html', forms = jobs) 
    
@app.route('/<category>', methods=['GET', 'POST'])
def cat(category):
    if request.method == 'GET':
        response = requests.get('http://localhost:5001/api/jobs')
        jobs = response.json()
        print(category)
        if category is not None:
            jobs = [job for job in jobs if job['category'] == str(category)]
        print(jobs)
        return render_template('index.html', forms=jobs)
    
    
# @app.route('/<keyword>', methods=['GET', 'POST'])
# def search(keyword):
#     if request.method == 'GET':
#         response = requests.get('http://localhost:5001/api/jobs')
#         jobs = response.json()
#         print(keyword)
#         # if keyword is not None:
#         #     jobs = [job for job in jobs if job['category'] == str(keyword)]
#         print(jobs)
#         return render_template('index.html', forms=jobs)





# @app.route('/aboutme', method=['GET', 'POST'])
# def aboutme():
#     return render_template('aboutme.html', title='aboutme')




# @app.route('/profile')
# def profile():
#     if current_user.is_authenticated:
#         return render_template('profile.html', title='profile')
#     else:
#         return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
