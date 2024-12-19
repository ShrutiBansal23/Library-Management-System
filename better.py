from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

    def __init__(self, name):
        self.name = name

    def serialize(self):
        
        return {
            'id': self.id,
            'name': self.name
        }    

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    published_date = db.Column(db.String(50))

    def __init__(self, title, genre, author_id, published_date):
        self.title = title
        self.genre = genre
        self.author_id = author_id
        self.published_date = published_date

    def serialize(self):
        
        return {
            'title': self.title,
            'genre': self.genre,
            'author_id':self.author_id,
            'published_date':self.published_date
        }      

@app.before_request
def create_tables():
    db.create_all()

@app.route('/authors', methods=['POST'])
def add_author():
    name = request.json['name']
    new_author = Author(name)

    try:
        db.session.add(new_author)
        db.session.commit()
        return jsonify(new_author.serialize()), 201
    except Exception as e:
        return jsonify({"message": "Error in creating author.","error": str(e)}), 400

@app.route('/authors', methods=['GET'])
def get_authors():
  authors = Author.query.all()
    
  authors_list = [author.serialize() for author in authors]
  return jsonify(authors_list)

@app.route('/books', methods=['POST'])
def add_book():
    title = request.json['title']
    genre = request.json.get('genre', '')
    author_id = request.json['author_id']
    published_date=request.json['published_date']
    
    new_book = Book(title, genre, author_id,published_date)
    
    try:
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"message":"book is created"}),201
    except Exception as e:
        return jsonify({"message": "Error in creating book.","error":str(e)}), 400

@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    a=[Book.serialize() for Book in books]
    return jsonify(a)

@app.route('/books/author/<author_id>', methods=['GET'])
def get_books_by_author(author_id):
    books = Book.query.filter_by(author_id=author_id).all()
    b=[Book.serialize() for Book in books]
    return jsonify(b)

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    
    if not book:
        return jsonify({"message": "Book not found."}), 404
    
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})

if __name__ == '__main__':
    app.run(debug=True)
