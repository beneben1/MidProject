from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.sqlite3"
app.config["SECRET_KEY"] = "random string"
CORS(app)

db = SQLAlchemy(app)


# Books model
class Books(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    year_published = db.Column(db.String(100))
    book_type = db.Column(db.Integer)

    def __init__(self, name, author, year_published, book_type):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.book_type = book_type

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "year_published": self.year_published,
            "book_type": self.book_type,
        }


# Function to display books
@app.route("/show-books", methods=["GET"])
def show_books():
    books_list = [book.to_dict() for book in Books.query.all()]
    return jsonify(books_list)


# Function to add a book
@app.route("/add-book", methods=["POST"])
def add_book():
    data = request.get_json()
    name = data.get("name")
    author = data.get("author")
    year_published = data.get("year_published")
    book_type = data.get("book_type")

    new_book = Books(name, author, year_published, book_type)
    db.session.add(new_book)
    db.session.commit()
    return "A new record was created."


# Function to delete a book
@app.route("/delete-book/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Books.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return "Book deleted."
    else:
        return "Book not found."


# Get a single book info
@app.route("/get-book/<book_id>", methods=["GET"])
def get_book(book_id):
    book = Books.query.get(book_id)
    return jsonify(book.to_dict())


# Function to update a book
@app.route("/update-book/<book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json()
    name = data.get("name")
    author = data.get("author")
    year_published = data.get("year_published")
    type_book = data.get("type_book")

    book = Books.query.get(book_id)
    if book:
        book.name = name
        book.author = author
        book.year_published = year_published
        book.type_book = type_book
        db.session.commit()
        return "The record was updated."
    else:
        return "Book not found."


# Customers model
class Customers(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    age = db.Column(db.String(100))

    def __init__(self, name, city, age):
        self.name = name
        self.city = city
        self.age = age

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "age": self.age,
        }


# Function to display customers
@app.route("/show-customers", methods=["GET"])
def show_customers():
    customers_list = [customer.to_dict() for customer in Customers.query.all()]
    return jsonify(customers_list)


# Function to add a customer
@app.route("/add-customer", methods=["POST"])
def add_customer():
    data = request.get_json()
    name = data.get("name")
    city = data.get("city")
    age = data.get("age")

    new_customer = Customers(name, city, age)
    db.session.add(new_customer)
    db.session.commit()
    return "A new record was created."


# Function to delete a customer
@app.route("/delete-customer/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = Customers.query.get(customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return "Customer deleted."
    else:
        return "Customer not found."


# Get a single customer info
@app.route("/get-customer/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = Customers.query.get(customer_id)
    return jsonify(customer.to_dict())


# Function to update a customer
@app.route("/update-customer/<customer_id>", methods=["PUT"])
def update_customer(customer_id):
    data = request.get_json()
    name = data.get("name")
    city = data.get("city")
    age = data.get("age")

    customer = Customers.query.get(customer_id)
    if customer:
        customer.name = name
        customer.city = city
        customer.age = age
        db.session.commit()
        return "The record was updated."
    else:
        return "Customer not found."


# Loans model
class Loans(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    custid = db.Column("custid", db.Integer, db.ForeignKey("customers.ID"))
    bookid = db.Column("bookid", db.Integer, db.ForeignKey("books.ID"))
    loandate = db.Column(db.Date)
    returndate = db.Column(db.Date)

    customer = relationship("Customers", foreign_keys=[custid])
    book = relationship("Books", foreign_keys=[bookid])

    def __init__(self, custid, bookid, loandate, returndate):
        self.custid = custid
        self.bookid = bookid
        self.loandate = loandate
        self.returndate = returndate

    def to_dict(self):  
        return {
            "id": self.id,
            "custid": self.custid,
            "bookid": self.bookid,
            "loandate": self.loandate,
            "returndate": self.returndate
        }


# Function to display loans
@app.route("/show-loans", methods=["GET"])
def show_loans():
    loans_list = [loan.to_dict() for loan in Loans.query.all()]
    return jsonify(loans_list)


# Function to add a loan
@app.route("/add-loan", methods=["POST"])
def add_loan():
    try:
        data = request.get_json()
        cust_id = int(data["cust_id"])
        book_id = int(data["book_id"])
        loan_date = datetime.strptime(data["loan_date"], "%d/%m/%Y").date()
        return_date = datetime.strptime(data["return_date"], "%d/%m/%Y").date()

        # Check if a loan with the same cust_id and book_id already exists
        existing_loan = Loans.query.filter_by(custid=cust_id, bookid=book_id).first()
        if existing_loan:
            return "Loan already exists for the given customer and book."
        customer = Customers.query.get(cust_id)
        book = Books.query.get(book_id)

        if not customer or not book:
            return "Invalid customer or book."

        # Calculate the loan duration based on book_type
        book_type_to_days = {
            1: timedelta(days=10),
            2: timedelta(days=5),
            3: timedelta(days=2),
        }
        loan_duration = book_type_to_days.get(book.book_type)
        if loan_duration:
            return_date = loan_date + loan_duration
            new_loan = Loans(
                custid=cust_id,
                bookid=book_id,
                loandate=loan_date,
                returndate=return_date,
            )
            db.session.add(new_loan)
            db.session.commit()
            return "A new loan was created."
        else:
            return "Invalid book type."
    except Exception as error:
        print("error: %s" % error)
        return "shtok"


# Function to delete a loan
@app.route("/delete-loan/<int:loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    loan = Loans.query.get(loan_id)
    if loan:
        db.session.delete(loan)
        db.session.commit()
        return "Loan deleted."
    else:
        return "Loan not found."


# Function to update a loan
@app.route("/update-loan/<int:loan_id>", methods=["PUT"])
def update_loan(loan_id):
    loan = Loans.query.get(loan_id)
    if loan:
        loan.returndate = datetime.now().date()
        db.session.commit()

        # Return the updated loans list after successful loan return
        loans_list = [loan.to_dict() for loan in Loans.query.all()]
        return jsonify(loans_list)
    else:
        return "Loan not found."



# Function to get expired loans
@app.route("/expired-loans", methods=["GET"])
def expired_loans():
    today = datetime.utcnow().date()
    expired_loans = Loans.query.filter(Loans.returndate < today).all()
    return render_template("expired_loans.html", loans=expired_loans)

# Get a single loan info
@app.route("/get-loan/<loan_id>", methods=["GET"])
def get_loan(loan_id):
    loan = Loans.query.get(loan_id)
    if loan:
        return jsonify(loan.to_dict())
    else:
        return "Loan not found."

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)