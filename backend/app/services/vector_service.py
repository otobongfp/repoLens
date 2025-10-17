# RepoLens Vector Store Service
# Embedding management and similarity search

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid
import numpy as np
from dataclasses import dataclass

try:
    import openai
    from openai import OpenAI
except ImportError:
    raise ImportError("openai not installed. Run: pip install openai")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    raise ImportError("psycopg2 not installed. Run: pip install psycopg2-binary")

logger = logging.getLogger(__name__)


@dataclass
class Embedding:
    """Embedding representation"""

    embedding_id: str
    content: str
    content_hash: str
    embedding_vector: List[float]
    metadata: Dict[str, Any]
    created_at: datetime


@dataclass
class SimilarityResult:
    """Similarity search result"""

    embedding_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]


class OpenAIEmbeddingService:
    """OpenAI embedding service"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = 1536  # OpenAI text-embedding-3-small dimensions

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        try:
            response = self.client.embeddings.create(
                model=self.model, input=text, dimensions=self.dimensions
            )
            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        try:
            response = self.client.embeddings.create(
                model=self.model, input=texts, dimensions=self.dimensions
            )
            return [data.embedding for data in response.data]

        except Exception as e:
            logger.error(f"Failed to create batch embeddings: {e}")
            raise


class PgVectorStore:
    """PostgreSQL with pgvector extension for vector storage"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.dimensions = 1536
        self._create_tables()

    def _create_tables(self):
        """Create vector tables"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS embeddings (
            embedding_id VARCHAR(255) PRIMARY KEY,
            content TEXT NOT NULL,
            content_hash VARCHAR(64) NOT NULL,
            embedding VECTOR(1536) NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS embeddings_content_hash_idx 
        ON embeddings(content_hash);
        
        CREATE INDEX IF NOT EXISTS embeddings_metadata_idx 
        ON embeddings USING GIN(metadata);
        
        CREATE INDEX IF NOT EXISTS embeddings_vector_idx 
        ON embeddings USING ivfflat (embedding vector_cosine_ops);
        """

        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_sql)
                    conn.commit()
            logger.info("Created vector tables and indexes")

        except Exception as e:
            logger.error(f"Failed to create vector tables: {e}")
            raise

    def store_embedding(self, embedding: Embedding) -> bool:
        """Store embedding in database"""
        sql = """
        INSERT INTO embeddings (embedding_id, content, content_hash, embedding, metadata, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (embedding_id) DO UPDATE SET
            content = EXCLUDED.content,
            content_hash = EXCLUDED.content_hash,
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        """

        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        sql,
                        (
                            embedding.embedding_id,
                            embedding.content,
                            embedding.content_hash,
                            embedding.embedding_vector,
                            json.dumps(embedding.metadata),
                            embedding.created_at,
                        ),
                    )
                    conn.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            return False

    def store_embeddings_batch(self, embeddings: List[Embedding]) -> int:
        """Store multiple embeddings"""
        sql = """
        INSERT INTO embeddings (embedding_id, content, content_hash, embedding, metadata, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (embedding_id) DO UPDATE SET
            content = EXCLUDED.content,
            content_hash = EXCLUDED.content_hash,
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata,
            updated_at = NOW()
        """

        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.executemany(
                        sql,
                        [
                            (
                                emb.embedding_id,
                                emb.content,
                                emb.content_hash,
                                emb.embedding_vector,
                                json.dumps(emb.metadata),
                                emb.created_at,
                            )
                            for emb in embeddings
                        ],
                    )
                    conn.commit()
            return len(embeddings)

        except Exception as e:
            logger.error(f"Failed to store batch embeddings: {e}")
            return 0

    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SimilarityResult]:
        """Search for similar embeddings"""
        base_sql = """
        SELECT embedding_id, content, metadata, 
               1 - (embedding <=> %s) as similarity_score
        FROM embeddings
        """

        params = [query_vector]

        if metadata_filter:
            where_conditions = []
            for key, value in metadata_filter.items():
                where_conditions.append(f"metadata->>%s = %s")
                params.extend([key, value])

            if where_conditions:
                base_sql += " WHERE " + " AND ".join(where_conditions)

        base_sql += " ORDER BY embedding <=> %s LIMIT %s"
        params.extend([query_vector, limit])

        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(base_sql, params)
                    results = cur.fetchall()

                    return [
                        SimilarityResult(
                            embedding_id=row["embedding_id"],
                            content=row["content"],
                            similarity_score=float(row["similarity_score"]),
                            metadata=row["metadata"],
                        )
                        for row in results
                    ]

        except Exception as e:
            logger.error(f"Failed to search similar embeddings: {e}")
            return []

    def get_embedding(self, embedding_id: str) -> Optional[Embedding]:
        """Get embedding by ID"""
        sql = """
        SELECT embedding_id, content, content_hash, embedding, metadata, created_at
        FROM embeddings
        WHERE embedding_id = %s
        """

        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(sql, (embedding_id,))
                    row = cur.fetchone()

                    if row:
                        return Embedding(
                            embedding_id=row["embedding_id"],
                            content=row["content"],
                            content_hash=row["content_hash"],
                            embedding_vector=row["embedding"],
                            metadata=row["metadata"],
                            created_at=row["created_at"],
                        )
                    return None

        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return None

    def delete_embedding(self, embedding_id: str) -> bool:
        """Delete embedding"""
        sql = "DELETE FROM embeddings WHERE embedding_id = %s"

        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, (embedding_id,))
                    conn.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to delete embedding: {e}")
            return False


class VectorService:
    """High-level vector service orchestrating embeddings and storage"""

    def __init__(self, openai_api_key: str, pgvector_url: str):
        self.embedding_service = OpenAIEmbeddingService(openai_api_key)
        self.vector_store = PgVectorStore(pgvector_url)

    def create_function_embedding(self, function_data: Dict[str, Any]) -> str:
        """Create embedding for function"""
        # Create embedding content
        content_parts = [
            f"Function: {function_data['name']}",
            f"Signature: {function_data['signature']}",
            f"File: {function_data['file_path']}",
        ]

        if function_data.get("docstring"):
            content_parts.append(f"Documentation: {function_data['docstring']}")

        if function_data.get("code_snippet"):
            content_parts.append(f"Code: {function_data['code_snippet'][:500]}")

        content = "\n".join(content_parts)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Check if embedding already exists
        existing = self.vector_store.get_embedding_by_hash(content_hash)
        if existing:
            return existing.embedding_id

        # Create new embedding
        embedding_vector = self.embedding_service.create_embedding(content)
        embedding_id = str(uuid.uuid4())

        embedding = Embedding(
            embedding_id=embedding_id,
            content=content,
            content_hash=content_hash,
            embedding_vector=embedding_vector,
            metadata={
                "function_id": function_data["function_id"],
                "tenant_id": function_data["tenant_id"],
                "repo_id": function_data["repo_id"],
                "file_path": function_data["file_path"],
                "function_name": function_data["name"],
                "language": function_data.get("language", "unknown"),
                "complexity_score": function_data.get("complexity_score", 0),
            },
            created_at=datetime.now(timezone.utc),
        )

        if self.vector_store.store_embedding(embedding):
            return embedding_id
        else:
            raise Exception("Failed to store embedding")

    def create_requirement_embedding(self, requirement_data: Dict[str, Any]) -> str:
        """Create embedding for requirement"""
        content = f"{requirement_data['title']}\n{requirement_data['text']}"
        if requirement_data.get("acceptance_criteria"):
            content += f"\nAcceptance Criteria: {', '.join(requirement_data['acceptance_criteria'])}"

        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Check if embedding already exists
        existing = self.vector_store.get_embedding_by_hash(content_hash)
        if existing:
            return existing.embedding_id

        # Create new embedding
        embedding_vector = self.embedding_service.create_embedding(content)
        embedding_id = str(uuid.uuid4())

        embedding = Embedding(
            embedding_id=embedding_id,
            content=content,
            content_hash=content_hash,
            embedding_vector=embedding_vector,
            metadata={
                "req_id": requirement_data["req_id"],
                "tenant_id": requirement_data["tenant_id"],
                "repo_id": requirement_data.get("repo_id"),
                "priority": requirement_data.get("priority", "unknown"),
                "source": requirement_data.get("source", "unknown"),
            },
            created_at=datetime.now(timezone.utc),
        )

        if self.vector_store.store_embedding(embedding):
            return embedding_id
        else:
            raise Exception("Failed to store requirement embedding")

    def search_similar_functions(
        self, query_text: str, tenant_id: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar functions"""
        # Create query embedding
        query_vector = self.embedding_service.create_embedding(query_text)

        # Search with tenant filter
        results = self.vector_store.search_similar(
            query_vector=query_vector,
            limit=top_k,
            metadata_filter={"tenant_id": tenant_id},
        )

        # Convert to function format
        function_results = []
        for result in results:
            if result.metadata.get("function_id"):
                function_results.append(
                    {
                        "function_id": result.metadata["function_id"],
                        "similarity_score": result.similarity_score,
                        "path": result.metadata.get("file_path", ""),
                        "signature": f"{result.metadata.get('function_name', '')}()",
                        "language": result.metadata.get("language", "unknown"),
                        "complexity_score": result.metadata.get("complexity_score", 0),
                        "same_repo": True,  # All results are from same tenant
                        "has_tests": False,  # TODO: Implement test detection
                        "call_graph_context": [],  # TODO: Implement call graph context
                    }
                )

        return function_results

    def search_similar_requirements(
        self, query_text: str, tenant_id: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar requirements"""
        query_vector = self.embedding_service.create_embedding(query_text)

        results = self.vector_store.search_similar(
            query_vector=query_vector,
            limit=top_k,
            metadata_filter={"tenant_id": tenant_id},
        )

        requirement_results = []
        for result in results:
            if result.metadata.get("req_id"):
                requirement_results.append(
                    {
                        "req_id": result.metadata["req_id"],
                        "similarity_score": result.similarity_score,
                        "title": result.content.split("\n")[0],
                        "text": result.content,
                        "priority": result.metadata.get("priority", "unknown"),
                        "source": result.metadata.get("source", "unknown"),
                    }
                )

        return requirement_results

    def batch_create_embeddings(
        self, items: List[Dict[str, Any]], item_type: str
    ) -> List[str]:
        """Batch create embeddings for multiple items"""
        embedding_ids = []

        # Prepare content for batch processing
        contents = []
        for item in items:
            if item_type == "function":
                content_parts = [
                    f"Function: {item['name']}",
                    f"Signature: {item['signature']}",
                    f"File: {item['file_path']}",
                ]
                if item.get("docstring"):
                    content_parts.append(f"Documentation: {item['docstring']}")
                contents.append("\n".join(content_parts))
            elif item_type == "requirement":
                content = f"{item['title']}\n{item['text']}"
                if item.get("acceptance_criteria"):
                    content += f"\nAcceptance Criteria: {', '.join(item['acceptance_criteria'])}"
                contents.append(content)

        # Create batch embeddings
        embedding_vectors = self.embedding_service.create_embeddings_batch(contents)

        # Store embeddings
        embeddings = []
        for i, (item, content, vector) in enumerate(
            zip(items, contents, embedding_vectors)
        ):
            embedding_id = str(uuid.uuid4())
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            metadata = {
                "tenant_id": item["tenant_id"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            if item_type == "function":
                metadata.update(
                    {
                        "function_id": item["function_id"],
                        "repo_id": item["repo_id"],
                        "file_path": item["file_path"],
                        "function_name": item["name"],
                        "language": item.get("language", "unknown"),
                        "complexity_score": item.get("complexity_score", 0),
                    }
                )
            elif item_type == "requirement":
                metadata.update(
                    {
                        "req_id": item["req_id"],
                        "repo_id": item.get("repo_id"),
                        "priority": item.get("priority", "unknown"),
                        "source": item.get("source", "unknown"),
                    }
                )

            embedding = Embedding(
                embedding_id=embedding_id,
                content=content,
                content_hash=content_hash,
                embedding_vector=vector,
                metadata=metadata,
                created_at=datetime.now(timezone.utc),
            )

            embeddings.append(embedding)
            embedding_ids.append(embedding_id)

        # Store all embeddings
        stored_count = self.vector_store.store_embeddings_batch(embeddings)

        if stored_count != len(embeddings):
            logger.warning(f"Only stored {stored_count}/{len(embeddings)} embeddings")

        return embedding_ids

    def get_embedding_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get embedding statistics for tenant"""
        sql = """
        SELECT 
            COUNT(*) as total_embeddings,
            COUNT(CASE WHEN metadata->>'function_id' IS NOT NULL THEN 1 END) as function_embeddings,
            COUNT(CASE WHEN metadata->>'req_id' IS NOT NULL THEN 1 END) as requirement_embeddings,
            AVG(array_length(embedding, 1)) as avg_dimensions
        FROM embeddings
        WHERE metadata->>'tenant_id' = %s
        """

        try:
            with psycopg2.connect(self.vector_store.connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(sql, (tenant_id,))
                    result = cur.fetchone()

                    return {
                        "total_embeddings": result["total_embeddings"],
                        "function_embeddings": result["function_embeddings"],
                        "requirement_embeddings": result["requirement_embeddings"],
                        "avg_dimensions": (
                            float(result["avg_dimensions"])
                            if result["avg_dimensions"]
                            else 0
                        ),
                    }

        except Exception as e:
            logger.error(f"Failed to get embedding stats: {e}")
            return {
                "total_embeddings": 0,
                "function_embeddings": 0,
                "requirement_embeddings": 0,
                "avg_dimensions": 0,
            }


if __name__ == "__main__":
    # Test vector service
    vector_service = VectorService(
        openai_api_key=os.getenv("OPENAI_API_KEY", "test-key"),
        pgvector_url=os.getenv(
            "PGVECTOR_DB_URL", "postgresql://user:pass@localhost/vectordb"
        ),
    )

    # Test function embedding
    test_function = {
        "function_id": "func_123",
        "tenant_id": "tenant_123",
        "repo_id": "repo_123",
        "name": "authenticate_user",
        "signature": "def authenticate_user(username: str, password: str) -> bool:",
        "file_path": "src/auth.py",
        "docstring": "Authenticate user with username and password",
        "language": "python",
        "complexity_score": 3,
    }

    embedding_id = vector_service.create_function_embedding(test_function)
    print(f"Created function embedding: {embedding_id}")

    # Test similarity search
    results = vector_service.search_similar_functions(
        "user authentication", "tenant_123", top_k=5
    )
    print(f"Found {len(results)} similar functions")
    for result in results:
        print(f"  - {result['signature']}: {result['similarity_score']:.3f}")
