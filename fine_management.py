from datetime import datetime
from database import get_connection

DAILY_FINE_RATE = 1.50  # Charge per day past due date

def check_and_calculate_fines():
    """Compares current date to due dates to auto-generate fines for overdue loans."""
    today = datetime.now().date()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        # Look for active/unreturned loans that are past due
        cursor.execute("SELECT id, due_date FROM loans WHERE return_date IS NULL")
        active_loans = cursor.fetchall()
        
        for loan_id, due_date_str in active_loans:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if today > due_date:
                days_overdue = (today - due_date).days
                fine_amount = days_overdue * DAILY_FINE_RATE
                
                # Check if fine record entry already exists
                cursor.execute("SELECT id FROM fines WHERE loan_id = ?", (loan_id,))
                if cursor.fetchone():
                    cursor.execute("UPDATE fines SET amount = ? WHERE loan_id = ?", (fine_amount, loan_id))
                else:
                    cursor.execute("INSERT INTO fines (loan_id, amount) VALUES (?, ?)", (loan_id, fine_amount))
        conn.commit()

def view_outstanding_fines():
    """Lists all unpaid fines along with member and book details."""
    check_and_calculate_fines()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.id, m.name, b.title, f.amount, f.status 
            FROM fines f
            JOIN loans l ON f.loan_id = l.id
            JOIN members m ON l.member_id = m.id
            JOIN books b ON l.book_id = b.id
            WHERE f.status = 'Unpaid'
        """)
        fines = cursor.fetchall()
        
        if not fines:
            print("Great! There are no outstanding member fines.")
            return
            
        print("\n--- Outstanding Library Fines ---")
        print(f"{'Fine ID':<8} {'Member':<20} {'Book Title':<25} {'Amount ($)':<12} {'Status'}")
        print("-" * 75)
        for f in fines:
            print(f"{f[0]:<8} {f[1]:<20} {f[2]:<25} ${f[3]:<11.2f} {f[4]}")

def settle_fine(fine_id):
    """Marks a specific cash fine as resolved/paid."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE fines SET status = 'Paid' WHERE id = ?", (fine_id,))
        if cursor.rowcount > 0:
            conn.commit()
            print(f"Fine ID {fine_id} successfully paid and settled.")
        else:
            print("Error: Fine record ID not found.")