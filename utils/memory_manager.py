from typing import Dict, Any

def extract_user_preferences(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract user preferences from latest interaction"""
    # Get the messages
    messages = state.get("messages", [])
    
    # Extract preferences from recent messages
    preferences = extract_preferences_from_messages(messages)
    
    return {
        "user_preferences": preferences,
        "memory_update": "Preferences extracted and ready for DB save"
    }

def extract_preferences_from_messages(messages: list) -> dict:
    """Extract user preferences from conversation history"""
    # Simple preference extraction logic
    preferences = {}
    
    # Look for common preference patterns in messages
    for message in messages:
        if isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = message
            
        # Extract preferences based on keywords
        if "boutique hotels" in content.lower():
            preferences["likes_boutique_hotels"] = True
        elif "luxury" in content.lower():
            preferences["budget_level"] = "luxury"
        elif "vegan" in content.lower():
            preferences["diet_preference"] = "vegan"
        elif "budget" in content.lower():
            preferences["budget_level"] = "budget"
            
    return preferences

def save_to_database(state: Dict[str, Any]) -> Dict[str, Any]:
    """Save user preferences to database"""
    # Get user preferences
    user_preferences = state.get("user_preferences", {})
    
    # Simulate DB save operation
    db_save_result = simulate_db_save(user_preferences)
    
    return {
        "db_save_status": db_save_result,
        "memory_update": "Preferences saved to database"
    }

def simulate_db_save(preferences: dict) -> str:
    """Simulate database save operation"""
    # In a real implementation, this would connect to actual DB
    # For now, we'll just return a success status
    return "success"

# Test function for pytest
def test_memory_manager():
    """Test memory manager node preference extraction"""
    # Create sample messages with preferences
    messages = [
        {"content": "I like boutique hotels"},
        {"content": "I prefer vegan food"}
    ]
    
    result = extract_user_preferences({"messages": messages})
    
    assert "likes_boutique_hotels" in result["user_preferences"]
    assert "diet_preference" in result["user_preferences"]