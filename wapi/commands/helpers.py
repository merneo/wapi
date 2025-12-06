"""
Shared helpers for command implementations (polling, formatting).
"""

import sys
from typing import Any, Callable, Dict, Optional

from ..constants import (
    DEFAULT_MAX_POLL_ATTEMPTS,
    DEFAULT_POLL_INTERVAL,
    EXIT_SUCCESS,
)
from ..exceptions import WAPITimeoutError, WAPIRequestError
from ..utils.formatters import format_output
from ..utils.logger import get_logger


def poll_and_check(
    client,
    command: str,
    params: Dict[str, Any],
    is_complete: Callable[[Dict[str, Any]], bool],
    args: Any,
    success_message: str,
    timeout_error_message: Optional[str] = None,
) -> int:
    """
    Poll a command until completion using the provided completion checker.

    Args:
        client: WedosAPIClient instance
        command: API command string
        params: parameters passed to poll_until_complete
        is_complete: callable that returns True when polling should stop
        args: CLI args with optional quiet/format attributes
        success_message: message printed on success
        timeout_error_message: custom timeout message (optional)

    Returns:
        EXIT_SUCCESS on success

    Raises:
        WAPITimeoutError if timeout detected by caller logic
        WAPIRequestError for non-success final codes
    """
    logger = get_logger("commands.helpers")

    final_result = client.poll_until_complete(
        command,
        params,
        is_complete=is_complete,
        max_attempts=DEFAULT_MAX_POLL_ATTEMPTS,
        interval=DEFAULT_POLL_INTERVAL,
        verbose=not (hasattr(args, "quiet") and args.quiet),
    )

    final_response = final_result.get("response", {})
    final_code = final_response.get("code")

    if final_code in ["1000", 1000]:
        logger.info(f"{success_message} (after polling)")
        print("✅ " + success_message)
        print(format_output(final_response, getattr(args, "format", "table")))
        return EXIT_SUCCESS

    error_msg = final_response.get("result", "Timeout or error")
    logger.warning(f"Polling completed with warning: {error_msg}")
    print(f"⚠️  {error_msg}")
    if "timeout" in str(error_msg).lower():
        print("Polling timeout", file=sys.stderr)
    if "timeout" in str(error_msg).lower() or final_code == "9998":
        raise WAPITimeoutError(timeout_error_message or f"Polling timeout: {error_msg}")
    # Treat non-timeout warnings as non-fatal (match prior behavior)
    return EXIT_SUCCESS
