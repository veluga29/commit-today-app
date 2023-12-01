from enum import Enum


class ResponseMessage(str, Enum):
    SUCCESS = "Request Success"
    FAIL = "Request Fail"
    CREATE_SUCCESS = "Create Successfully"
