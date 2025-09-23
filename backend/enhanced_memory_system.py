"""
🧠 ENHANCED PERSISTENT MEMORY SYSTEM
Three-tier memory architecture combining the best of Mem0, Memento MCP, and LangGraph
"""

import asyncio
import json
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import asyncpg
import os
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
import openai
from openai import AsyncOpenAI

@dataclass
class MemoryEntity:
    """Memory entity inspired by Memento MCP"""
    name: str
    entity_type: str  # 'customer', 'order', 'product', 'preference', 'issue'
    observations: List[str]
    confidence: float = 1.0
    created_at: datetime = None
    last_updated: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class MemoryRelation:
    """Memory relations between entities"""
    from_entity: str
    to_entity: str
    relation_type: str  # 'purchased', 'prefers', 'complained_about', 'similar_to'
    strength: float = 1.0
    confidence: float = 1.0
    created_at: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class EnhancedMemorySystem:
    """
    Three-tier persistent memory system:
    1. Short-term: Current conversation (existing PostgreSQL)
    2. Medium-term: Session knowledge graph (PostgreSQL + vectors)
    3. Long-term: Cross-conversation semantic memory (vector search)
    """
    
    def __init__(self, db_url: str, openai_api_key: str):
        self.db_url = db_url
        self.pool = None
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        
        # Initialize sentence transformer for embeddings (lightweight, fast)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        print("🧠 Enhanced Memory System initialized")
        
    async def init_db(self):
        """Initialize enhanced memory tables"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.db_url, min_size=2, max_size=5)
            print("✅ Enhanced Memory Pool initialized")
            
        async with self.pool.acquire() as conn:
            # Create vector extension if not exists
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Register vector types with asyncpg
            from pgvector.asyncpg import register_vector
            await register_vector(conn)
            
            # Memory entities table (inspired by Memento MCP)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_entities (
                    entity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    entity_type VARCHAR(100) NOT NULL,
                    observations JSONB NOT NULL DEFAULT '[]',
                    confidence FLOAT DEFAULT 1.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}',
                    embedding vector(384),  -- MiniLM embeddings are 384-dimensional
                    user_context VARCHAR(255) -- Which user this entity belongs to
                );
            """)
            
            # Memory relations table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_relations (
                    relation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    from_entity_id UUID REFERENCES memory_entities(entity_id) ON DELETE CASCADE,
                    to_entity_id UUID REFERENCES memory_entities(entity_id) ON DELETE CASCADE,
                    relation_type VARCHAR(100) NOT NULL,
                    strength FLOAT DEFAULT 1.0,
                    confidence FLOAT DEFAULT 1.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'
                );
            """)
            
            # Conversation summaries table (inspired by LangGraph)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    summary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    conversation_id UUID REFERENCES chatbot_conversations(conversation_id) ON DELETE CASCADE,
                    summary_text TEXT NOT NULL,
                    key_entities JSONB DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    embedding vector(384)
                );
            """)
            
            # Long-term memories table (inspired by Mem0)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memories (
                    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_context VARCHAR(255) NOT NULL,
                    memory_content TEXT NOT NULL,
                    memory_type VARCHAR(50) DEFAULT 'general',  -- 'preference', 'fact', 'experience', 'pattern'
                    importance_score FLOAT DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    embedding vector(384),
                    source_conversation_id UUID REFERENCES chatbot_conversations(conversation_id)
                );
            """)
            
            # Create indexes for performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_entities_name ON memory_entities(name);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_entities_type ON memory_entities(entity_type);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_entities_user ON memory_entities(user_context);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_relations_type ON memory_relations(relation_type);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_long_term_memories_user ON long_term_memories(user_context);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_long_term_memories_type ON long_term_memories(memory_type);")
            
            print("✅ Enhanced memory tables created/verified")
            
    async def create_entity(self, entity: MemoryEntity, user_context: str) -> str:
        """Create a new memory entity"""
        async with self.pool.acquire() as conn:
            # Generate embedding for the entity
            entity_text = f"{entity.name} {entity.entity_type} " + " ".join(entity.observations)
            embedding = self.encoder.encode(entity_text).tolist()
            
            entity_id = await conn.fetchval("""
                INSERT INTO memory_entities 
                (name, entity_type, observations, confidence, metadata, embedding, user_context)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING entity_id
            """, 
            entity.name, entity.entity_type, json.dumps(entity.observations), 
            entity.confidence, json.dumps(entity.metadata), embedding, user_context)
            
            print(f"✅ Created entity: {entity.name} ({entity.entity_type})")
            return str(entity_id)
            
    async def create_relation(self, relation: MemoryRelation, user_context: str):
        """Create a relation between entities"""
        async with self.pool.acquire() as conn:
            # Get entity IDs
            from_id = await conn.fetchval(
                "SELECT entity_id FROM memory_entities WHERE name = $1 AND user_context = $2", 
                relation.from_entity, user_context
            )
            to_id = await conn.fetchval(
                "SELECT entity_id FROM memory_entities WHERE name = $1 AND user_context = $2", 
                relation.to_entity, user_context
            )
            
            if from_id and to_id:
                await conn.execute("""
                    INSERT INTO memory_relations 
                    (from_entity_id, to_entity_id, relation_type, strength, confidence, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, from_id, to_id, relation.relation_type, relation.strength, 
                relation.confidence, json.dumps(relation.metadata))
                
                print(f"✅ Created relation: {relation.from_entity} -[{relation.relation_type}]-> {relation.to_entity}")

    async def semantic_search_entities(self, query: str, user_context: str, 
                                     limit: int = 5, min_similarity: float = 0.6) -> List[Dict]:
        """Semantic search for relevant entities (Memento MCP style)"""
        async with self.pool.acquire() as conn:
            # Generate query embedding
            query_embedding = self.encoder.encode(query).tolist()
            
            results = await conn.fetch("""
                SELECT 
                    name, entity_type, observations, confidence, metadata,
                    1 - (embedding <=> $1::vector) as similarity
                FROM memory_entities 
                WHERE user_context = $2
                  AND 1 - (embedding <=> $1::vector) >= $3
                ORDER BY embedding <=> $1::vector
                LIMIT $4
            """, query_embedding, user_context, min_similarity, limit)
            
            return [dict(r) for r in results]

    async def store_long_term_memory(self, content: str, user_context: str, 
                                   memory_type: str = 'general', 
                                   importance: float = 0.5,
                                   conversation_id: str = None):
        """Store long-term memory with semantic embedding (Mem0 style)"""
        async with self.pool.acquire() as conn:
            # Register vector types for this connection
            from pgvector.asyncpg import register_vector
            await register_vector(conn)
            
            embedding = self.encoder.encode(content)  # Keep as numpy array
            
            await conn.execute("""
                INSERT INTO long_term_memories 
                (user_context, memory_content, memory_type, importance_score, embedding, source_conversation_id)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, user_context, content, memory_type, importance, embedding, conversation_id)
            
            print(f"💾 Stored long-term memory: {content[:50]}...")

    async def retrieve_long_term_memories(self, query: str, user_context: str, 
                                        limit: int = 3, min_similarity: float = 0.5) -> List[Dict]:
        """Retrieve relevant long-term memories"""
        async with self.pool.acquire() as conn:
            query_embedding = self.encoder.encode(query).tolist()
            
            results = await conn.fetch("""
                SELECT 
                    memory_content, memory_type, importance_score,
                    1 - (embedding <=> $1::vector) as similarity,
                    access_count, last_accessed
                FROM long_term_memories 
                WHERE user_context = $2
                  AND 1 - (embedding <=> $1::vector) >= $3
                ORDER BY 
                    importance_score DESC,
                    embedding <=> $1::vector,
                    access_count DESC
                LIMIT $4
            """, query_embedding, user_context, min_similarity, limit)
            
            # Update access count
            if results:
                for result in results:
                    await conn.execute("""
                        UPDATE long_term_memories 
                        SET access_count = access_count + 1, last_accessed = NOW()
                        WHERE memory_content = $1 AND user_context = $2
                    """, result['memory_content'], user_context)
            
            return [dict(r) for r in results]

    async def extract_conversation_insights(self, conversation_id: str, 
                                          user_identifier: str) -> Dict[str, Any]:
        """Extract insights from conversation using LLM (inspired by all three systems)"""
        async with self.pool.acquire() as conn:
            # Get conversation messages
            messages = await conn.fetch("""
                SELECT message_role, message_content, executed_function_name, 
                       function_input_parameters, function_output_result
                FROM chatbot_messages 
                WHERE conversation_id = $1 
                ORDER BY message_created_at ASC
            """, conversation_id)
            
            if not messages:
                return {}
                
            # Build conversation text
            conversation_text = ""
            for msg in messages:
                conversation_text += f"{msg['message_role']}: {msg['message_content']}\n"
                if msg['executed_function_name']:
                    conversation_text += f"[Function: {msg['executed_function_name']}]\n"
            
            # Use OpenAI to extract insights
            extraction_prompt = f"""
            Analyze this conversation and extract structured insights:

            {conversation_text}

            Extract:
            1. Key entities (people, products, orders, preferences)
            2. Important relationships between entities  
            3. Long-term memories worth storing
            4. Customer preferences or patterns
            5. Issues or complaints mentioned

            Return as JSON with this structure:
            {{
                "entities": [
                    {{"name": "entity_name", "type": "customer|product|order|preference", "observations": ["observation1", "observation2"]}},
                ],
                "relations": [
                    {{"from": "entity1", "to": "entity2", "type": "purchased|prefers|complained_about", "strength": 0.8}}
                ],
                "long_term_memories": [
                    {{"content": "memory content", "type": "preference|fact|experience", "importance": 0.7}}
                ],
                "summary": "Brief conversation summary"
            }}
            """
            
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # Fast and cheap
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                insights = json.loads(response.choices[0].message.content)
                print(f"🧠 Extracted insights: {len(insights.get('entities', []))} entities, {len(insights.get('long_term_memories', []))} memories")
                return insights
                
            except Exception as e:
                print(f"❌ Error extracting insights: {e}")
                return {}

    async def process_conversation_memory(self, conversation_id: str, user_identifier: str):
        """Process and store all types of memory from a conversation"""
        insights = await self.extract_conversation_insights(conversation_id, user_identifier)
        
        if not insights:
            return
            
        # Store entities
        for entity_data in insights.get('entities', []):
            entity = MemoryEntity(
                name=entity_data['name'],
                entity_type=entity_data['type'],
                observations=entity_data['observations']
            )
            await self.create_entity(entity, user_identifier)
        
        # Store relations
        for relation_data in insights.get('relations', []):
            relation = MemoryRelation(
                from_entity=relation_data['from'],
                to_entity=relation_data['to'],
                relation_type=relation_data['type'],
                strength=relation_data.get('strength', 1.0)
            )
            await self.create_relation(relation, user_identifier)
        
        # Store long-term memories
        for memory_data in insights.get('long_term_memories', []):
            await self.store_long_term_memory(
                content=memory_data['content'],
                user_context=user_identifier,
                memory_type=memory_data.get('type', 'general'),
                importance=memory_data.get('importance', 0.5),
                conversation_id=conversation_id
            )
        
        # Store conversation summary
        if insights.get('summary'):
            async with self.pool.acquire() as conn:
                embedding = self.encoder.encode(insights['summary']).tolist()
                await conn.execute("""
                    INSERT INTO conversation_summaries 
                    (conversation_id, summary_text, key_entities, embedding)
                    VALUES ($1, $2, $3, $4)
                """, conversation_id, insights['summary'], 
                json.dumps([e['name'] for e in insights.get('entities', [])]), embedding)

    async def get_conversation_context(self, query: str, user_identifier: str) -> Dict[str, Any]:
        """Get comprehensive context for a user query"""
        # Get semantic entities
        entities = await self.semantic_search_entities(query, user_identifier, limit=5)
        
        # Get long-term memories  
        memories = await self.retrieve_long_term_memories(query, user_identifier, limit=3)
        
        # Get entity relations
        relations = []
        if entities:
            async with self.pool.acquire() as conn:
                for entity in entities[:3]:  # Only for top entities
                    entity_relations = await conn.fetch("""
                        SELECT e1.name as from_name, e2.name as to_name, r.relation_type, r.strength
                        FROM memory_relations r
                        JOIN memory_entities e1 ON r.from_entity_id = e1.entity_id
                        JOIN memory_entities e2 ON r.to_entity_id = e2.entity_id
                        WHERE e1.name = $1 AND e1.user_context = $2
                        ORDER BY r.strength DESC LIMIT 3
                    """, entity['name'], user_identifier)
                    relations.extend([dict(r) for r in entity_relations])
        
        return {
            "entities": entities,
            "memories": memories,
            "relations": relations,
            "context_strength": len(entities) + len(memories)
        }

    async def cleanup_old_memories(self, days_old: int = 90, min_access_count: int = 1):
        """Cleanup old, unused memories to prevent bloat"""
        async with self.pool.acquire() as conn:
            # Delete old, rarely accessed memories
            deleted = await conn.fetchval("""
                DELETE FROM long_term_memories 
                WHERE created_at < NOW() - INTERVAL '%s days'
                  AND access_count < $1
                  AND importance_score < 0.3
                RETURNING count(*)
            """ % days_old, min_access_count)
            
            print(f"🧹 Cleaned up {deleted or 0} old memories")

    async def get_memory_stats(self, user_context: str) -> Dict[str, int]:
        """Get memory system statistics"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM memory_entities WHERE user_context = $1) as entities,
                    (SELECT COUNT(*) FROM memory_relations WHERE EXISTS(
                        SELECT 1 FROM memory_entities WHERE entity_id = from_entity_id AND user_context = $1
                    )) as relations,
                    (SELECT COUNT(*) FROM long_term_memories WHERE user_context = $1) as memories,
                    (SELECT COUNT(*) FROM conversation_summaries WHERE EXISTS(
                        SELECT 1 FROM chatbot_conversations WHERE conversation_id = conversation_summaries.conversation_id AND user_identifier = $1
                    )) as summaries
            """, user_context)
            
            return dict(stats) if stats else {}

# Global enhanced memory instance
enhanced_memory = None

async def init_enhanced_memory(db_url: str, openai_api_key: str):
    """Initialize the global enhanced memory system"""
    global enhanced_memory
    if not enhanced_memory:
        enhanced_memory = EnhancedMemorySystem(db_url, openai_api_key)
        await enhanced_memory.init_db()
        print("🧠 Global Enhanced Memory System ready!")
    return enhanced_memory
