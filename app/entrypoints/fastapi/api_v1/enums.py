from enum import Enum


class ResponseMessage(str, Enum):
    SUCCESS = "Request Success"
    FAIL = "Request Fail"
    CREATE_SUCCESS = "Create Successfully"
    UPDATE_SUCCESS = "Update Successfully"
    LOGIN_SUCCESS = "Login Successfully"
    LOGOUT_SUCCESS = "Logout Successfully"
