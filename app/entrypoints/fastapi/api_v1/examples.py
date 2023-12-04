from app.entrypoints.fastapi.api_v1 import schemas as global_schemas


def get_error_responses(status_codes: list[int]) -> dict:
    status_codes.append(422)
    return {status_code: dict(model=global_schemas.ErrorResponse) for status_code in status_codes}
