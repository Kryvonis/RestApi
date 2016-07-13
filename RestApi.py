from flask import Flask, jsonify, abort, make_response, request, render_template, g
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from math import ceil
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

auth = HTTPBasicAuth()
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'My server key for token'
db = SQLAlchemy(app)


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), index=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = UserModel.query.get(data['id'])
        return user

    def get_user_json(self):
        return {
            'id': self.id,
            'email': self.username,
        }


class PostModel(db.Model):
    __searchable__ = ['title', 'body']
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), unique=True)
    body = db.Column(db.String(150), unique=True)
    creator = db.Column(db.Integer)

    def __repr__(self):
        return '<Post %r>' % self.title

    def get_post_json(self):
        return {
            'title': self.title,
            'body': self.body,
        }


@app.route('/api/user', methods=['POST'])
def create_user():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
        abort(400)
    if UserModel.query.filter_by(email=email).first() is not None:
        abort(400)
    user = UserModel(email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'email': user.email}), 201


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')}), 200


@app.route('/api/post', methods=['POST'])
@auth.login_required
def create_post():
    title = request.json.get('title')
    body = request.json.get('body')
    if title is None:
        abort(400)
    post = PostModel(title=title, body=body, creator=g.user.id)
    db.session.add(post)
    db.session.commit()
    return jsonify({'post': post.title}), 201


@app.route('/api/user', methods=['GET'])
@auth.login_required
def get_user_profile():
    user = UserModel.query.filter_by(id=g.user.id).first()
    if user is None:
        abort(400)
    return jsonify(user.get_user_json()), 200


@app.route('/api/posts', methods=['GET'])
@auth.login_required
def get_posts_by_user():
    posts = PostModel.query.filter_by(creator=g.user.id)
    return jsonify({'posts': [post.get_post_json() for post in posts]})


@app.route('/api/posts/all', methods=['GET'])
@auth.login_required
def get_posts():
    posts = PostModel.query.all()
    total_count = len(posts)
    items_per_page = 5
    page_count = ceil(total_count / items_per_page)
    page = request.args.get('page')
    if page is not None:
        page = int(page)
    else:
        page = 1

    if page < 1:
        page = 1
    if not page_count == 0 and page > page_count:
        abort(400)
    bottom_bound = (page - 1) * items_per_page
    top_bound = page * items_per_page
    next_page = page + 1
    prev_page = page - 1
    if top_bound > total_count:
        next_page = "null"
        top_bound = total_count + 1
    if bottom_bound < 1:
        prev_page = "null"
    items = [item.get_post_json() for item in posts[bottom_bound:top_bound]]
    return jsonify({
        "items": items,
        "meta":
            {"count": items_per_page,
             "next": "?page=%s" % next_page,
             "previous": "?page=%s" % prev_page,
             "total_count": total_count,
             "page_count": page_count
             }
    })


@app.route('/api/posts/search', methods=['GET'])
@auth.login_required
def get_post_search():
    search = request.args.get('q')
    if search is None:
        abort(400)
    try:
        posts = db.engine.execute('SELECT "id","title","body","creator" '
                                  'FROM "post_model" '
                                  'WHERE "title" LIKE "%{0}%" OR "body" LIKE "%{0}%" OR "creator" LIKE "%{0}%"'.format(search)
                                  )
    except:
        abort(400)
    return jsonify({"items": [post.get_post_json() for post in posts]})


@app.route('/api/help', methods=['GET'])
def help():
    return jsonify(
        {
            'create user': '/api/user method POST. Require two fields -email and -password',
            'get auth token': 'api/token method GET. Require -email and -password from user',
            'create post': '/api/post method POST. Require one field -title and one optional -body field ',
            'get users profile': '/api/user method GET. Require -token or -email and -password',
            'get users posts': '/api/posts method GET. Require -token or -email and -password',
            'get all posts': '/api/post/all meghod GET.Require -token or -email and -password. Paging added',
            'post search': '/api/post/search method GET.Require argument -q'
        }
    )


@app.route('/')
def index():
    return render_template('index.html')


@auth.verify_password
def verify_password(email_or_token, password):
    user = UserModel.verify_auth_token(email_or_token)
    if not user:
        user = UserModel.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(405)
def bad_request(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)


if __name__ == '__main__':
    app.run(debug=True)
