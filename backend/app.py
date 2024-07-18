from flask import Flask, request, jsonify
from flask_cors import CORS

from main import *

app = Flask(__name__)
CORS(app)

# This file handles the API calls from the frontend to the backend and calls the respective functions from main.py
# The functions in main.py are the core functions that handle the logic of the SecureAuthAI package
# Each function checks for the appropriate parameters and returns the appropriate values in case of an error


@app.route("/initialize-package", methods=["POST"])
def call_initialize_package():
    try:
        data = request.json

        other_details = data.get("other_details", None)

        value, success, message = initialize_package(other_details)

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/sign-up", methods=["POST"])
def call_sign_up():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        password = data["password"]
        location = data["location"]
        device = data["device"]

        other_details = data.get("other_details", None)
        unique_identifiers = data.get("unique_identifiers", None)

        value, success, message = sign_up(
            SECURE_AUTH_AI_TABLE_KEY,
            password,
            location,
            device,
            other_details,
            unique_identifiers,
        )

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/log-in", methods=["POST"])
def call_log_in():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        password = data["password"]
        location = data["location"]
        device = data["device"]
        other_details = data["other_details"]

        value, success, message = log_in(
            SECURE_AUTH_AI_TABLE_KEY, password, location, device, other_details
        )

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/get-user-details", methods=["POST"])
def call_get_user_details():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        identifier = data["identifier"]
        value = data["value"]

        value, success, message = get_user_details(
            SECURE_AUTH_AI_TABLE_KEY, identifier, value
        )

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": [],
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": [], "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/get-all-details", methods=["POST"])
def call_get_all_details():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]

        value, success, message = get_all_details(SECURE_AUTH_AI_TABLE_KEY)

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": [],
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": [], "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/update-user-details", methods=["POST"])
def call_update_user_details():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        identifier = data["identifier"]
        value = data["value"]
        details = data["details"]

        break_defaults = data.get("break_defaults", False)

        value, success, message = update_user_details(
            SECURE_AUTH_AI_TABLE_KEY, identifier, value, details, break_defaults
        )

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/add-column", methods=["POST"])
def call_add_column():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        column_name = data["column_name"]

        value, success, message = add_column(SECURE_AUTH_AI_TABLE_KEY, column_name)

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/remove-column", methods=["POST"])
def call_remove_column():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        column_name = data["column_name"]

        value, success, message = remove_column(
            SECURE_AUTH_AI_TABLE_KEY, column_name
        )

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/remove-user", methods=["POST"])
def call_remove_user():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        identifier = data["identifier"]
        value = data["value"]

        value, success, message = remove_user(
            SECURE_AUTH_AI_TABLE_KEY, identifier, value
        )

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/verify-mfa", methods=["POST"])
def call_verify_mfa():
    try:
        data = request.json

        SECURE_AUTH_AI_TABLE_KEY = data["SECURE_AUTH_AI_TABLE_KEY"]
        provided_mfa_key = data["provided_mfa_key"]
        identifier = data["identifier"]
        value = data["value"]

        value, success, message = verify_mfa(
            SECURE_AUTH_AI_TABLE_KEY, provided_mfa_key, identifier, value
        )

        return jsonify({"value": value, "success": success, "message": message})

    except KeyError as e:
        return (
            jsonify(
                {
                    "value": "",
                    "success": False,
                    "message": f"Missing required parameter: {e}",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify({"value": "", "success": False, "message": f"BACKEND ERROR: {e}"}),
            500,
        )


@app.route("/")
def call_default():
    return "Welcome to the SecureAuthAI API!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
