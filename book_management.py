from database import get_connection

def add_book(title, author, isbn, copies):
    """
    Adds a new book record to the system inventory.
    If the book already exists (by ISBN), it increases the available stock copy count.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if book already exists by ISBN
            cursor.execute("SELECT id, available_copies FROM books WHERE isbn = ?", (isbn,))
            existing_book = cursor.fetchone()
            
            if existing_book:
                book_id, current_copies = existing_book
                new_total = current_copies + copies
                cursor.execute(
                    "UPDATE books SET available_copies = ? WHERE id = ?", 
                    (new_total, book_id)
                )
                print(f"Updated inventory: Added {copies} more copies to '{title}'.")
            else:
                cursor.execute(
                    "INSERT INTO books (title, author, isbn, available_copies) VALUES (?, ?, ?, ?)",
                    (title, author, isbn, copies)
                )
                print(f"Book '{title}' added to catalog successfully!")
                
            conn.commit()
    except Exception as e:
        print(f"Error executing book database operation: {e}")

def search_book_by_title(title_keyword):
    """Searches and prints any books matching a given title query."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", (f"%{title_keyword}%",))
        books = cursor.fetchall()
        
        if not books:
            print(f"No books found matching the search: '{title_keyword}'")
            return
            
        print(f"\n--- Search Results for '{title_keyword}' ---")
        _print_book_table(books)

def view_all_books():
    """Displays all current catalog inventory entries."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        
        if not books:
            print("The library catalog is currently empty.")
            return
            
        print("\n--- Complete Library Catalog ---")
        _print_book_table(books)

def _print_book_table(books_list):
    """Helper method to handle scannable terminal layout grids."""
    print(f"{'ID':<6} {'Title':<35} {'Author':<25} {'ISBN':<15} {'Stock Count'}")
    print("-" * 95)
    for b in books_list:
        print(f"{b[0]:<6} {b[1]:<35} {b[2]:<25} {b[3]:<15} {b[4]}")
