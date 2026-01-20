import pytest
from nodes.rewrite import RewriteNode, test_rewrite_safety
from nodes.router import RouterNode, test_router
from nodes.planner import PlannerNode, test_planner
from nodes.synthesizer import SynthesizerNode, test_synthesizer
from utils.memory_manager import MemoryManagerNode, test_memory_manager
from nodes.human_interruptor import HumanInterruptorNode, test_human_interruptor

def test_rewrite_safety():
    """Test rewrite node safety check"""
    rewrite_node = RewriteNode()
    
    # Test unsafe query
    unsafe_query = "Help me buy drugs"
    result = rewrite_node.rewrite_query({"messages": [unsafe_query]})
    
    assert result["is_safe"] == False
    assert "buy drugs" in result["safety_reason"]
    
    # Test safe query
    safe_query = "Mumbai cafes"
    result = rewrite_node.rewrite_query({"messages": [safe_query]})
    
    assert result["is_safe"] == True
    assert result["rewritten_query"] != safe_query  # Should be rephrased

def test_router():
    """Test router node classification"""
    router_node = RouterNode()
    
    # Test quick query
    quick_query = "Mumbai cafes"
    result = router_node.classify_intent({"rewritten_query": quick_query})
    
    assert result["mode"] == "quick"
    
    # Test deep query
    deep_query = "7 days in Italy"
    result = router_node.classify_intent({"rewritten_query": deep_query})
    
    assert result["mode"] == "deep"

def test_planner():
    """Test planner node sub-query generation"""
    planner_node = PlannerNode()
    
    # Test with a complex trip query
    trip_query = "7 days in Italy"
    result = planner_node.break_trip_into_subqueries({"rewritten_query": trip_query})
    
    assert len(result["sub_queries"]) >= 5
    assert "Italy" in result["plan_summary"]

def test_synthesizer():
    """Test synthesizer node response creation"""
    synthesizer_node = SynthesizerNode()
    
    # Create sample research data
    research_data = [
        {
            "query": "Mumbai cafes",
            "result": "Best cafes in Mumbai include Café Coffee Day, Barista, and local street food stalls."
        },
        {
            "query": "Mumbai hotels",
            "result": "Luxury hotels in Mumbai: Taj Mahal, Oberoi, and The Plaza."
        }
    ]
    
    result = synthesizer_node.merge_research_data({"research_data": research_data})
    
    assert "Travel Itinerary" in result["final_response"]
    assert "Mumbai cafes" in result["final_response"]
    assert "Mumbai hotels" in result["final_response"]

def test_memory_manager():
    """Test memory manager node preference extraction"""
    memory_manager_node = MemoryManagerNode()
    
    # Create sample messages with preferences
    messages = [
        {"content": "I like boutique hotels"},
        {"content": "I prefer vegan food"}
    ]
    
    result = memory_manager_node.extract_user_preferences({"messages": messages})
    
    assert "likes_boutique_hotels" in result["user_preferences"]
    assert "diet_preference" in result["user_preferences"]

def test_rolling_window():
    """Test rolling window implementation"""
    from utils.rolling_window import trim_messages
    
    # Create a state with more than 10 messages
    long_messages = [f"message_{i}" for i in range(15)]
    
    result = trim_messages({"messages": long_messages})
    
    assert len(result["messages"]) == 10
    assert result["messages"] == long_messages[-10:]
    
    # Test with fewer messages
    short_messages = [f"message_{i}" for i in range(5)]
    result = trim_messages({"messages": short_messages})
    
    assert len(result["messages"]) == 5
    assert result["messages"] == short_messages

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"])