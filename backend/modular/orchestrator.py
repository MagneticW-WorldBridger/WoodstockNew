"""
ORCHESTRATOR AGENT - JORGE'S MAIN PATTERN
NO TOOLS - Only routes requests to specialized agents
"""

from pydantic_ai import Agent, RunContext
from .dependencies import SharedDeps, ChainResult, ChainCommand, ChainStep
from .customer_agent import customer_agent
from .order_agent import order_agent  
from .product_agent import product_agent
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# ============================================================================
# MAIN ORCHESTRATOR (NO TOOLS - ONLY ROUTING)
# ============================================================================

orchestrator_agent = Agent[SharedDeps, str](
    'openai:gpt-4o',
    deps_type=SharedDeps,
    instructions="""
    You are the MAIN ORCHESTRATOR for Woodstock Furniture AI.
    
    CRITICAL: You have NO TOOLS yourself. Your job is to:
    1. ANALYZE user intent 
    2. ROUTE to specialized agents via delegate_to_agent() function
    3. ORCHESTRATE multi-step chains for complex requests
    
    AVAILABLE SPECIALISTS:
    - customer_agent: Find customers by phone/email (use for customer lookup)
    - order_agent: Handle order history/details (use for order queries)  
    - product_agent: Search products/catalog (use for product searches)
    
    ROUTING RULES:
    - "my phone is X" → customer_agent
    - "show my orders" → order_agent (needs customer_id from customer_agent first)
    - "grey sofas" → product_agent
    - "tell me everything about customer X" → CHAINED: customer→orders→details
    
    NEVER try to search/lookup data yourself. ALWAYS delegate.
    """
)

@orchestrator_agent.tool  
async def delegate_to_agent(ctx: RunContext[SharedDeps], agent_name: str, operation: str, params: Dict[str, Any]) -> str:
    """
    Delegate a task to a specialized agent
    
    Args:
        agent_name: "customer_agent", "order_agent", "product_agent"
        operation: The operation to perform
        params: Parameters for the operation
    """
    
    print(f"🎯 Orchestrator: Delegating {operation} to {agent_name} with {params}")
    
    try:
        if agent_name == "customer_agent":
            result = await customer_agent.run(
                f"Search for customer: {params.get('identifier', '')}",
                deps=ctx.deps
            )
            return f"CUSTOMER_RESULT: {json.dumps(result.output.model_dump())}"
            
        elif agent_name == "order_agent":
            result = await order_agent.run(
                f"Handle order operation: {operation}",
                deps=ctx.deps
            )
            return f"ORDER_RESULT: {json.dumps(result.output.model_dump())}"
            
        elif agent_name == "product_agent":
            result = await product_agent.run(
                f"Search products: {params.get('query', '')}",
                deps=ctx.deps
            )
            return f"PRODUCT_RESULT: {json.dumps(result.output.model_dump())}"
            
        else:
            return f"ERROR: Unknown agent {agent_name}"
            
    except Exception as e:
        print(f"❌ Orchestrator delegation error: {e}")
        return f"ERROR: Delegation to {agent_name} failed: {str(e)}"

# ============================================================================
# CHAIN EXECUTOR (ASYNC MULTI-STEP WORKFLOWS)
# ============================================================================

class ChainExecutor:
    """Executes multi-step workflows asynchronously - Jorge's pattern"""
    
    def __init__(self):
        self.active_chains: Dict[str, ChainCommand] = {}
    
    async def execute_customer_order_chain(self, deps: SharedDeps, identifier: str) -> ChainResult:
        """
        Execute the classic chain: phone/email → customer → orders → details → HTML
        This is Jorge's main use case example
        """
        
        chain_id = str(uuid.uuid4())[:8]
        print(f"🔗 Starting customer order chain {chain_id} for {identifier}")
        
        # Define the chain steps
        chain = ChainCommand(
            chain_id=chain_id,
            user_goal=f"Get complete customer journey for {identifier}",
            steps=[
                ChainStep(
                    step_id="step_1_customer",
                    agent_name="customer_agent", 
                    tool_name="search_customer",
                    params={"identifier": identifier, "type": "auto"}
                ),
                ChainStep(
                    step_id="step_2_orders",
                    agent_name="order_agent",
                    tool_name="order_operations", 
                    params={"operation": "list_by_customer", "customer_id": None},  # Will be filled from step 1
                    depends_on="step_1_customer"
                ),
                ChainStep(
                    step_id="step_3_analytics",
                    agent_name="order_agent",
                    tool_name="order_operations",
                    params={"operation": "get_analytics", "customer_id": None},  # Optional analytics
                    depends_on="step_1_customer"
                )
            ]
        )
        
        self.active_chains[chain_id] = chain
        intermediate_results = []
        
        try:
            # Execute steps sequentially with dependency resolution
            for i, step in enumerate(chain.steps):
                print(f"🔗 Executing step {i+1}/{len(chain.steps)}: {step.step_id}")
                
                # Resolve dependencies from previous steps
                resolved_params = self._resolve_step_params(step.params, intermediate_results)
                
                # Execute step with appropriate agent
                if step.agent_name == "customer_agent":
                    result = await customer_agent.run(
                        f"Find customer {resolved_params.get('identifier')}",
                        deps=deps
                    )
                    step_result = result.output.model_dump()
                    
                elif step.agent_name == "order_agent":
                    # Call order agent's tool directly using the async function
                    from .order_agent import order_operations
                    fake_ctx = type('Context', (), {'deps': deps})()  # Mock context
                    step_result = await order_operations(fake_ctx, **resolved_params)
                    step_result = step_result.model_dump()
                    
                else:
                    step_result = {"error": f"Unknown agent {step.agent_name}"}
                
                # Store result and mark completed
                step.result = step_result
                step.completed = True
                intermediate_results.append({
                    "step_id": step.step_id,
                    "result": step_result
                })
                
                print(f"✅ Step {step.step_id} completed")
                
                # Stop if step failed
                if step_result.get("found") == False and step.step_id == "step_1_customer":
                    print(f"❌ Chain stopped - customer not found")
                    break
            
            # Generate final HTML output combining all results
            final_html = self._generate_chain_html(intermediate_results, identifier)
            
            return ChainResult(
                success=True,
                steps_completed=len([s for s in chain.steps if s.completed]),
                total_steps=len(chain.steps),
                final_output=final_html,
                intermediate_results=intermediate_results
            )
            
        except Exception as e:
            print(f"❌ Chain execution failed: {e}")
            return ChainResult(
                success=False,
                steps_completed=len([s for s in chain.steps if s.completed]),
                total_steps=len(chain.steps),
                error=str(e),
                intermediate_results=intermediate_results
            )
        
        finally:
            # Cleanup
            if chain_id in self.active_chains:
                del self.active_chains[chain_id]
    
    def _resolve_step_params(self, params: Dict[str, Any], previous_results: list) -> Dict[str, Any]:
        """Resolve parameters using results from previous steps"""
        
        resolved = params.copy()
        
        # Find customer_id from step_1_customer result
        for result_data in previous_results:
            if result_data["step_id"] == "step_1_customer":
                customer_result = result_data["result"]
                if customer_result.get("found") and customer_result.get("customer_id"):
                    resolved["customer_id"] = customer_result["customer_id"]
                break
        
        return resolved
    
    def _generate_chain_html(self, results: list, identifier: str) -> str:
        """Generate beautiful HTML combining all chain results"""
        
        html_parts = []
        html_parts.append(f"<div class='customer-journey'>")
        html_parts.append(f"<h2>🎯 Complete Customer Journey: {identifier}</h2>")
        
        # Add each step's HTML
        for result_data in results:
            step_result = result_data["result"] 
            if step_result.get("html"):
                html_parts.append(step_result["html"])
        
        html_parts.append("</div>")
        
        return "\n".join(html_parts)

# Global chain executor instance
chain_executor = ChainExecutor()
