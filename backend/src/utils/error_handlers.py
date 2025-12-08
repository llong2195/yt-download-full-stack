"""Custom exception classes for the application."""


class DownloadException(Exception):
    """Exception raised during download operations.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        technical_details: Technical details for logging
    """

    def __init__(
        self,
        message: str,
        error_code: str = "DOWNLOAD_ERROR",
        technical_details: str | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.technical_details = technical_details or message
        super().__init__(self.message)


class ValidationException(Exception):
    """Exception raised during input validation.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        field: Field name that failed validation
    """

    def __init__(
        self,
        message: str,
        error_code: str = "VALIDATION_ERROR",
        field: str | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.field = field
        super().__init__(self.message)


class NotFoundException(Exception):
    """Exception raised when a resource is not found.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        resource_type: Type of resource not found
        resource_id: ID of resource not found
    """

    def __init__(
        self,
        message: str,
        error_code: str = "NOT_FOUND",
        resource_type: str | None = None,
        resource_id: str | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(self.message)


class DiskSpaceException(DownloadException):
    """Exception raised when disk space is insufficient."""

    def __init__(
        self,
        required_space: int,
        available_space: int,
        message: str | None = None,
    ):
        self.required_space = required_space
        self.available_space = available_space
        msg = (
            message
            or f"Insufficient disk space. Required: {required_space} bytes, Available: {available_space} bytes"
        )
        super().__init__(
            message=msg,
            error_code="INSUFFICIENT_DISK_SPACE",
            technical_details=f"Required: {required_space}, Available: {available_space}",
        )
