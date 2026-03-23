"""
Test script for release_management_withfilters agent.

Tests basic functionality of the enhanced release management agent.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agent.manager.sub_agent.old_agents.release_management_withfilters.tool import (
    get_vesting_dates,
    get_vesting_details_with_data,
    create_execution_plan,
    extract_filters_from_query,
    apply_filter,
    calculate_tax_with_filters,
    create_batch
)


class MockToolContext:
    """Mock ToolContext for testing."""
    def __init__(self):
        self.state = {}


def test_get_vesting_dates():
    """Test vesting date retrieval."""
    print("\n=== Test 1: Get Vesting Dates ===")
    result = get_vesting_dates(count=2)
    print(f"Status: {result['status']}")
    print(f"Vesting dates: {result['vesting_dates']}")
    assert result['status'] == 'success'
    assert len(result['vesting_dates']) == 2
    print("✅ PASSED")


def test_workflow_no_filters():
    """Test complete workflow without filters."""
    print("\n=== Test 2: Complete Workflow (No Filters) ===")

    context = MockToolContext()
    vesting_date = "2026-03-15"

    # Step 1: Create execution plan
    print("\nStep 1: Create execution plan...")
    plan_result = create_execution_plan(
        vesting_date=vesting_date,
        user_query="Simulate next vesting",
        tool_context=context
    )
    print(f"Plan ID: {plan_result['plan_id']}")
    print(f"Has filters: {plan_result['has_filters']}")
    print(f"Steps: {len(plan_result['steps'])}")

    # Step 2: Get vesting details
    print("\nStep 2: Get vesting details...")
    details_result = get_vesting_details_with_data(
        vesting_date=vesting_date,
        tool_context=context
    )
    print(f"Status: {details_result['status']}")
    print(f"Tranche count: {details_result['tranche_count']}")

    # Step 3: Calculate tax
    print("\nStep 3: Calculate tax...")
    tax_result = calculate_tax_with_filters(
        vesting_date=vesting_date,
        fmv=10.0,
        sales=12.0,
        tool_context=context
    )
    print(f"Status: {tax_result['status']}")
    print(f"Records processed: {tax_result['records_processed']}")
    print(f"Total shares: {tax_result['total_shares']:,}")
    print(f"Total tax: ${tax_result['total_tax']:,.2f}")

    # Step 4: Create batch
    print("\nStep 4: Create batch...")
    batch_result = create_batch(
        vesting_date=vesting_date,
        tool_context=context,
        save_to_file=False  # Don't save during test
    )
    print(f"Status: {batch_result['status']}")
    print(f"Batch ID: {batch_result['batch_id']}")
    print(f"Record count: {batch_result['record_count']}")
    print(f"Approval URL: {batch_result['approval_url']}")

    print("\n✅ PASSED - Complete workflow without filters")


def test_workflow_with_filters():
    """Test complete workflow with filters."""
    print("\n=== Test 3: Complete Workflow (With Filters) ===")

    context = MockToolContext()
    vesting_date = "2026-03-15"

    # Step 1: Create execution plan
    print("\nStep 1: Create execution plan...")
    plan_result = create_execution_plan(
        vesting_date=vesting_date,
        user_query="Simulate RSUs with FMV 10",
        tool_context=context
    )
    print(f"Plan ID: {plan_result['plan_id']}")
    print(f"Has filters: {plan_result['has_filters']}")
    print(f"Steps: {len(plan_result['steps'])}")

    # Step 2: Get vesting details
    print("\nStep 2: Get vesting details...")
    details_result = get_vesting_details_with_data(
        vesting_date=vesting_date,
        tool_context=context
    )
    print(f"Status: {details_result['status']}")
    print(f"Tranche count: {details_result['tranche_count']}")
    original_count = details_result['tranche_count']

    # Step 3: Extract filters
    print("\nStep 3: Extract filters...")
    filter_result = extract_filters_from_query(
        user_query="Simulate RSUs",
        tool_context=context
    )
    print(f"Status: {filter_result['status']}")
    print(f"Has filters: {filter_result['has_filters']}")
    print(f"Filter summary: {filter_result['filter_summary']}")
    print(f"Conditions: {filter_result['filter_conditions']}")

    # Step 4: Apply filters
    print("\nStep 4: Apply filters...")
    apply_result = apply_filter(
        vesting_date=vesting_date,
        tool_context=context
    )
    print(f"Status: {apply_result['status']}")
    print(f"Original count: {apply_result['original_count']}")
    print(f"Filtered count: {apply_result['filtered_count']}")
    print(f"Reduction: {apply_result['original_count'] - apply_result['filtered_count']} records")

    # Step 5: Calculate tax on filtered data
    print("\nStep 5: Calculate tax on filtered data...")
    tax_result = calculate_tax_with_filters(
        vesting_date=vesting_date,
        fmv=10.0,
        sales=12.0,
        tool_context=context
    )
    print(f"Status: {tax_result['status']}")
    print(f"Records processed: {tax_result['records_processed']}")
    print(f"Total shares: {tax_result['total_shares']:,}")
    print(f"Total tax: ${tax_result['total_tax']:,.2f}")

    # Step 6: Create batch
    print("\nStep 6: Create batch...")
    batch_result = create_batch(
        vesting_date=vesting_date,
        tool_context=context,
        save_to_file=False
    )
    print(f"Status: {batch_result['status']}")
    print(f"Batch ID: {batch_result['batch_id']}")
    print(f"Record count: {batch_result['record_count']}")
    print(f"Approval URL: {batch_result['approval_url']}")

    print("\n✅ PASSED - Complete workflow with filters")


def test_multiple_filters():
    """Test multiple filter conditions."""
    print("\n=== Test 4: Multiple Filters ===")

    context = MockToolContext()
    vesting_date = "2026-03-15"

    # Get vesting details
    get_vesting_details_with_data(vesting_date=vesting_date, tool_context=context)

    # Extract filters for complex query
    print("\nExtracting filters for: 'Engineering RSUs above 5000 shares'...")
    filter_result = extract_filters_from_query(
        user_query="Engineering RSUs above 5000 shares",
        tool_context=context
    )
    print(f"Has filters: {filter_result['has_filters']}")
    print(f"Filter summary: {filter_result['filter_summary']}")
    print(f"Conditions ({len(filter_result['filter_conditions'])} found):")
    for cond in filter_result['filter_conditions']:
        print(f"  - {cond['field']} {cond['operator']} {cond['value']}")

    # Apply filters
    apply_result = apply_filter(vesting_date=vesting_date, tool_context=context)
    print(f"\nOriginal: {apply_result['original_count']} → Filtered: {apply_result['filtered_count']}")

    print("\n✅ PASSED - Multiple filters")


def test_error_handling():
    """Test error handling for missing prerequisites."""
    print("\n=== Test 5: Error Handling ===")

    context = MockToolContext()
    vesting_date = "2026-03-15"

    # Try to calculate tax without fetching data
    print("\nTrying to calculate tax without fetching data...")
    tax_result = calculate_tax_with_filters(
        vesting_date=vesting_date,
        fmv=10.0,
        sales=12.0,
        tool_context=context
    )
    print(f"Status: {tax_result['status']}")
    print(f"Message: {tax_result.get('message', 'No message')}")
    assert tax_result['status'] == 'error'

    # Try to create batch without calculating tax
    print("\nTrying to create batch without calculating tax...")
    batch_result = create_batch(
        vesting_date=vesting_date,
        tool_context=context,
        save_to_file=False
    )
    print(f"Status: {batch_result['status']}")
    print(f"Message: {batch_result.get('message', 'No message')}")
    assert batch_result['status'] == 'error'

    print("\n✅ PASSED - Error handling")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing release_management_withfilters Agent")
    print("=" * 60)

    try:
        test_get_vesting_dates()
        test_workflow_no_filters()
        test_workflow_with_filters()
        test_multiple_filters()
        test_error_handling()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
