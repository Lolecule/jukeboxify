def error(message):
    return {"response_code": "error", "message": message}

def success(message):
    return {"response_code": "success", "message": message}

INVALID_COMMAND = error("Invalid command, try again")

LOGIN_SUCCESS = success("Successfully logged in!")

LOGIN_FAILED = error("Login failed!")
