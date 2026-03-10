"""
user.py

Looks up employee/user records from the configured relational database
(MariaDB by default) using a case-insensitive name search.
"""

from config.db_mapper import db_factory

def get_user(name):
  """
  Retrieve a user record by a partial name match.

  Performs a case-insensitive LIKE query against the ``users`` table
  and returns the first matching row.  Returns a dict of None values
  when no match is found.

  Args:
    name (str): Full or partial name to search for.

  Returns:
    dict: A dictionary with the following keys:
      - "name"       (str|None): The user's full name.
      - "email"      (str|None): The user's email address.
      - "department" (str|None): The user's role/department.
  """

  conn = db_factory("mariadb")

  cursor = conn.cursor()

  query = """
  SELECT name, email, role
  FROM users
  WHERE LOWER(name) LIKE LOWER(?)
  LIMIT 1
  """

  cursor.execute(query, (f"%{name}%",))

  row = cursor.fetchone()

  cursor.close()
  conn.close()

  if not row:
    return {
      "name": None,
      "email": None,
      "department": None
    }

  return {
    "name": row[0],
    "email": row[1],
    "department": row[2]
  }