class AppError(Exception):
    """Exception métier de base. Les routers la traduisent en HTTPException."""
    status_code: int = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class ValidationError(AppError):
    status_code = 422
