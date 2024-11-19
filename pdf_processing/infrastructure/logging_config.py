import logging
import json
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('pdf_processor.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.setLevel(logging.INFO)
    
    def _format_log(self, message: str, extra: Dict[str, Any] = None) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }
        if extra:
            log_data.update(extra)
        return json.dumps(log_data)
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        self.logger.info(self._format_log(message, extra))
    
    def error(self, message: str, error: Exception = None, extra: Dict[str, Any] = None):
        if error:
            if not extra:
                extra = {}
            extra["error_type"] = type(error).__name__
            extra["error_message"] = str(error)
        self.logger.error(self._format_log(message, extra))
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.logger.warning(self._format_log(message, extra))
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.logger.debug(self._format_log(message, extra))
