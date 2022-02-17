import warnings


def mark_deprecated(message: str) -> None:
    """Deprecate the given callee."""
    # https://stackoverflow.com/a/30253848/13781503
    warnings.simplefilter("once", DeprecationWarning)
    warnings.warn(
        message,
        category=DeprecationWarning,
        stacklevel=2,
    )
    warnings.simplefilter("default", DeprecationWarning)
