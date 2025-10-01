"""
🚀 MEMORY MANAGEMENT API ENDPOINTS
RESTful endpoints for testing, managing, and monitoring the enhanced memory system
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from memory_integration import orchestrator
from enhanced_memory_system import enhanced_memory

# Create API router
memory_router = APIRouter(prefix="/memory", tags=["Enhanced Memory"])

# Pydantic models for API
class MemoryQuery(BaseModel):
    query: str
    user_identifier: str
    limit: int = 5
    min_similarity: float = 0.6

class MemoryEntity(BaseModel):
    name: str
    entity_type: str
    observations: List[str]
    confidence: float = 1.0
    metadata: Dict[str, Any] = {}

class MemoryRelation(BaseModel):
    from_entity: str
    to_entity: str
    relation_type: str
    strength: float = 1.0
    confidence: float = 1.0
    metadata: Dict[str, Any] = {}

class LongTermMemory(BaseModel):
    content: str
    memory_type: str = 'general'
    importance: float = 0.5

# Memory Management Endpoints
@memory_router.get("/status")
async def memory_system_status():
    """Get overall memory system status"""
    try:
        await orchestrator.ensure_enhanced_memory()
        
        if not enhanced_memory:
            return {"status": "not_initialized", "message": "Enhanced memory not initialized"}
        
        # Get database stats
        async with enhanced_memory.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM memory_entities) as total_entities,
                    (SELECT COUNT(*) FROM memory_relations) as total_relations,
                    (SELECT COUNT(*) FROM long_term_memories) as total_memories,
                    (SELECT COUNT(*) FROM conversation_summaries) as total_summaries,
                    (SELECT COUNT(DISTINCT user_context) FROM memory_entities) as unique_users
            """)
            
        return {
            "status": "operational",
            "message": "Enhanced memory system is running",
            "stats": dict(stats) if stats else {},
            "system_ready": orchestrator.enhanced_ready
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@memory_router.get("/user/{user_identifier}/summary")
async def get_user_memory_summary(user_identifier: str):
    """Get comprehensive memory summary for a user"""
    try:
        summary = await orchestrator.get_memory_summary_for_user(user_identifier)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/search/entities")
async def search_entities(query: MemoryQuery):
    """Semantic search for memory entities"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
            
        results = await enhanced_memory.semantic_search_entities(
            query.query, query.user_identifier, query.limit, query.min_similarity
        )
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/search/memories")
async def search_long_term_memories(query: MemoryQuery):
    """Search long-term memories"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
            
        results = await enhanced_memory.retrieve_long_term_memories(
            query.query, query.user_identifier, query.limit, query.min_similarity
        )
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/context/{user_identifier}")
async def get_user_context(user_identifier: str, query: str = "general context"):
    """Get enhanced conversation context for a user"""
    try:
        context = await orchestrator.get_enhanced_context(query, user_identifier)
        
        # Also get structured context data
        await orchestrator.ensure_enhanced_memory()
        if enhanced_memory:
            context_data = await enhanced_memory.get_conversation_context(query, user_identifier)
            return {
                "formatted_context": context,
                "raw_data": context_data,
                "has_context": bool(context.strip())
            }
        else:
            return {
                "formatted_context": context,
                "raw_data": {},
                "has_context": False
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/entity/create")
async def create_memory_entity(entity: MemoryEntity, user_identifier: str):
    """Create a new memory entity"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
        
        from enhanced_memory_system import MemoryEntity as MemEntityClass
        mem_entity = MemEntityClass(
            name=entity.name,
            entity_type=entity.entity_type,
            observations=entity.observations,
            confidence=entity.confidence,
            metadata=entity.metadata
        )
        
        entity_id = await enhanced_memory.create_entity(mem_entity, user_identifier)
        return {"success": True, "entity_id": entity_id, "message": f"Created entity: {entity.name}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/relation/create")
async def create_memory_relation(relation: MemoryRelation, user_identifier: str):
    """Create a new memory relation"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
        
        from enhanced_memory_system import MemoryRelation as MemRelationClass
        mem_relation = MemRelationClass(
            from_entity=relation.from_entity,
            to_entity=relation.to_entity,
            relation_type=relation.relation_type,
            strength=relation.strength,
            confidence=relation.confidence,
            metadata=relation.metadata
        )
        
        await enhanced_memory.create_relation(mem_relation, user_identifier)
        return {"success": True, "message": f"Created relation: {relation.from_entity} -[{relation.relation_type}]-> {relation.to_entity}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/memory/store")
async def store_long_term_memory(memory: LongTermMemory, user_identifier: str, conversation_id: Optional[str] = None):
    """Store a long-term memory"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
        
        await enhanced_memory.store_long_term_memory(
            content=memory.content,
            user_context=user_identifier,
            memory_type=memory.memory_type,
            importance=memory.importance,
            conversation_id=conversation_id
        )
        
        return {"success": True, "message": f"Stored memory: {memory.content[:50]}..."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/conversation/{conversation_id}/process")
async def process_conversation_memory(conversation_id: str, user_identifier: str, background_tasks: BackgroundTasks):
    """Manually trigger conversation memory processing"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
        
        # Process in background
        background_tasks.add_task(
            enhanced_memory.process_conversation_memory,
            conversation_id,
            user_identifier
        )
        
        return {"success": True, "message": f"Started processing conversation {conversation_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/conversation/{conversation_id}/insights")
async def get_conversation_insights(conversation_id: str, user_identifier: str):
    """Get insights from a specific conversation"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
        
        insights = await enhanced_memory.extract_conversation_insights(conversation_id, user_identifier)
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Administrative Endpoints
@memory_router.delete("/user/{user_identifier}")
async def forget_user_data(user_identifier: str):
    """GDPR-compliant deletion of all user memory data"""
    try:
        await orchestrator.forget_user_data(user_identifier)
        return {"success": True, "message": f"Deleted all memory data for user: {user_identifier}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.post("/maintenance/cleanup")
async def cleanup_old_memories(days_old: int = 90, min_access_count: int = 1):
    """Clean up old, unused memories"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
        
        await enhanced_memory.cleanup_old_memories(days_old, min_access_count)
        return {"success": True, "message": f"Cleaned up memories older than {days_old} days"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Testing Endpoints
@memory_router.post("/test/populate-sample-data")
async def populate_sample_memory_data(user_identifier: str = "test_user"):
    """Populate sample memory data for testing"""
    try:
        await orchestrator.ensure_enhanced_memory()
        if not enhanced_memory:
            raise HTTPException(status_code=503, detail="Enhanced memory not available")
        
        # Create sample entities
        from enhanced_memory_system import MemoryEntity as MemEntityClass, MemoryRelation as MemRelationClass
        
        entities = [
            MemEntityClass("Janice Daniels", "customer", ["Purchased sectional sofa", "Lives in Covington GA", "Phone 407-288-6040"]),
            MemEntityClass("Repose Avenue Sectional", "product", ["Popular sectional", "Dual power reclining", "Defender Sand color"]),
            MemEntityClass("Order #0710544II27", "order", ["$1,997.50 total", "Delivered July 2025", "3-piece sectional set"])
        ]
        
        for entity in entities:
            await enhanced_memory.create_entity(entity, user_identifier)
        
        # Create sample relations
        relations = [
            MemRelationClass("Janice Daniels", "Order #0710544II27", "placed_order", 1.0),
            MemRelationClass("Order #0710544II27", "Repose Avenue Sectional", "contains_product", 1.0),
            MemRelationClass("Janice Daniels", "Repose Avenue Sectional", "purchased", 0.9)
        ]
        
        for relation in relations:
            await enhanced_memory.create_relation(relation, user_identifier)
        
        # Create sample memories
        memories = [
            "Customer prefers sectional furniture over individual pieces",
            "Janice is a high-value customer with excellent payment history", 
            "Customer mentioned needing furniture for large family gatherings"
        ]
        
        for memory in memories:
            await enhanced_memory.store_long_term_memory(memory, user_identifier, memory_type="preference")
        
        return {"success": True, "message": f"Created sample data for {user_identifier}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@memory_router.get("/test/demo-context")
async def demo_enhanced_context(user_identifier: str = "test_user", query: str = "sectional furniture"):
    """Demonstrate enhanced context generation"""
    try:
        context = await orchestrator.get_enhanced_context(query, user_identifier)
        await orchestrator.ensure_enhanced_memory()
        
        if enhanced_memory:
            context_data = await enhanced_memory.get_conversation_context(query, user_identifier)
            stats = await enhanced_memory.get_memory_stats(user_identifier)
            
            return {
                "query": query,
                "user": user_identifier,
                "enhanced_context": context,
                "context_data": context_data,
                "memory_stats": stats,
                "demo_successful": bool(context.strip())
            }
        else:
            return {"error": "Enhanced memory not available"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




