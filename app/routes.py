from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from psycopg import Error

from .db import get_db, query

bp = Blueprint("lab", __name__)


def mode():
    return "secure" if request.args.get("mode") == "secure" or request.form.get("mode") == "secure" else "vulnerable"


@bp.get("/")
def index():
    return render_template("index.html")


@bp.route("/auth", methods=["GET", "POST"])
def auth():
    selected = mode(); account = None; error = None; demo_account = None
    if request.method == "POST":
        username = request.form.get("username", ""); password = request.form.get("password", "")
        try:
            if selected == "secure":
                rows = query("SELECT username, role FROM accounts WHERE username = %s AND password = %s", (username, password))
            else:
                # Deliberately unsafe for the tautology demonstration.
                rows = query(f"SELECT username, role FROM accounts WHERE username = '{username}' AND password = '{password}'")
            if rows:
                session["account"] = dict(rows[0]); return redirect(url_for("lab.auth", mode=selected))
            error = "Sign-in failed. Check the supplied credentials."
        except Error:
            error = "The database rejected the request. Try again with valid input."
    try:
        # This is the fictional student account seeded in sql/02_seed.sql.
        demo_rows = query("SELECT username, password FROM accounts WHERE username = %s", ("student",))
        demo_account = dict(demo_rows[0]) if demo_rows else None
    except Error:
        # Keep the login page usable before PostgreSQL setup; values match the seed script.
        demo_account = {"username": "student", "password": "LibraryPass-42"}
    account = session.get("account")
    return render_template("auth.html", mode=selected, account=account, error=error, demo_account=demo_account)


@bp.post("/auth/sign-out")
def sign_out():
    session.pop("account", None); return redirect(url_for("lab.auth"))


@bp.route("/catalog", methods=["GET", "POST"])
def catalog():
    selected = mode(); term = request.values.get("q", ""); products=[]; users=[]; error=None
    try:
        if selected == "secure":
            products = query("SELECT name, price, description FROM products WHERE name ILIKE %s OR description ILIKE %s ORDER BY id", (f"%{term}%", f"%{term}%"))
        else:
            # The selected columns intentionally match users for UNION teaching.
            products = query(f"SELECT name, price, description FROM products WHERE name ILIKE '%{term}%' OR description ILIKE '%{term}%'")
    except Error as exc:
        error = "The catalog query failed: " + str(exc).splitlines()[0]
    return render_template("catalog.html", mode=selected, term=term, products=products, error=error)


@bp.route("/library", methods=["GET", "POST"])
def library():
    selected=mode(); book_id=request.values.get("book_id", ""); book=None; error=None
    try:
        if selected == "secure":
            if not book_id.isdigit(): raise ValueError("Book ID must be a whole number.")
            rows=query("SELECT title, author, publication_year, available FROM books WHERE id = %s", (int(book_id),))
        else:
            rows=query(f"SELECT title, author, publication_year, available FROM books WHERE id = {book_id}")
        book=rows[0] if rows else None
    except (ValueError, Error) as exc:
        error = "Please enter a valid Book ID." if selected == "secure" else "Database error (educational leakage): " + str(exc).splitlines()[0]
    return render_template("library.html", mode=selected, book=book, book_id=book_id, error=error)


@bp.route("/tracking", methods=["GET", "POST"])
def tracking():
    selected = mode()
    number = request.values.get("tracking_number", "")
    found = None
    error = None
    try:
        if selected == "secure":
            rows = query("SELECT 1 FROM shipments WHERE tracking_number = %s", (number,))
        else:
            # Deliberately unsafe: Boolean expressions in the tracking field alter this predicate.
            rows = query(f"SELECT 1 FROM shipments WHERE tracking_number = '{number}'")
        found = bool(rows)
    except Error as exc:
        error = "The tracking lookup could not be completed." if selected == "secure" else \
                "Database error (educational leakage): " + str(exc).splitlines()[0]
    return render_template("tracking.html", mode=selected, number=number, found=found, error=error)


@bp.route("/product", methods=["GET", "POST"])
def product():
    selected=mode(); message=None; error=None
    if request.method == "POST":
        name=request.form.get("reviewer", ""); review=request.form.get("review", "")
        try:
            if selected == "secure":
                if not name.strip() or not review.strip() or len(review) > 1000: raise ValueError
                with get_db().cursor() as cur: cur.execute("INSERT INTO reviews (product_id, reviewer_name, review_text) VALUES (%s, %s, %s)", (1, name.strip(), review.strip()))
            else:
                # Unsafe simple-query execution is intentional: a crafted review can terminate
                # the INSERT and append an UPDATE in this isolated teaching database.
                sql=f"INSERT INTO reviews (product_id, reviewer_name, review_text) VALUES (1, '{name}', '{review}')"
                with get_db().cursor() as cur: cur.execute(sql)
            get_db().commit(); message="Review submitted."
        except (ValueError, Error) as exc:
            get_db().rollback(); error="Please provide a valid review." if selected == "secure" else "Database error: " + str(exc).splitlines()[0]
    if request.args.get("reset") == "1":
        db = get_db()
        try:
            with db.cursor() as cur:
                # Preserve the review from sql/02_seed.sql, remove only test reviews,
                # and restore the seed row if a previous test removed it.
                cur.execute(
                    "UPDATE products SET price = %s WHERE id = %s",
                    (899.00, 1),
                )
                cur.execute(
                    """
                    DELETE FROM reviews
                    WHERE product_id = %s
                      AND NOT (reviewer_name = %s AND review_text = %s)
                    """,
                    (1, "Demo visitor", "A reliable fictional laptop for coursework."),
                )
                cur.execute(
                    """
                    INSERT INTO reviews (product_id, reviewer_name, review_text)
                    SELECT %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM reviews
                        WHERE product_id = %s
                          AND reviewer_name = %s
                          AND review_text = %s
                    )
                    """,
                    (1, "Demo visitor", "A reliable fictional laptop for coursework.",
                     1, "Demo visitor", "A reliable fictional laptop for coursework."),
                )
            db.commit()
        except Error:
            db.rollback()
            raise
        return redirect(url_for("lab.product", mode=selected))
    product_row=query("SELECT id, name, price, description FROM products WHERE id=1")[0]
    reviews=query("SELECT reviewer_name, review_text, created_at FROM reviews WHERE product_id=1 ORDER BY created_at DESC")
    return render_template("product.html", mode=selected, product=product_row, reviews=reviews, message=message, error=error)

