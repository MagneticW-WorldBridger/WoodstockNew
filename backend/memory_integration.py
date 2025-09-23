"""
🔗 MEMORY INTEGRATION MODULE
Seamlessly integrate enhanced memory with existing conversation system
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enhanced_memory_system import enhanced_memory, init_enhanced_memory
from conversation_memory import memory as simple_memory

class MemoryOrchestrator:
    """
    Orchestrates between simple conversation memory and enhanced persistent memory
    """
    
    def __init__(self):
        self.enhanced_ready = False
        print("🎭 Memory Orchestrator initialized")
    
    async def ensure_enhanced_memory(self):
        """Ensure enhanced memory is initialized"""
        if not self.enhanced_ready and enhanced_memory:
            self.enhanced_ready = True
            print("✅ Enhanced memory is ready")
    
    async def save_message_with_enhancement(self, conversation_id: str, 
                                          message_role: str, message_content: str,
                                          user_identifier: str,
                                          function_name: str = None,
                                          function_args: Dict = None,
                                          function_result: Any = None):
        """Save message to both simple and enhanced memory systems"""
        
        # Always save to simple memory (existing system)
        if message_role == 'user':
            await simple_memory.save_user_message(conversation_id, message_content)
        else:
            await simple_memory.save_assistant_message(
                conversation_id, message_content, function_name, function_args, function_result
            )
        
        # Enhanced memory processing (async, non-blocking)
        await self.ensure_enhanced_memory()
        if self.enhanced_ready:
            try:
                # Process conversation every 5 messages for efficiency
                async with simple_memory.pool.acquire() as conn:
                    message_count = await conn.fetchval(
                        "SELECT COUNT(*) FROM chatbot_messages WHERE conversation_id = $1", 
                        conversation_id
                    )
                    
                    # Process insights periodically or at conversation end
                    if message_count % 5 == 0 or "goodbye" in message_content.lower():
                        print(f"🧠 Processing memory insights for conversation {conversation_id}")
                        asyncio.create_task(
                            enhanced_memory.process_conversation_memory(conversation_id, user_identifier)
                        )
                        
            except Exception as e:
                print(f"⚠️ Enhanced memory processing failed (non-critical): {e}")

    async def get_enhanced_context(self, query: str, user_identifier: str) -> str:
        """Get enhanced context for better AI responses"""
        await self.ensure_enhanced_memory()
        if not self.enhanced_ready:
            return ""
            
        try:
            context_data = await enhanced_memory.get_conversation_context(query, user_identifier)
            
            if context_data['context_strength'] == 0:
                return ""
            
            # Format context for AI consumption
            context_parts = []
            
            # Add entities
            if context_data['entities']:
                entities_text = "Relevant context about the user:\n"
                for entity in context_data['entities'][:3]:
                    entities_text += f"- {entity['name']} ({entity['entity_type']}): {', '.join(entity['observations'])}\n"
                context_parts.append(entities_text)
            
            # Add long-term memories
            if context_data['memories']:
                memories_text = "Important things to remember:\n"
                for memory in context_data['memories']:
                    memories_text += f"- {memory['memory_content']} (importance: {memory['importance_score']:.1f})\n"
                context_parts.append(memories_text)
            
            # Add relationships
            if context_data['relations']:
                relations_text = "Relevant relationships:\n"
                for relation in context_data['relations'][:3]:
                    relations_text += f"- {relation['from_name']} {relation['relation_type']} {relation['to_name']}\n"
                context_parts.append(relations_text)
            
            if context_parts:
                return "\n\n".join(context_parts) + "\n\nUse this context to provide more personalized and relevant responses.\n"
                
        except Exception as e:
            print(f"⚠️ Enhanced context retrieval failed: {e}")
            
        return ""

    async def get_memory_summary_for_user(self, user_identifier: str) -> Dict[str, Any]:
        """Get comprehensive memory summary for a user"""
        await self.ensure_enhanced_memory()
        if not self.enhanced_ready:
            return {"status": "enhanced_memory_not_ready"}
        
        try:
            stats = await enhanced_memory.get_memory_stats(user_identifier)
            
            # Get recent entities
            recent_entities = await enhanced_memory.semantic_search_entities(
                "recent customer information", user_identifier, limit=5, min_similarity=0.1
            )
            
            # Get important memories
            important_memories = await enhanced_memory.retrieve_long_term_memories(
                "important preferences facts", user_identifier, limit=5, min_similarity=0.1
            )
            
            return {
                "status": "ready",
                "stats": stats,
                "recent_entities": recent_entities,
                "important_memories": important_memories
            }
            
        except Exception as e:
            print(f"❌ Error getting memory summary: {e}")
            return {"status": "error", "message": str(e)}

    async def forget_user_data(self, user_identifier: str):
        """GDPR-compliant data deletion"""
        await self.ensure_enhanced_memory()
        if not self.enhanced_ready:
            print("⚠️ Enhanced memory not ready for deletion")
            return
        
        try:
            async with enhanced_memory.pool.acquire() as conn:
                # Delete all user-specific data
                await conn.execute("DELETE FROM long_term_memories WHERE user_context = $1", user_identifier)
                await conn.execute("DELETE FROM memory_entities WHERE user_context = $1", user_identifier)
                
                print(f"🗑️ Deleted all memory data for user: {user_identifier}")
                
        except Exception as e:
            print(f"❌ Error deleting user memory data: {e}")

# Global orchestrator instance
orchestrator = MemoryOrchestrator()

async def initialize_memory_orchestrator(db_url: str, openai_api_key: str):
    """Initialize the complete memory system"""
    global orchestrator
    
    # Initialize simple memory
    if not simple_memory.pool:
        await simple_memory.init_db()
    
    # Initialize enhanced memory
    await init_enhanced_memory(db_url, openai_api_key)
    
    # Ensure orchestrator is ready
    await orchestrator.ensure_enhanced_memory()
    
    print("🎭 Memory Orchestrator fully initialized!")
    return orchestrator
