from datetime import datetime, timedelta
from database import get_connection

DAYS_ALLOWED = 14  # Default standard loan period

def issue_book(book_id, member_id):
    """Issues a book copy if available and logs dates."""
    issue_date = datetime.now().date()
    due_date = issue_date + timedelta(days=DAYS_ALLOWED)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Check availability
            cursor.execute("SELECT available_copies FROM books WHERE id = ?", (book_id,))
            result = cursor.fetchone()
            if not result or result[0] <= 0:
                print("Transaction Failed: This book is currently out of stock.")
                return

            # Decrement inventory and log loan record
            cursor.execute("UPDATE books SET available_copies = available_copies - 1 WHERE id = ?", (book_id,))
            cursor.execute(
                "INSERT INTO loans (book_id, member_id, issue_date, due_date) VALUES (?, ?, ?, ?)",
                (book_id, member_id, str(issue_date), str(due_date))
            )
            conn.commit()
            print(f"Book issued successfully! Due date: {due_date}")
            
    except Exception as e:
        print(f"Transaction Error: {e}")

def return_book(loan_id):
    """Marks a loan as returned and updates the book inventory."""
    return_date = str(datetime.now().date())
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Find the linked book ID
            cursor.execute("SELECT book_id, return_date FROM loans WHERE id = ?", (loan_id,))
            record = cursor.fetchone()
            
            if not record:
                print("Record Not Found: Invalid Loan ID.")
                return
            if record[1] is not None:
                print("Warning: This loan has already been settled and returned.")
                return
                
            book_id = record[0]
            
            # Mark returned and restore inventory level
            cursor.execute("UPDATE loans SET return_date = ? WHERE id = ?", (return_date, loan_id))
            cursor.execute("UPDATE books SET available_copies = available_copies + 1 WHERE id = ?", (book_id,))
            conn.commit()
            print("Book returned safely and processed.")
            
    except Exception as e:
        print(f"Processing Error: {e}")