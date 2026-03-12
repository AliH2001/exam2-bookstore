"""
Exam 2 - Bookstore API Integration Tests
==========================================
Write your tests below. Each section (Part B and Part D) is marked.
Follow the instructions in each part carefully.

Run your tests with:
    pytest test_bookstore.py -v

Run with coverage:
    pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
"""

import pytest
from bookstore_app import app


# ============================================================
# FIXTURE: Test client with isolated database (provided)
# ============================================================

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client with a temporary database."""
    db_path = str(tmp_path / "test_bookstore.db")
    monkeypatch.setattr("bookstore_db.DB_NAME", db_path)

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============================================================
# HELPER: Create a book (provided for convenience)
# ============================================================

def create_sample_book(client, title="The Great Gatsby", author="F. Scott Fitzgerald", price=12.99):
    """Helper to create a book and return the response JSON."""
    response = client.post("/books", json={
        "title": title,
        "author": author,
        "price": price,
    })
    return response


# ============================================================
# PART B - Integration Tests (20 marks)
# Write at least 14 tests covering ALL of the following:
#
# POST /books:
#   - Create a valid book (check 201 and response body)
#   - Create with missing title (check 400)
#   - Create with empty author (check 400)
#   - Create with invalid price (check 400)

def test_create_valid_book(client):
    response = create_sample_book(client)
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["title"] == "Clean Code"
    assert data["author"] == "Robert Martin"
    assert data["price"] == 10.50

def test_create_book_missing_title(client):
    response = client.post("/books", json={"author": "Robert Martin", "price": 10.50})
    assert response.status_code == 400
    
def test_create_book_empty_author(client):
    response = client.post("/books", json={"title": "Clean Code", "author": "", "price": 10.50})
    assert response.status_code == 400

def test_create_book_invalid_price(client):
    response = client.post("/books", json={"title": "Clean Code", "author": "Robert Martin", "price": -5})
    assert response.status_code == 400


# GET /books:
#   - List books when empty (check 200, empty list)
#   - List books after adding 2+ books (check count)

def test_list_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()["books"] = []
   

def test_list_books_after_adding_two(client):
    create_sample_book(client, title="Book 1", author="Author A", price=5.00)
    create_sample_book(client, title="Book 2", author="Author B", price=20.50)
    response = client.get("/books")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["books"]) == 2

# GET /books/<id>:
#   - Get an existing book (check 200)
#   - Get a non-existing book (check 404)
def test_get_existing_book(client):
    response = create_sample_book(client)
    book_id = response.get_json()["id"]
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == book_id


def test_get_non_existing_book(client):
    response = client.get("/books/999")
    assert response.status_code == 404

# PUT /books/<id>:
#   - Update a book's title (check 200 and new value)
#   - Update with invalid price (check 400)
#   - Update a non-existing book (check 404)

def test_update_book_title(client):
    created = create_sample_book(client)
    book_id = created.get_json()["book"]["id"]
    r = client.put(f"/books/{book_id}", json={
        "title": "How to write clean code",
        "author": "Robert Martin",
        "price": 10.50
    })
    assert r.status_code == 200
    assert r.get_json()["book"]["title"] == "How to write clean code"

def test_update_book_invalid_price(client):
    created = create_sample_book(client)
    book_id = created.get_json()["book"]["id"]
    r = client.put(f"/books/{book_id}", json={
        "title": "Clean Code",
        "author": "Robert Martin",
        "price": 15.99
    })
    assert r.status_code == 400

# DELETE /books/<id>:
#   - Delete an existing book (check 200, then confirm 404)
#   - Delete a non-existing book (check 404)
def test_delete_existing_book(client):
    created = create_sample_book(client)
    book_id = created.get_json()["book"]["id"]
    r = client.delete(f"/books/{book_id}")
    assert r.status_code == 200
    r = client.get(f"/books/{book_id}")
    assert r.status_code == 404

def test_delete_non_existing_book(client):
    r = client.delete("/books/999")
    assert r.status_code == 404

# Full workflow:
#   - Create -> Read -> Update -> Read again -> Delete -> Confirm gone
# ============================================================

# TODO: Write your Part B tests here

def test_full_crud_workflow(client):
    
    # Create
    response = create_sample_book(client, title="code", author="Ali", price=19.99)
    assert response.status_code == 201
    book_id = response.get_json()["book"]["id"]

    # Read
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["book"]["title"] == "code"

    # Update
    response = client.put(f"/books/{book_id}", json={
        "title": "Clean Code",
        "author": "Robert Martin",
        "price": 10.50
    })
    assert response.status_code == 200
    # Read again
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["book"]["title"] == "Clean Code"

    # Delete
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 200

    # Confirm gone
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404

# ============================================================
# PART D - Coverage (5 marks)
# Run: pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
# You must achieve 85%+ coverage across both files.
# If lines are missed, add more tests above to cover them.
# ============================================================


# ============================================================
# BONUS (5 extra marks)
# 1. Add a search endpoint to bookstore_app.py:
#    GET /books/search?q=<query>
#    - Uses search_books() from bookstore_db.py
#    - Returns {"books": [...]} with status 200
#    - Returns {"error": "Search query is required"} with 400 if q is missing
#
# 2. Write 3 integration tests for the search endpoint:
#    - Search by title (partial match)
#    - Search by author (partial match)
#    - Search with no results (empty list)
# ============================================================

# TODO: Write your bonus tests here (optional)
