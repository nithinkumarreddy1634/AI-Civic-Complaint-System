class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=409, detail=detail)


class AIProcessingException(AppException):
    def __init__(self, detail: str = "AI Processing Error"):
        super().__init__(status_code=500, detail=detail)


class FileValidationException(AppException):
    def __init__(self, detail: str = "File Validation Error"):
        super().__init__(status_code=422, detail=detail)
