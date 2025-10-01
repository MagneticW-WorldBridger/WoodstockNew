#!/usr/bin/env python3
"""
🧪 CONVERSATIONAL TESTING FRAMEWORK
Automated testing of conversation flows using discourse analysis
"""

import asyncio
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass
import httpx

@dataclass
class ConversationTestCase:
    """Test case for conversation validation"""
    name: str
    scenario: str
    messages: List[str]
    expected_functions: List[str]
    expected_patterns: List[str]
    max_turns: int = 15
    should_escalate: bool = False

class ConversationTester:
    """Automated conversation testing using psychological UX principles"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_cases = self.load_test_scenarios()
    
    def load_test_scenarios(self) -> List[ConversationTestCase]:
        """Load conversation test scenarios based on analysis reports"""
        return [
            ConversationTestCase(
                name="customer_identification_flow",
                scenario="User provides phone for identification and expects recognition",
                messages=[
                    "My phone is 407-288-6040",
                    "Show me my orders",
                    "Details on the most recent one"
                ],
                expected_functions=["get_customer_by_phone", "get_orders_by_customer", "get_order_details"],
                expected_patterns=["Hello", "Great to see you", "order history", "order details"]
            ),
            
            ConversationTestCase(
                name="product_discovery_flow", 
                scenario="User searches for products and expects easy filtering options",
                messages=[
                    "Show me sectionals",
                    "Under $2000",
                    "In gray color"
                ],
                expected_functions=["search_magento_products", "search_products_by_price_range", "search_products_by_color"],
                expected_patterns=["FOUND", "OPTIONS", "What would you like to do next", "Filter by"]
            ),
            
            ConversationTestCase(
                name="support_escalation_flow",
                scenario="User has problem and expects immediate support escalation", 
                messages=[
                    "My delivery was damaged",
                    "This is the third time this happened",
                    "I need this fixed now"
                ],
                expected_functions=["handle_support_escalation"],
                expected_patterns=["frustrating", "resolved right away", "HIGH PRIORITY", "Upload Photos"],
                should_escalate=True
            ),
            
            ConversationTestCase(
                name="conversation_repair_test",
                scenario="User indicates confusion and AI repairs the conversation",
                messages=[
                    "I'm looking for a couch",
                    "No, that's not what I meant", 
                    "Something more modern for a small room"
                ],
                expected_functions=["search_magento_products"],
                expected_patterns=["I see I may have misunderstood", "Are you asking about", "modern", "small room"]
            ),
            
            ConversationTestCase(
                name="error_recovery_test",
                scenario="Function fails and AI provides graceful alternatives",
                messages=[
                    "999-999-9999",  # Non-existent customer
                    "I'm getting frustrated"
                ],
                expected_functions=["get_customer_by_phone"],
                expected_patterns=["don't have a customer record", "Let me help you get started", "What brings you"]
            ),
            
            ConversationTestCase(
                name="long_term_memory_test",
                scenario="User asks about previous conversations",
                messages=[
                    "Do you remember what I told you about my living room?",
                    "What were my furniture preferences?"
                ],
                expected_functions=["recall_user_memory"],
                expected_patterns=["Here's what I remember", "Let's build that context", "previous conversations"]
            )
        ]
    
    async def run_conversation_test(self, test_case: ConversationTestCase) -> Dict[str, Any]:
        """Run a single conversation test case"""
        print(f"🧪 Testing: {test_case.name}")
        
        results = {
            "test_name": test_case.name,
            "scenario": test_case.scenario,
            "status": "running",
            "messages": [],
            "functions_called": [],
            "patterns_found": [],
            "errors": [],
            "duration": 0,
            "discourse_quality": {}
        }
        
        start_time = time.time()
        
        try:
            for i, message in enumerate(test_case.messages):
                print(f"   📝 Turn {i+1}: {message[:50]}...")
                
                # Send message to chat API
                response = await self.send_chat_message(message)
                
                if response:
                    results["messages"].append({
                        "turn": i+1,
                        "user": message,
                        "assistant": response.get("content", ""),
                        "functions": self.extract_functions_called(response)
                    })
                    
                    # Track functions called
                    functions = self.extract_functions_called(response)
                    results["functions_called"].extend(functions)
                    
                    # Check for expected patterns
                    patterns = self.check_patterns(response.get("content", ""), test_case.expected_patterns)
                    results["patterns_found"].extend(patterns)
                
                # Small delay to simulate natural conversation
                await asyncio.sleep(0.5)
            
            # Analyze discourse quality
            results["discourse_quality"] = self.analyze_discourse_quality(results["messages"])
            
            # Determine test result
            functions_match = all(func in results["functions_called"] for func in test_case.expected_functions)
            patterns_match = len(results["patterns_found"]) >= len(test_case.expected_patterns) * 0.7
            
            if functions_match and patterns_match:
                results["status"] = "PASSED"
            else:
                results["status"] = "FAILED"
                if not functions_match:
                    results["errors"].append(f"Expected functions {test_case.expected_functions}, got {results['functions_called']}")
                if not patterns_match:
                    results["errors"].append(f"Expected patterns not found: {test_case.expected_patterns}")
        
        except Exception as e:
            results["status"] = "ERROR"
            results["errors"].append(str(e))
        
        results["duration"] = time.time() - start_time
        print(f"   ✅ Test completed: {results['status']} ({results['duration']:.2f}s)")
        
        return results
    
    async def send_chat_message(self, message: str) -> Dict[str, Any]:
        """Send message to chat API and get response"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    json={
                        "messages": [{"role": "user", "content": message}],
                        "stream": False,
                        "user_identifier": "test_user_conversation_testing"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("choices") and len(data["choices"]) > 0:
                        return data["choices"][0].get("message", {})
                
                return {"content": f"Error: {response.status_code}"}
                
        except Exception as e:
            return {"content": f"Connection error: {str(e)}"}
    
    def extract_functions_called(self, response: Dict[str, Any]) -> List[str]:
        """Extract function names from response"""
        content = response.get("content", "")
        functions = []
        
        # Look for function result patterns
        if "Function Result (" in content:
            import re
            matches = re.findall(r'Function Result \(([^)]+)\)', content)
            functions.extend(matches)
        
        return functions
    
    def check_patterns(self, content: str, expected_patterns: List[str]) -> List[str]:
        """Check if expected discourse patterns are present"""
        found_patterns = []
        
        for pattern in expected_patterns:
            if pattern.lower() in content.lower():
                found_patterns.append(pattern)
        
        return found_patterns
    
    def analyze_discourse_quality(self, messages: List[Dict]) -> Dict[str, float]:
        """Analyze conversation for discourse coherence"""
        if len(messages) < 2:
            return {"insufficient_data": True}
        
        quality_scores = {
            "referential_coherence": 0.0,
            "topical_progression": 0.0,
            "response_variety": 0.0,
            "anticipatory_design": 0.0
        }
        
        # Check referential coherence (does AI reference previous context?)
        coherence_count = 0
        for i in range(1, len(messages)):
            assistant_response = messages[i].get("assistant", "")
            previous_user = messages[i-1].get("user", "")
            
            # Simple checks for referential coherence
            if any(word in assistant_response.lower() for word in ["based on", "from your", "you mentioned", "your previous"]):
                coherence_count += 1
        
        quality_scores["referential_coherence"] = coherence_count / max(len(messages)-1, 1)
        
        # Check response variety (does AI avoid repetition?)
        responses = [msg.get("assistant", "") for msg in messages]
        unique_responses = len(set(responses))
        quality_scores["response_variety"] = unique_responses / max(len(responses), 1)
        
        # Check anticipatory design (does AI provide next action suggestions?)
        anticipatory_count = 0
        for msg in messages:
            assistant_response = msg.get("assistant", "")
            if any(phrase in assistant_response for phrase in ["What would you like to do", "What's next", "**", "•"]):
                anticipatory_count += 1
        
        quality_scores["anticipatory_design"] = anticipatory_count / max(len(messages), 1)
        
        return quality_scores
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all conversation test cases"""
        print("🧪 Starting Conversational Testing Framework...")
        print(f"📊 Running {len(self.test_cases)} test scenarios")
        
        results = {
            "timestamp": time.time(),
            "total_tests": len(self.test_cases),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_results": [],
            "overall_quality": {}
        }
        
        for test_case in self.test_cases:
            test_result = await self.run_conversation_test(test_case)
            results["test_results"].append(test_result)
            
            if test_result["status"] == "PASSED":
                results["passed"] += 1
            elif test_result["status"] == "FAILED":
                results["failed"] += 1
            else:
                results["errors"] += 1
        
        # Calculate overall discourse quality
        all_quality_scores = [t["discourse_quality"] for t in results["test_results"] if t["discourse_quality"]]
        if all_quality_scores:
            avg_quality = {}
            for metric in ["referential_coherence", "response_variety", "anticipatory_design"]:
                scores = [q.get(metric, 0) for q in all_quality_scores if metric in q]
                avg_quality[metric] = sum(scores) / len(scores) if scores else 0
            results["overall_quality"] = avg_quality
        
        print(f"\n📊 TESTING COMPLETE:")
        print(f"   ✅ Passed: {results['passed']}/{results['total_tests']}")
        print(f"   ❌ Failed: {results['failed']}/{results['total_tests']}")
        print(f"   🚨 Errors: {results['errors']}/{results['total_tests']}")
        
        if results["overall_quality"]:
            print(f"\n🧠 DISCOURSE QUALITY SCORES:")
            for metric, score in results["overall_quality"].items():
                print(f"   {metric}: {score:.2f}")
        
        return results

# 🚀 QUICK TEST RUNNER FOR IMMEDIATE VALIDATION
async def quick_conversation_test():
    """Quick test of basic conversation flow"""
    tester = ConversationTester()
    
    # Test key scenarios quickly
    quick_tests = [
        ConversationTestCase(
            name="basic_customer_flow",
            scenario="Customer identification and order lookup",
            messages=["407-288-6040", "Show my orders"],
            expected_functions=["get_customer_by_phone", "get_orders_by_customer"],
            expected_patterns=["Hello", "orders"]
        ),
        ConversationTestCase(
            name="product_search_flow", 
            scenario="Product search with anticipatory design",
            messages=["Show me sectionals"],
            expected_functions=["search_magento_products"],
            expected_patterns=["FOUND", "What would you like to do next"]
        )
    ]
    
    print("🧪 QUICK CONVERSATION VALIDATION...")
    for test in quick_tests:
        result = await tester.run_conversation_test(test)
        print(f"   {test.name}: {result['status']}")
    
    return "✅ Quick validation complete"

if __name__ == "__main__":
    # Run quick test when called directly
    asyncio.run(quick_conversation_test())



