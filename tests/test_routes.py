import pytest
from recipe_app import app, db
from recipe_app.models import User, Recipe, Comment, Rating

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def init_database():
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture
def new_user():
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    return user

@pytest.fixture
def new_recipe(new_user):
    return Recipe(title='Test Recipe', description='Test description', ingredients='Test ingredients', instructions='Test instructions', author=new_user)

@pytest.fixture
def new_comment(new_user, new_recipe):
    return Comment(comment='Test comment', commenter=new_user, recipe=new_recipe)

@pytest.fixture
def new_rating(new_user, new_recipe):
    return Rating(rating=5, rater=new_user, recipe=new_recipe)

def test_index(client, init_database, new_recipe):
    with app.app_context():
        db.session.add(new_recipe)
        db.session.commit()
    response = client.get('/')
    assert response.status_code == 200
    assert b'Test Recipe' in response.data

def test_register(client, init_database):
    response = client.post('/register', data=dict(username='testuser2', email='test2@example.com', password='password', confirm_password='password'), follow_redirects=True)
    assert response.status_code == 200
    # assert b'Your account has been created!' in response.data

def test_login(client, init_database, new_user):
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()
    response = client.post('/login', data=dict(email='test@example.com', password='password'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Home' in response.data

def test_logout(client, init_database, new_user):
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()
    with client:
        client.post('/login', data=dict(email='test@example.com', password='password'), follow_redirects=True)
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

def test_new_recipe(client, init_database, new_user):
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = new_user.id
    response = client.post('/recipe/new', data=dict(title='New Test Recipe', description='New Test Description', ingredients='New Test Ingredients', instructions='New Test Instructions'), follow_redirects=True)
    assert response.status_code == 200
    assert b'New Test Recipe' in response.data

def test_recipe_detail(client, init_database, new_user, new_recipe, new_comment, new_rating):
    with app.app_context():
        db.session.add(new_user)
        db.session.add(new_recipe)
        db.session.add(new_comment)
        db.session.add(new_rating)
        db.session.commit()
    with client.session_transaction() as sess:
        sess['user_id'] = new_user.id
    response = client.get(f'/recipe/{new_recipe.id}')
    assert response.status_code == 200
    assert b'Test Recipe' in response.data

def test_search(client, init_database, new_recipe):
    with app.app_context():
        db.session.add(new_recipe)
        db.session.commit()
    response = client.get('/search?q=Test')
    assert response.status_code == 200
    assert b'Test Recipe' in response.data