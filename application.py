from flask import Flask, request, render_template, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'superdupersecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myAppDatabase.db'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'LogIn'


class User(UserMixin, db.Model):
    id          = db.Column(db.Integer, primary_key = True)
    username    = db.Column(db.String(15), unique = True)
    password   = db.Column(db.String(30))
    first_name   = db.Column(db.String(30))
    TicTacToe = db.relationship('TicTacToeLeaderboard', backref='TicTacToeScore')
    Snake = db.relationship('SnakeLeaderboard', backref='SnakeScore')
    BrickBreaker = db.relationship('BrickBreakerLeaderboard', backref='BrickBreakerScore')

    def __init__(self, username, password, first_name):
        self.username   = username
        self.password   = password
        self.first_name  = first_name


class TicTacToeLeaderboard(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, score):
        self.score = score



class SnakeLeaderboard(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, score):
        self.score = score



class BrickBreakerLeaderboard(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, score):
        self.score = score



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=30)])
    remember = BooleanField('Remember Me')


class RegistorForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=30)])
    first_name = StringField('First name', validators=[InputRequired(), Length(max=30)])


@app.route('/')
def index():
    if current_user.is_authenticated:
        name=current_user.first_name
        userID=current_user.id
        TLeaderboard = TicTacToeLeaderboard.query.all()
    else:
        name="Guest"
    return render_template("index.html", name=name)



@app.route('/LogIn', methods = ['GET', 'POST'])
def LogIn():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)


                return redirect('/')

    return render_template('logIn.html', form=form)


@app.route('/SignUp', methods = ['GET', 'POST'])
def SignUp():
    form = RegistorForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password, first_name=form.first_name.data)
        TicTacToeUserScore = TicTacToeLeaderboard(0)
        SnakeUserScore = SnakeLeaderboard(0)
        BrickBreakerUserScore = BrickBreakerLeaderboard(0)

        db.session.add(TicTacToeUserScore)
        db.session.add(SnakeUserScore)
        db.session.add(BrickBreakerUserScore)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('LogIn'))

    return render_template("signUp.html", form=form)


@app.route('/LogOut')
@login_required
def LogOut():
    logout_user()
    return redirect('/')



@app.route('/AboutWebsite')
def aboutSite():
    if current_user.is_authenticated:
        name=current_user.first_name
        userID=current_user.id
    else:
        name="Guest"
        userID=1

    return render_template("aboutWebsite.html", name=name, userID=userID)

@app.route('/TicTacToe')
@login_required
def TicTacToe():
    if current_user.is_authenticated:
        name=current_user.first_name
        userID=current_user.id
        currentUserTicTacToeScore = TicTacToeLeaderboard.query.get(int(userID))
    else:
        name="Guest"
    return render_template("tictactoe.html", name=name, userID=userID, currentUserTicTacToeScore=currentUserTicTacToeScore)


@app.route('/UpdateTicTacToeScore', methods=['POST'])
def UpdateTicTacToeScore():
    TicTacToeScore = request.form["TicTacToeFormScore"]

    userID=current_user.id

    TicTacToeHigh = TicTacToeLeaderboard.query.get(userID)
    TicTacToeHigh.score = TicTacToeScore

    db.session.commit()

    return redirect( '/TicTacToe' )


@app.route('/SnakeGame')
@login_required
def SnakeGame():
    if current_user.is_authenticated:
        name=current_user.first_name
        userID=current_user.id
        currentUserSnakeScore = SnakeLeaderboard.query.get(int(userID))
    else:
        name="Guest"
    return render_template("snakeGame.html", name=name, userID=userID, currentUserSnakeScore=currentUserSnakeScore)


@app.route('/UpdateSnakeScore', methods=['POST'])
def UpdateSnakeScore():
    SnakeScore = request.form["SnakeFormScore"]

    userID=current_user.id

    SnakeHigh = SnakeLeaderboard.query.get(userID)
    SnakeHigh.score = SnakeScore

    db.session.commit()

    return redirect( '/SnakeGame' )




@app.route('/BrickBreakerGame')
@login_required
def BrickBreakerGame():
    if current_user.is_authenticated:
        name=current_user.first_name
        userID=current_user.id
        currentUserBrickBreakerScore = BrickBreakerLeaderboard.query.get(int(userID))
    else:
        name="Guest"
    return render_template("brickBreakerGame.html", name=name, userID=userID, currentUserBrickBreakerScore=currentUserBrickBreakerScore)


@app.route('/UpdateBrickBreakerScore', methods=['POST'])
def UpdateBrickBreakerScore():
    BrickBreakerScore = request.form["BrickBreakerFormScore"]

    userID=current_user.id

    BrickBreakerHigh = BrickBreakerLeaderboard.query.get(userID)
    BrickBreakerHigh.score = BrickBreakerScore

    db.session.commit()

    return redirect( '/BrickBreakerGame' )



@app.route('/TicTacToeTutorial')
def TicTacToeGameTutorial():
    if current_user.is_authenticated:
        name=current_user.first_name
    else:
        name="Guest"
    return render_template('ticTacToeTutorial.html', name=name)


@app.route('/SnakeTutorial')
def SnakeGameTutorail():
    if current_user.is_authenticated:
        name=current_user.first_name
    else:
        name="Guest"
    return render_template('snakeTutorial.html', name=name)


@app.route('/BrickBreakerTutorial')
def BrickBreakerGameTutorail():
    if current_user.is_authenticated:
        name=current_user.first_name
    else:
        name="Guest"
    return render_template('brickBreakerTutorial.html', name=name)


@app.route('/TicTacToeLeaderboard')
def TicTacToeGameLeaderboard():
    if current_user.is_authenticated:
        name=current_user.username
        userID=current_user.id
        leaderboard = TicTacToeLeaderboard.query.order_by(TicTacToeLeaderboard.score.desc()).all()
        allUsers=User.query.all()
    else:
        name="Guest"
    return render_template('ticTacToeLeaderboard.html', name=name, leaderboard=leaderboard, userID=userID, allUsers=allUsers)


@app.route('/SnakeLeaderboard')
def SnakeGameLeaderboard():
    if current_user.is_authenticated:
        name=current_user.first_name
        userID=current_user.id
        leaderboard = SnakeLeaderboard.query.order_by(SnakeLeaderboard.score.desc()).all()
    else:
        name="Guest"
    return render_template('snakeLeaderboard.html', name=name, leaderboard=leaderboard, userID=userID)


@app.route('/BrickBreakerLeaderboard')
def BrickBreakerGameLeaderboard():
    if current_user.is_authenticated:
        name=current_user.first_name
        userID=current_user.id
        leaderboard = BrickBreakerLeaderboard.query.order_by(BrickBreakerLeaderboard.score.desc()).all()
    else:
        name="Guest"
    return render_template('brickbreakerLeaderboard.html', name=name, leaderboard=leaderboard, userID=userID)


if __name__ == "__main__":
    app.run()