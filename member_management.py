from database import get_connection

def add_member(name, email):
    """
    Registers a new unique member card profile into the database.
    Catches errors if an email duplication constraint conflict happens.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO members (name, email) VALUES (?, ?)", 
                (name, email)
            )
            conn.commit()
            print(f"Member profiles updated: Card created for '{name}'.")
    except Exception as e:
        print(f"Registration Failed: {e} (Verify if email is unique).")

def find_member_by_email(email):
    """Finds and returns raw query results for a specific registered email identifier."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE email = ?", (email,))
        member = cursor.fetchone()
        
        if member:
            print(f"\n--- Member Found ---")
            print(f"ID: {member[0]} | Name: {member[1]} | Email: {member[2]}")
            return member
        else:
            print(f"No accounts tied to database records under: {email}")
            return None

def view_all_members():
    """Outputs a complete master registry log of active accounts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()
        
        if not members:
            print("No accounts are active or registered yet.")
            return
            
        print("\n--- Master Patron Registry ---")
        print(f"{'ID':<6} {'Full Name':<30} {'Registered Contact Email'}")
        print("-" * 70)
        for m in members:
            print(f"{m[0]:<6} {m[1]:<30} {m[2]}")
