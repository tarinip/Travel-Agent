from typing import Dict, Any

def trim_messages(state: Dict[str, Any]) -> Dict[str, Any]:
    """Trim state['messages'] to keep only the last 10 messages"""
    # Get current messages
    messages = state.get("messages", [])
    
    # Keep only the last 10 messages
    if len(messages) > 10:
        trimmed_messages = messages[-10:]
        return {
            "messages": trimmed_messages
        }
    else:
        return {
            "messages": messages
        }

# Test function for pytest
# def test_trim_messages():
#     """Test rolling window implementation"""
#     # Create a state with more than 10 messages
#     long_messages = [f"message_{i}" for i in range(15)]
    
#     result = trim_messages({"messages": long_messages})
    
#     assert len(result["messages"]) == 10
#     assert result["messages"] == long_messages[-10:]
    
#     # Test with fewer messages
#     short_messages = [f"message_{i}" for i in range(5)]
#     result = trim_messages({"messages": short_messages})
    
#     assert len(result["messages"]) == 5
#     assert result["messages"] == short_messages