import logging
import time
from django.db import connection

logger = logging.getLogger("performance")


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()
        sql_seconds = 0.0
        query_count = 0

        def record_query(execute, sql, params, many, context):
            nonlocal sql_seconds, query_count
            query_start = time.perf_counter()
            try:
                return execute(sql, params, many, context)
            finally:
                sql_seconds += time.perf_counter() - query_start
                query_count += 1

        try:
            with connection.execute_wrapper(record_query):
                response = self.get_response(request)
            return response
        finally:
            elapsed = time.perf_counter() - start
            logger.warning(
                "PERF path=%s method=%s total=%.3fs "
                "sql_total=%.3fs queries=%d",
                request.path,
                request.method,
                elapsed,
                sql_seconds,
                query_count,
            )
