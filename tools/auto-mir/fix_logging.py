import re

with open("auto_mir.py", "r") as f:
    text = f.read()

replacement = """
    # Setup structured JSON logging
    from pythonjsonlogger import jsonlogger

    class BugIdFilter(logging.Filter):
        def filter(self, record):
            record.bug_id = args.bug_id
            return True

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(bug_id)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.addFilter(BugIdFilter())
"""

old_logging = """    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )"""

text = text.replace(old_logging, replacement.strip())

with open("auto_mir.py", "w") as f:
    f.write(text)
