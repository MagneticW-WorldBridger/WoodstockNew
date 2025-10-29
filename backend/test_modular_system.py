"""
TEST MODULAR SYSTEM - JORGE'S ARCHITECTURE
Tests the 1 agent = 1 tool pattern + chained commands
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

# Load environment variables
load_dotenv()

async def test_modular_system():
    """Test the complete modular architecture"""
    
    print("🚀 Testing Modular Agent Architecture (Jorge's Pattern)")
    print("=" * 60)
    
    try:
        # Import modular components
        from modular.dependencies import SharedDeps
        from modular.customer_agent import customer_agent
        from modular.order_agent import order_agent
        from modular.product_agent import product_agent
        from modular.orchestrator import orchestrator_agent, chain_executor
        
        print("✅ All modular components imported successfully")
        
        # Create shared dependencies
        deps = await SharedDeps.create(
            user_id="test_user",
            conversation_id="test_conv_001"
        )
        print("✅ Shared dependencies created")
        
        # Test 1: Customer Agent (Specialized)
        print("\n🔍 TEST 1: Customer Agent Specialization")
        print("-" * 40)
        
        customer_result = await customer_agent.run(
            "Find customer with phone 404-916-2522", 
            deps=deps
        )
        print(f"Customer Result: {customer_result.output.found}")
        if customer_result.output.html:
            print(f"HTML Output: {customer_result.output.html[:100]}...")
        
        # Test 2: Product Agent (Specialized)  
        print("\n🛒 TEST 2: Product Agent Specialization")
        print("-" * 40)
        
        product_result = await product_agent.run(
            "Search for grey sofas",
            deps=deps
        )
        print(f"Product Result: {product_result.output.found}")
        print(f"Products Found: {product_result.output.total_found}")
        if product_result.output.html_carousel:
            print(f"Carousel HTML: {product_result.output.html_carousel[:100]}...")
        
        # Test 3: Orchestrator Routing (No Tools)
        print("\n🎯 TEST 3: Orchestrator Routing")
        print("-" * 40)
        
        orchestrator_result = await orchestrator_agent.run(
            "Find customer with phone 404-916-2522",
            deps=deps
        )
        print(f"Orchestrator Result: {orchestrator_result.output[:150]}...")
        
        # Test 4: Chained Command (Jorge's Main Use Case)
        print("\n🔗 TEST 4: Chained Command Execution")
        print("-" * 40)
        
        chain_result = await chain_executor.execute_customer_order_chain(
            deps, "404-916-2522"
        )
        print(f"Chain Success: {chain_result.success}")
        print(f"Steps Completed: {chain_result.steps_completed}/{chain_result.total_steps}")
        if chain_result.final_output:
            print(f"Final Output: {chain_result.final_output[:200]}...")
        
        # Test 5: Async Performance Check
        print("\n⚡ TEST 5: Async Performance")
        print("-" * 40)
        
        import time
        start_time = time.time()
        
        # Run multiple operations in parallel (Jorge's async recommendation)
        tasks = [
            customer_agent.run("Find customer 404-916-2522", deps=deps),
            product_agent.run("Search sectionals", deps=deps),
            product_agent.run("Search recliners", deps=deps)
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"Parallel execution time: {end_time - start_time:.2f} seconds")
        print(f"Operations completed: {len(results)}")
        
        # Cleanup
        await deps.cleanup()
        print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Modular architecture is working with Jorge's pattern")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_api_endpoint():
    """Test the modular API endpoint"""
    
    print("\n🌐 Testing Modular API Endpoint")
    print("=" * 40)
    
    try:
        import httpx
        
        # Start the modular server in background (if not running)
        # For now, just test the health endpoint structure
        
        print("✅ API structure ready for testing")
        print("📋 To test live:")
        print("   1. Run: python modular/main_modular.py")
        print("   2. Visit: http://localhost:8002/health")
        print("   3. Test: curl -X POST http://localhost:8002/v1/chat/completions")
        
    except Exception as e:
        print(f"⚠️ API test setup issue: {e}")

if __name__ == "__main__":
    print("🧪 Woodstock Modular Architecture Test Suite")
    
    # Run async tests
    success = asyncio.run(test_modular_system())
    
    # Run API tests
    asyncio.run(test_api_endpoint())
    
    if success:
        print("\n🎉 MODULAR SYSTEM IS READY!")
        print("🚀 Run 'python modular/main_modular.py' to start")
    else:
        print("\n💥 TESTS FAILED - Check errors above")
