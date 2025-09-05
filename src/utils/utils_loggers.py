import glob
import logging
from pathlib import Path
from utils.helpers import LOGS_INFO


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger that writes to a specific log file.
    ---
    Args:
        name (str): Name of the logger.
        log_file (str): Name or relative path to log file.
        level (int): Logging level (default: logging.INFO)
    Returns:
        logging.Logger: Configured logger instance.
    """
    log_file_path = Path(log_file)
    if not log_file_path.is_absolute():
        log_file_path = LOGS_INFO / (
            log_file_path.with_suffix(".log")
            if log_file_path.suffix != ".log"
            else log_file_path
        )

    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # File handler
        fh = logging.FileHandler(log_file_path)
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(ch)
    return logger


def logs_exist(log_dir: Path = LOGS_INFO) -> bool:
    """
    Checks if any .log file in the log directory is non-empty.
    ---
    Args:
        log_dir (Path): Path to the logs directory.
    Returns:
        bool: True if at least one log file is non-empty.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    return any(Path(f).stat().st_size > 0 for f in glob.glob(str(log_dir / "*.log")))


def clear_logs(log_dir: Path = LOGS_INFO) -> None:
    """
    Clears contents of all .log files in the given directory.
    ---
    Args:
        log_dir (Path): Path to the logs directory.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    for log_file in log_dir.glob("*.log"):
        log_file.write_text("")
