# -*- coding: utf-8 -*-
"""
Standalone test for error handling - no pytest dependency.
Run with: python tests/test_error_handling_standalone.py
"""
import asyncio
import sys
from pathlib import Path

# Add root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from src.agents.base import BaseAgent, AgentState
from src.core.exceptions import CriticalAgentError


class MockCriticalAgent(BaseAgent):
    """Test agent that simulates a critical failure."""
    is_critical = True
    
    async def process(self, state: AgentState) -> AgentState:
        raise ValueError("Simulated critical failure in data fetch")


class MockDegradedAgent(BaseAgent):
    """Test agent that simulates a non-critical failure."""
    is_critical = False
    
    async def process(self, state: AgentState) -> AgentState:
        raise ValueError("Simulated enrichment failure")


class MockSuccessAgent(BaseAgent):
    """Test agent that succeeds."""
    is_critical = True
    
    async def process(self, state: AgentState) -> AgentState:
        state.analysis_reports["mock_report"] = "Success!"
        return state


async def test_critical_agent_stops_pipeline():
    """CRITICAL agents must raise CriticalAgentError and stop the pipeline."""
    print("\n[TEST 1] Critical agent stops pipeline...")
    agent = MockCriticalAgent(name="TestCritical", role="Test")
    state = AgentState(match_id="test_match_123")
    
    try:
        await agent.execute(state)
        print("  [FAIL] Should have raised CriticalAgentError")
        return False
    except CriticalAgentError as e:
        if e.code == "CRITICAL_AGENT_FAILURE" and "TestCritical" in e.details.get("agent", ""):
            print("  [PASS] CriticalAgentError raised with correct details")
            return True
        else:
            print(f"  [FAIL] Wrong error details: {e}")
            return False
    except Exception as e:
        print(f"  [FAIL] Wrong exception type: {type(e).__name__}")
        return False


async def test_degraded_agent_continues_pipeline():
    """NON-CRITICAL agents must append error but continue execution."""
    print("\n[TEST 2] Degraded agent continues pipeline...")
    agent = MockDegradedAgent(name="TestDegraded", role="Enrichment")
    state = AgentState(match_id="test_match_456")
    
    try:
        result = await agent.execute(state)
        if len(result.errors) == 1 and "TestDegraded Error" in result.errors[0]:
            print("  [PASS] Error logged but execution continued")
            return True
        else:
            print(f"  [FAIL] Wrong errors: {result.errors}")
            return False
    except Exception as e:
        print(f"  [FAIL] Should NOT have raised: {e}")
        return False


async def test_successful_agent_no_errors():
    """Successful agents should complete without errors."""
    print("\n[TEST 3] Successful agent no errors...")
    agent = MockSuccessAgent(name="TestSuccess", role="Test")
    state = AgentState(match_id="test_match_789")
    
    try:
        result = await agent.execute(state)
        if len(result.errors) == 0 and result.analysis_reports.get("mock_report") == "Success!":
            print("  [PASS] No errors, report added")
            return True
        else:
            print(f"  [FAIL] Unexpected result: errors={result.errors}")
            return False
    except Exception as e:
        print(f"  [FAIL] Unexpected exception: {e}")
        return False


async def test_error_chaining():
    """CriticalAgentError must chain to the original exception."""
    print("\n[TEST 4] Error chaining preserves context...")
    agent = MockCriticalAgent(name="TestChain", role="Test")
    state = AgentState(match_id="test_chain_123")
    
    try:
        await agent.execute(state)
        print("  [FAIL] Should have raised CriticalAgentError")
        return False
    except CriticalAgentError as e:
        if e.__cause__ is not None and isinstance(e.__cause__, ValueError):
            print("  [PASS] Exception chaining works correctly")
            return True
        else:
            print(f"  [FAIL] No cause chain: {e.__cause__}")
            return False


async def run_all_tests():
    print("=" * 50)
    print("ERROR HANDLING TESTS")
    print("=" * 50)
    
    results = [
        await test_critical_agent_stops_pipeline(),
        await test_degraded_agent_continues_pipeline(),
        await test_successful_agent_no_errors(),
        await test_error_chaining(),
    ]
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    return all(results)


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
