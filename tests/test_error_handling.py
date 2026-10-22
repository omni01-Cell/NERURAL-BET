# -*- coding: utf-8 -*-
"""
Unit tests for error handling in the agent pipeline.
Tests both critical (fail-fast) and degradable (continue) agent behaviors.
"""
import pytest
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


@pytest.mark.asyncio
async def test_critical_agent_stops_pipeline():
    """
    CRITICAL agents must raise CriticalAgentError and stop the pipeline.
    This prevents corrupted state from propagating downstream.
    """
    agent = MockCriticalAgent(name="TestCritical", role="Test")
    state = AgentState(match_id="test_match_123")
    
    with pytest.raises(CriticalAgentError) as exc_info:
        await agent.execute(state)
    
    # Verify error details are preserved
    assert exc_info.value.code == "CRITICAL_AGENT_FAILURE"
    assert "TestCritical" in exc_info.value.details["agent"]
    assert "Simulated critical failure" in exc_info.value.details["original_error"]


@pytest.mark.asyncio
async def test_degraded_agent_continues_pipeline():
    """
    NON-CRITICAL agents must append error but continue execution.
    This allows enrichment agents to fail gracefully.
    """
    agent = MockDegradedAgent(name="TestDegraded", role="Enrichment")
    state = AgentState(match_id="test_match_456")
    
    # Should NOT raise - just log and continue
    result = await agent.execute(state)
    
    # Verify error was logged but state is returned
    assert len(result.errors) == 1
    assert "TestDegraded Error" in result.errors[0]
    assert "Simulated enrichment failure" in result.errors[0]


@pytest.mark.asyncio
async def test_successful_agent_no_errors():
    """
    Successful agents should complete without errors.
    """
    agent = MockSuccessAgent(name="TestSuccess", role="Test")
    state = AgentState(match_id="test_match_789")
    
    result = await agent.execute(state)
    
    assert len(result.errors) == 0
    assert result.analysis_reports.get("mock_report") == "Success!"


@pytest.mark.asyncio
async def test_error_chaining_preserves_context():
    """
    CriticalAgentError must chain to the original exception
    for proper debugging via __cause__.
    """
    agent = MockCriticalAgent(name="TestChain", role="Test")
    state = AgentState(match_id="test_chain_123")
    
    try:
        await agent.execute(state)
        pytest.fail("Should have raised CriticalAgentError")
    except CriticalAgentError as e:
        # Verify exception chaining
        assert e.__cause__ is not None
        assert isinstance(e.__cause__, ValueError)
        assert "Simulated critical failure" in str(e.__cause__)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
