"""
Pydantic models for release management with filters.

Provides validation and structure for:
- Filter conditions and extraction
- Execution plans
- Tax calculation results
- Batch creation and metadata
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class FilterOperator(str, Enum):
    """Supported filter operators."""
    EQUAL = "="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"


class FilterLogic(str, Enum):
    """Logic for combining multiple filters."""
    AND = "AND"
    OR = "OR"


class FilterCondition(BaseModel):
    """Represents a single filter condition."""
    field: str = Field(..., description="Field name to filter on")
    operator: FilterOperator = Field(..., description="Comparison operator")
    value: Union[str, int, float] = Field(..., description="Value to compare against")

    class Config:
        use_enum_values = True


class FilterConditions(BaseModel):
    """Container for multiple filter conditions."""
    conditions: List[FilterCondition] = Field(default_factory=list)
    logic: FilterLogic = Field(default=FilterLogic.AND, description="How to combine conditions")

    class Config:
        use_enum_values = True


class PlanStepStatus(str, Enum):
    """Status of a plan step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanStep(BaseModel):
    """Single execution step in a plan."""
    step_number: int = Field(..., description="Sequential step number")
    action: str = Field(..., description="Tool or action to execute")
    description: str = Field(..., description="Human-readable description")
    required_inputs: List[str] = Field(default_factory=list, description="Required input parameters")
    expected_output: str = Field(..., description="Expected output or result")
    status: PlanStepStatus = Field(default=PlanStepStatus.PENDING)

    class Config:
        use_enum_values = True


class ExecutionPlan(BaseModel):
    """Complete execution plan for a vesting release workflow."""
    plan_id: str = Field(..., description="Unique plan identifier")
    vesting_date: str = Field(..., description="Vesting date being processed")
    steps: List[PlanStep] = Field(..., description="Ordered list of execution steps")
    has_filters: bool = Field(default=False, description="Whether filters are detected")
    fmv_value: Optional[float] = Field(None, description="FMV parameter if detected")
    sales_value: Optional[float] = Field(None, description="Sales price parameter if detected")


class TaxResult(BaseModel):
    """Tax calculation result for a single employee."""
    employee_id: str
    employee_name: str
    grant_type: str
    vesting_date: str
    shares_released: int
    fmv_at_release: float
    sale_price_at_release: float
    tax_withheld_amount: float
    net_proceeds: float
    gross_value: float


class BatchStatus(str, Enum):
    """Status of a release batch."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


class BatchMetadata(BaseModel):
    """Batch summary information."""
    batch_id: str = Field(..., description="Unique batch identifier")
    vesting_date: str = Field(..., description="Vesting date for this batch")
    creation_timestamp: str = Field(..., description="ISO timestamp of batch creation")
    record_count: int = Field(..., description="Number of records in batch")
    total_shares_released: int = Field(..., description="Total shares across all records")
    total_tax_withheld: float = Field(..., description="Total tax amount withheld")
    filter_applied: bool = Field(default=False, description="Whether filters were applied")
    filter_summary: Optional[str] = Field(None, description="Human-readable filter description")
    status: BatchStatus = Field(default=BatchStatus.DRAFT)

    class Config:
        use_enum_values = True


class BatchRecord(BaseModel):
    """Single record in a release batch."""
    employee_id: str
    employee_name: str
    grant_type: str
    shares_released: int
    fmv_at_release: float
    sale_price_at_release: float
    tax_withheld_amount: float
    net_shares_delivered: int
    net_proceeds: float


class Batch(BaseModel):
    """Complete batch structure with metadata and records."""
    metadata: BatchMetadata
    records: List[BatchRecord]
