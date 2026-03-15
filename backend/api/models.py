"""
Pydantic models for request and response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AnalyzeRequest(BaseModel):
    """Request model for code analysis endpoint."""
    language: str = Field(..., description="Programming language: 'C' or 'Java'")
    code: str = Field(..., description="Source code to analyze")
    input_data: Optional[str] = Field(None, description="Optional input data for program execution")
    expected_output: Optional[str] = Field(None, description="Optional expected output for comparison")


class LLMExplanation(BaseModel):
    """LLM-generated explanation structure."""
    summary: str = Field(..., description="Simple explanation of the error")
    cause: str = Field(..., description="Root cause analysis")
    fix: str = Field(..., description="Suggested fix")
    corrected_code: Optional[str] = Field(None, description="Corrected code (if applicable)")


class AnalyzeResponse(BaseModel):
    """Response model for code analysis endpoint."""
    compile_errors: Dict[str, Any] = Field(default_factory=dict, description="Compilation errors")
    runtime_errors: Dict[str, Any] = Field(default_factory=dict, description="Runtime errors")
    output_analysis: Dict[str, Any] = Field(default_factory=dict, description="Output comparison analysis")
    llm_explanation: Dict[str, Any] = Field(default_factory=dict, description="LLM-generated explanation")
    execution_success: Optional[bool] = Field(None, description="Whether code executed successfully")
    program_output: Optional[str] = Field(None, description="Program output if execution was successful")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

