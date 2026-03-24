from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apc.api')

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(
            f"Exception: {exc}",
            exc_info=True,
            extra={
                'url': context['request'].path,
                'user': context['request'].user.id if context['request'].user.is_authenticated else None,
            }
        )
        # Standardize error response
        response.data = {
            'error': response.data.get('detail', 'An error occurred'),
            'status_code': response.status_code
        }
    else:
        # Unhandled exceptions
        logger.critical(f"Unhandled exception: {exc}", exc_info=True)
        response = Response(
            {'error': 'Internal server error', 'status_code': 500},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
