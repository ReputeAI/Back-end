import contextvars
import logging
import re
import structlog

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

_SENSITIVE_RE = re.compile("password|secret|token|key", re.IGNORECASE)


def _mask_secrets(logger: structlog.BoundLogger, name: str, event_dict: dict) -> dict:
    for key in list(event_dict.keys()):
        if _SENSITIVE_RE.search(key):
            event_dict[key] = "***"
    return event_dict


def _add_request_id(logger: structlog.BoundLogger, name: str, event_dict: dict) -> dict:
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    structlog.configure(
        processors=[
            _mask_secrets,
            _add_request_id,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
