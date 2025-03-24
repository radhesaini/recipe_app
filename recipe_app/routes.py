# recipe_app/routes.py
from flask import render_template, url_for, flash, redirect, request
from recipe_app import app, db
from recipe_app.forms import RegistrationForm, LoginForm, RecipeForm, CommentForm, RatingForm
from recipe_app.models import User, Recipe, Comment, Rating
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        print(User.query.first().email)
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/recipe/new', methods=['GET', 'POST'])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(title=form.title.data, description=form.description.data, ingredients=form.ingredients.data, instructions=form.instructions.data, author=current_user)
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_recipe.html', title='New Recipe', form=form, legend='New Recipe')

@app.route('/recipe/<int:recipe_id>', methods=['GET', 'POST'])
@login_required
def recipe_detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    comment_form = CommentForm()
    rating_form = RatingForm()

    if comment_form.validate_on_submit() and comment_form.submit_comment.data:
        comment = Comment(comment=comment_form.comment.data, user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('recipe_detail', recipe_id=recipe_id))

    if rating_form.validate_on_submit() and rating_form.submit_rating.data:
      rating = Rating(rating=rating_form.rating.data, user_id=current_user.id, recipe_id=recipe_id)
      db.session.add(rating)
      db.session.commit()
      return redirect(url_for('recipe_detail', recipe_id=recipe_id))

    comments = Comment.query.filter_by(recipe_id=recipe_id).all()
    ratings = Rating.query.filter_by(recipe_id=recipe_id).all()

    return render_template('recipe_detail.html', recipe=recipe, comment_form=comment_form, comments=comments, rating_form=rating_form, ratings=ratings)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if query:
        results = Recipe.query.filter(Recipe.title.contains(query) | Recipe.ingredients.contains(query)).all()
    else:
        results = []
    return render_template('search_results.html', results=results, query=query)