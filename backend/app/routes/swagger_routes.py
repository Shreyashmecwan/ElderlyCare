from flask import Blueprint, jsonify, render_template_string

swagger_bp = Blueprint("swagger", __name__, url_prefix="/api")

OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "ElderCare Healthcare Management REST API",
        "version": "1.0.0",
        "description": "Comprehensive RESTful API for ElderCare: smart medication management, adherence tracking, care circle authorization, appointments, and email alerts."
    },
    "servers": [
        {"url": "http://localhost:5000", "description": "Local Development Server"}
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    },
    "security": [{"BearerAuth": []}],
    "paths": {
        "/api/auth/register": {
            "post": {
                "summary": "Register new user",
                "description": "Registers an Elderly, Family, or Caretaker user.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string", "example": "elizabeth@example.com"},
                                    "password": {"type": "string", "example": "Secure123!"},
                                    "full_name": {"type": "string", "example": "Elizabeth Miller"},
                                    "role": {"type": "string", "enum": ["ELDERLY", "FAMILY", "CARETAKER"]},
                                    "phone_number": {"type": "string", "example": "+1-555-0192"},
                                    "timezone": {"type": "string", "example": "America/New_York"}
                                },
                                "required": ["email", "password", "full_name", "role"]
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "User created with JWT tokens"}}
            }
        },
        "/api/auth/login": {
            "post": {
                "summary": "Authenticate user",
                "responses": {"200": {"description": "Returns access and refresh tokens"}}
            }
        },
        "/api/auth/me": {
            "get": {
                "summary": "Get authenticated user profile and memberships",
                "responses": {"200": {"description": "Current user data"}}
            }
        },
        "/api/profiles": {
            "get": {
                "summary": "List accessible healthcare profiles",
                "responses": {"200": {"description": "Array of profiles"}}
            },
            "post": {
                "summary": "Create an elderly healthcare profile",
                "responses": {"201": {"description": "Profile created"}}
            }
        },
        "/api/profiles/join": {
            "post": {
                "summary": "Join a profile using a unique invitation passcode",
                "description": "Redeems e.g. CARE-XXXX or FAM-XXXX passcode to authorize family or caretaker.",
                "responses": {"200": {"description": "Connected to elderly profile"}}
            }
        },
        "/api/medications": {
            "get": {
                "summary": "List medications for a profile",
                "parameters": [
                    {"name": "profile_id", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["active", "inactive", "all"]}}
                ],
                "responses": {"200": {"description": "List of medications"}}
            },
            "post": {
                "summary": "Add a new medication with scheduled administration times",
                "responses": {"201": {"description": "Medication created"}}
            }
        },
        "/api/adherence/daily": {
            "get": {
                "summary": "Get scheduled doses for today or a specific date",
                "parameters": [
                    {"name": "profile_id", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "date", "in": "query", "schema": {"type": "string", "example": "2026-11-15"}}
                ],
                "responses": {"200": {"description": "Array of dose records with status"}}
            }
        },
        "/api/adherence/{log_id}/status": {
            "post": {
                "summary": "Mark scheduled dose as TAKEN, SKIPPED, or MISSED",
                "parameters": [
                    {"name": "log_id", "in": "path", "required": True, "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Dose status updated and logged in audit trail"}}
            }
        },
        "/api/adherence/stats": {
            "get": {
                "summary": "Calculate adherence percentage and daily breakdown",
                "parameters": [
                    {"name": "profile_id", "in": "query", "required": True, "schema": {"type": "string"}},
                    {"name": "days", "in": "query", "schema": {"type": "integer", "default": 7}}
                ],
                "responses": {"200": {"description": "Adherence statistics"}}
            }
        },
        "/api/appointments": {
            "get": {
                "summary": "List doctor appointments for a profile",
                "responses": {"200": {"description": "List of appointments"}}
            },
            "post": {
                "summary": "Create an appointment",
                "responses": {"201": {"description": "Appointment created"}}
            }
        },
        "/api/dashboard/elderly": {
            "get": {
                "summary": "Get elderly user dashboard data",
                "responses": {"200": {"description": "Elderly dashboard metrics"}}
            }
        },
        "/api/dashboard/family": {
            "get": {
                "summary": "Get family dashboard data",
                "responses": {"200": {"description": "Family dashboard metrics"}}
            }
        },
        "/api/dashboard/caretaker": {
            "get": {
                "summary": "Get caretaker dashboard data",
                "responses": {"200": {"description": "Caretaker dashboard metrics"}}
            }
        }
    }
}

SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>ElderCare API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
    <style>
        body { margin: 0; background: #fafafa; }
        .topbar { display: none; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
    <script>
        window.onload = () => {
            window.ui = SwaggerUIBundle({
                url: '/api/openapi.json',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                deepLinking: true
            });
        };
    </script>
</body>
</html>
"""

@swagger_bp.route("/openapi.json", methods=["GET"])
def get_openapi_json():
    return jsonify(OPENAPI_SPEC)

@swagger_bp.route("/docs", methods=["GET"])
def get_swagger_ui():
    return render_template_string(SWAGGER_UI_HTML)
