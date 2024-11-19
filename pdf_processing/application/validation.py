import os
from typing import Optional
from dataclasses import dataclass
from ..domain.entities import ProcessingStatus

@dataclass
class ValidationError:
    field: str
    message: str

class PDFValidationError(Exception):
    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        super().__init__(self._format_errors())
    
    def _format_errors(self) -> str:
        return "; ".join(f"{error.field}: {error.message}" for error in self.errors)

def validate_pdf_processing_request(pdf_path: str, base_output_dir: str) -> Optional[list[ValidationError]]:
    errors = []
    
    # Validate PDF path
    if not pdf_path:
        errors.append(ValidationError("pdf_path", "PDF path is required"))
    elif not os.path.exists(pdf_path):
        errors.append(ValidationError("pdf_path", "PDF file does not exist"))
    elif not pdf_path.lower().endswith('.pdf'):
        errors.append(ValidationError("pdf_path", "File must be a PDF"))
    
    # Validate output directory
    if not base_output_dir:
        errors.append(ValidationError("base_output_dir", "Output directory is required"))
    elif os.path.exists(base_output_dir) and not os.path.isdir(base_output_dir):
        errors.append(ValidationError("base_output_dir", "Output path exists but is not a directory"))
    
    return errors if errors else None

def validate_processing_status(status: dict) -> Optional[list[ValidationError]]:
    errors = []
    
    required_fields = {
        "status": str,
        "current_page": int,
        "total_pages": int,
        "processed_sections": int,
        "processed_images": int
    }
    
    for field, field_type in required_fields.items():
        if field not in status:
            errors.append(ValidationError(field, f"Missing required field: {field}"))
        elif not isinstance(status[field], field_type):
            errors.append(ValidationError(field, f"Invalid type for {field}, expected {field_type.__name__}"))
    
    if "status" in status:
        try:
            ProcessingStatus(status["status"])
        except ValueError:
            errors.append(ValidationError("status", f"Invalid status value: {status['status']}"))
    
    return errors if errors else None
