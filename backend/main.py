from typing import Optional, Any, List, Dict, Tuple, Union
from dotenv import load_dotenv
import os
import psycopg2
from psycopg2 import sql
import uuid
import bcrypt
from model_use import is_safe

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# These functions are the core logic of the SecureAuthAI package
# Each function is a different API call that the user can make
# The functions are called from app.py


def sign_up(
    SECURE_AUTH_AI_PACKAGE_USER: str,
    password: str,
    location: List[str],
    device: str,
    other_details: Optional[Dict[str, str]] = None,
    unique_identifiers: Optional[List[str]] = None,
) -> Tuple[str, bool, str]:
    """Intilialize the user
    If sign up succeeds, returns MFA key
    unique_identifiers is a list of identifiers that must be unique for each user
    other_details is a dictionary of other details that the user wants to store
    all unique_identifiers must be in other_details
    """

    cur = None
    conn = None

    try:
        if unique_identifiers and other_details:
            for identifier in unique_identifiers:
                if get_user_details(identifier, other_details[identifier]):
                    return (
                        "",
                        False,
                        "User already exists with the given unique identifier",
                    )

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        columns = ["password"]
        tokenized_password = _tokenize_password(password)
        values = [tokenized_password]

        if other_details:
            for column_name, value in other_details.items():
                columns.append(column_name)
                values.append(value)

        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() * len(values)),
        )

        cur.execute(insert_query, values)

        conn.commit()

        set_values_var = _set_values(
            SECURE_AUTH_AI_PACKAGE_USER,
            tokenized_password,
            location,
            device,
            False,
            True,
        )

        if isinstance(set_values_var, str):
            return set_values_var, True, "User signed up"
        else:
            return "", False, "SERVER - Error in setting values"

    except Exception as e:
        return "", False, f"Error in signing up: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def log_in(
    SECURE_AUTH_AI_PACKAGE_USER: str,
    password: str,
    location: List[str],
    device: str,
    other_details: Dict[str, str],
) -> Tuple[str, bool, str]:
    """Log in the user. Returns 'MFA' if the user needs to use MFA"""

    cur = None
    conn = None

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        columns = []
        values = []

        for column_name, value in other_details.items():
            columns.append(
                sql.SQL("{column} = %s").format(column=sql.Identifier(column_name))
            )
            values.append(value)

        select_query = sql.SQL("SELECT * FROM {table} WHERE {conditions}").format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            conditions=sql.SQL(" AND ").join(columns),
        )

        cur.execute(select_query, values)
        results = cur.fetchall()
        conn.commit()

        for row in results:
            if _is_correct_password(password, row[1]):
                set_values_var = _set_values(
                    SECURE_AUTH_AI_PACKAGE_USER, row[1], location, device
                )
                if isinstance(set_values_var, str):
                    # Checks using the AI model and anomaly detection if login attempt is safe or not
                    if (
                        is_safe(
                            coords=row[3],
                            devices=row[4],
                            times=row[5],
                            attempts=row[7],
                            curr_attempts=row[6],
                        )
                        and row[6] < 5
                    ):
                        if _reset_attempts(SECURE_AUTH_AI_PACKAGE_USER, row[1]):
                            return "", True, "User logged in"
                        else:
                            return "", False, "SERVER - Error resetting attempts"
                    else:
                        return "MFA", False, "MFA required, use verify_mfa"
                else:
                    return "", False, "SERVER - Error in setting values"
            else:
                set_values_var = _set_values(
                    SECURE_AUTH_AI_PACKAGE_USER, row[1], location, device
                )

                if not isinstance(set_values_var, str):
                    return "", False, "SERVER - Error in setting values"

        return (
            "",
            False,
            "No user found with the given details, password might be wrong",
        )

    except Exception as e:
        return "", False, f"Error in logging in: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_user_details(
    SECURE_AUTH_AI_PACKAGE_USER: str, identifier: str, value: str
) -> Tuple[List[Any], bool, str]:
    """Get the details of the user based on an identifier, returns [] if user does not exist
    Function can also be used to check if the user exists"""

    cur = None
    conn = None

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        select_query = sql.SQL("SELECT * FROM {table} WHERE {identifier} = %s").format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            identifier=sql.Identifier(identifier),
        )

        cur.execute(select_query, (value,))
        results = cur.fetchall()
        conn.commit()

        return results, True, "User details retrieved"

    except Exception as e:
        return [], False, f"Error getting user details: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_all_details(
    SECURE_AUTH_AI_PACKAGE_USER: str,
) -> Tuple[List[Any], bool, str]:
    """Get the details of all users"""

    cur = None
    conn = None

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        select_query = sql.SQL("SELECT * FROM {table}").format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER)
        )

        cur.execute(select_query)
        results = cur.fetchall()
        conn.commit()

        return results, True, "All details retrieved"

    except Exception as e:
        return [], False, f"Error in getting all details: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def update_user_details(
    SECURE_AUTH_AI_PACKAGE_USER: str,
    identifier: str,
    value: str,
    details: Dict[str, Any],
    break_defaults: bool = False,
) -> Tuple[str, bool, str]:
    """Update the details of the user
    If break_defaults is set to True, the user can update the reserved columns
    It is NOT recommended to update the reserved columns as it can lead to other functions not working as intended
    """

    conn = None
    cur = None

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        if "password" in details:
            details["password"] = _tokenize_password(details["password"])
            # .decode("utf-8")

        if not break_defaults:
            if (
                "id" in details
                or "total_logins" in details
                or "prev_locations" in details
                or "prev_devices" in details
                or "prev_logins" in details
                or "attempts" in details
                or "all_attempts" in details
            ):
                return (
                    "",
                    False,
                    "Error in updating details: Reserved column name used. If you wish to update these columns, set break_defaults to True",
                )

        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = %s").format(sql.Identifier(col)) for col in details.keys()
        )

        update_query = sql.SQL(
            """
            UPDATE {table}
            SET {set_clause}
            WHERE {identifier} = %s;
            """
        ).format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            set_clause=set_clause,
            identifier=sql.Identifier(identifier),
        )

        values = list(details.values()) + [value]

        cur.execute(update_query, values)

        conn.commit()

        return "", True, "Details updated"

    except Exception as e:
        return "", False, f"Error updating details: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def add_column(
    SECURE_AUTH_AI_PACKAGE_USER: str, column_name: str
) -> Tuple[str, bool, str]:
    """Add a column to the table
    Column datatype is set to VARCHAR(100)"""

    conn = None
    cur = None

    if column_name in [
        "id",
        "password",
        "total_logins",
        "prev_locations",
        "prev_devices",
        "prev_logins",
        "attempts",
        "all_attempts",
        "mfa_key",
    ]:
        return "", False, "Reserved column name used"

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        alter_query = sql.SQL(
            """
            ALTER TABLE {table}
            ADD COLUMN {column} VARCHAR(100);
            """
        ).format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            column=sql.Identifier(column_name),
        )

        cur.execute(alter_query)

        conn.commit()

        return "", True, "Column added"

    except Exception as e:
        return "", False, f"Error adding column: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def remove_column(
    SECURE_AUTH_AI_PACKAGE_USER: str, column_name: str
) -> Tuple[str, bool, str]:
    """Remove a column from the table"""

    conn = None
    cur = None

    if column_name in [
        "id",
        "password",
        "total_logins",
        "prev_locations",
        "prev_devices",
        "prev_logins",
        "attempts",
        "all_attempts",
        "mfa_key",
    ]:
        return "", False, "Reserved column name used"

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        alter_query = sql.SQL(
            """
            ALTER TABLE {table}
            DROP COLUMN {column};
            """
        ).format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            column=sql.Identifier(column_name),
        )

        cur.execute(alter_query)

        conn.commit()

        return "", True, "Column removed"

    except Exception as e:
        return "", False, f"Error removing column: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def remove_user(
    SECURE_AUTH_AI_PACKAGE_USER: str,
    identifier: str,
    value: str,
) -> Tuple[str, bool, str]:
    """Removes the user"""

    cur = None
    conn = None

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        delete_query = sql.SQL("DELETE FROM {table} WHERE {identifier} = %s").format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            identifier=sql.Identifier(identifier),
        )

        cur.execute(delete_query, (value,))

        conn.commit()

        return "", True, "User removed"

    except Exception as e:
        return "", False, f"Error removing user: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def verify_mfa(
    SECURE_AUTH_AI_PACKAGE_USER: str,
    provided_mfa_key: str,
    identifier: str,
    value: str,
) -> Tuple[str, bool, str]:
    """Verify the MFA key, retruns new MFA key on success"""

    conn = None
    cur = None

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        select_query = sql.SQL(
            "SELECT * FROM {table} WHERE {identifier} = {value}"
        ).format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            identifier=sql.Identifier(identifier),
            value=sql.Literal(value),
        )

        cur.execute(select_query)
        results = cur.fetchall()

        if not results or len(results) > 1:
            return (
                "",
                False,
                "User does not exist or multiple user exists with the same identifier",
            )

        conn.commit()

        if results[0][8] == provided_mfa_key:
            tokenized_password = results[0][1]

            if not _reset_attempts(SECURE_AUTH_AI_PACKAGE_USER, tokenized_password):
                return "", False, "SERVER - Error in resetting attempts"

            new_mfa_key = str(uuid.uuid4())

            update_mfa_query = sql.SQL(
                """
                UPDATE {table}
                SET mfa_key = {new_mfa_key}
                WHERE password = %s;
                """
            ).format(
                table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
                new_mfa_key=sql.Literal(new_mfa_key),
            )

            cur.execute(update_mfa_query, (tokenized_password,))
            conn.commit()

            return new_mfa_key, True, "MFA key verified"
        else:
            return "", False, "MFA key incorrect"

    except Exception as e:
        return "", False, f"Error verifying MFA: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def _reset_attempts(SECURE_AUTH_AI_PACKAGE_USER: str, tokenized_password: str) -> bool:
    """Updates and resets login attempts. Please report to creator in case of any error in this function"""

    conn = None
    cur = None

    try:

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        select_query = sql.SQL("SELECT * FROM {table} WHERE password = %s").format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
        )

        cur.execute(select_query, (tokenized_password,))
        results = cur.fetchall()

        if not results:
            return False

        row = results[0]

        update_total_logins_query = sql.SQL(
            """
            UPDATE {table}
            SET total_logins = total_logins + 1
            WHERE password = %s;
            """
        ).format(table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER))

        update_all_attempts_query = sql.SQL(
            """
            UPDATE {table}
            SET all_attempts = array_append(all_attempts, %s)
            WHERE password = %s;
            """
        ).format(table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER))

        cur.execute(
            update_all_attempts_query,
            (
                row[6],
                row[1],
            ),
        )

        update_attempts_query = sql.SQL(
            """
            UPDATE {table}
            SET attempts = 0
            WHERE password = %s;
            """
        ).format(table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER))

        cur.execute(update_attempts_query, (row[1],))
        cur.execute(update_total_logins_query, (row[1],))

        conn.commit()

        return True
    except Exception as e:
        print(f"SERVER - Error resetting attempts: {e}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def _set_values(
    SECURE_AUTH_AI_PACKAGE_USER: str,
    tokenized_password: str,
    location: List[str],
    device: str,
    wrong_password: bool = False,
    sign_up: bool = False,
) -> Union[bool, str]:
    """Sets the default table values. Please report to creator in case of any error in this function"""

    conn = None
    cur = None
    mfa_key = None

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        update_prev_logins_query = sql.SQL(
            """
            UPDATE {table}
            SET prev_logins = array_append(prev_logins, CURRENT_TIMESTAMP)
            WHERE password = %s;
            """
        ).format(table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER))

        update_prev_locations_query = sql.SQL(
            """
            UPDATE {table}
            SET prev_locations = array_cat(prev_locations, ARRAY[[{longitude}, {latitude}]])
            WHERE password = %s;
            """
        ).format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            longitude=sql.Literal(location[0]),
            latitude=sql.Literal(location[1]),
        )

        update_prev_devices_query = sql.SQL(
            """
            UPDATE {table}
            SET prev_devices = array_append(prev_devices, {device})
            WHERE password = %s;
            """
        ).format(
            table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
            device=sql.Literal(device),
        )

        if wrong_password:
            update_attempts_query = sql.SQL(
                """
                UPDATE {table}
                SET attempts = attempts + 1
                WHERE password = %s;
                """
            ).format(table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER))

            cur.execute(update_attempts_query, (tokenized_password,))

            mfa_key = "True"
        elif sign_up:
            update_total_logins_query = sql.SQL(
                """
                UPDATE {table}
                SET total_logins = 1
                WHERE password = %s;
                """
            ).format(table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER))

            mfa_key = str(uuid.uuid4())

            update_mfa_query = sql.SQL(
                """
                UPDATE {table}
                SET mfa_key = {mfa_key}
                WHERE password = %s;
                """
            ).format(
                table=sql.Identifier(SECURE_AUTH_AI_PACKAGE_USER),
                mfa_key=sql.Literal(mfa_key),
            )

            cur.execute(update_total_logins_query, (tokenized_password,))
            cur.execute(update_mfa_query, (tokenized_password,))
        else:
            mfa_key = "True"

        cur.execute(update_prev_logins_query, (tokenized_password,))
        cur.execute(update_prev_locations_query, (tokenized_password,))
        cur.execute(update_prev_devices_query, (tokenized_password,))

        conn.commit()

        if mfa_key:
            return mfa_key
        else:
            return False

    except Exception as e:
        print("SERVER - Error in setting values: ", e)
        return False

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def _tokenize_password(password: str) -> str:
    """Tokenize the password"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def _is_correct_password(provided_password: str, tokenized_password: str) -> bool:
    """Checks if the password is correct"""
    return bcrypt.checkpw(
        provided_password.encode("utf-8"), tokenized_password.encode("utf-8")
    )


def initialize_package(other_details: List[str] = None) -> Tuple[str, bool, str]:
    """This function needs to be called FIRST to generate a unique token that refers to the table.
    After this the user can begin using the rest of the package functions

    If you make a mistake in creating the table, call this function again to get a new token
    other_details should NOT contain the following: id, password, total_logins, prev_locations, prev_devices, prev_logins, attempts, all_attempts
    All other data will be stored as a string
    """
    cur = None
    conn = None

    try:
        uid = str(uuid.uuid4())

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        columns = [
            sql.SQL("id SERIAL PRIMARY KEY"),
            sql.SQL("password VARCHAR(100) NOT NULL"),
            sql.SQL("total_logins INT DEFAULT 0"),
            sql.SQL("prev_locations VARCHAR(100)[][] DEFAULT ARRAY[]::VARCHAR(100)[]"),
            sql.SQL("prev_devices VARCHAR(200)[] DEFAULT ARRAY[]::VARCHAR(200)[]"),
            sql.SQL("prev_logins TIMESTAMP[] DEFAULT ARRAY[]::TIMESTAMP[]"),
            sql.SQL("attempts INT DEFAULT 0"),
            sql.SQL("all_attempts INT[] DEFAULT ARRAY[]::INT[]"),
            sql.SQL("mfa_key VARCHAR(100)"),
        ]

        if other_details:
            if (
                ("id" in other_details)
                or ("password" in other_details)
                or ("total_logins" in other_details)
                or ("prev_locations" in other_details)
                or ("prev_devices" in other_details)
                or ("prev_logins" in other_details)
                or ("attempts" in other_details)
                or ("all_attempts" in other_details)
                or ("mfa_key" in other_details)
            ):
                return "", False, "Reserved column name used"

            for column_name in other_details:
                columns.append(
                    sql.SQL("{} VARCHAR(100)").format(sql.Identifier(column_name))
                )

        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ( {} );").format(
            sql.Identifier(uid), sql.SQL(", ").join(columns)
        )

        cur.execute(create_table_query)

        conn.commit()

        return uid, True, "Table created"

    except Exception as e:
        return "", False, f"Error in creating table: {e}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
