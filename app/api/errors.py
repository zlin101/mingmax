from fastapi import HTTPException, status


def llm_client_failed_exception(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": {
                "code": "LLM_CLIENT_FAILED",
                "message": str(error),
                "details": [],
            }
        },
    )
