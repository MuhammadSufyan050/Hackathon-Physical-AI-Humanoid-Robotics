import logging
import time
from typing import List, Dict, Any, Optional
from ..config.settings import config
from .entities import Query, QueryResult
from .qdrant_client import qdrant_client
from .cohere_embedder import CohereEmbedder

logger = logging.getLogger(__name__)


class QueryValidator:
    """
    Executes validation queries and collects results
    Implements the validation workflow and metrics collection
    """

    def __init__(self):
        self.embedder = CohereEmbedder()

    def validate_single_query(self, query_text: str, top_k: Optional[int] = None) -> QueryResult:
        """
        Validate a single query against Qdrant and return results
        """
        if top_k is None:
            top_k = config.top_k

        logger.info(f"Validating query: '{query_text[:50]}...' with top_k={top_k}")
        start_time = time.time()

        # Create query object
        import uuid
        query_id = f"query-{uuid.uuid4().hex[:8]}"
        query = Query(
            id=query_id,
            text=query_text,
            category=self._categorize_query(query_text)
        )

        try:
            # Generate embedding for the query
            logger.debug(f"Generating embedding for query {query_id}")
            query_embedding = self.embedder.embed_query(query_text)

            # Execute search in Qdrant
            logger.debug(f"Executing Qdrant search for query {query_id}")
            search_results = qdrant_client.search(query_embedding, top_k=top_k)

            # Format results into TextChunk objects
            from .entities import TextChunk
            retrieved_chunks = []
            similarity_scores = []

            for i, result in enumerate(search_results):
                chunk = TextChunk(
                    id=result['id'],
                    content=result['content'],
                    metadata=result['metadata']
                )
                retrieved_chunks.append(chunk)
                similarity_scores.append(result['similarity_score'])
                logger.debug(f"Retrieved chunk {i+1}: {result['id']} with score {result['similarity_score']:.3f}")

            # Calculate total time
            retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger.info(f"Query {query_id} completed in {retrieval_time:.2f}ms, retrieved {len(retrieved_chunks)} chunks")

            # Create QueryResult object
            query_result = QueryResult(
                query_id=query.id,
                retrieved_chunks=retrieved_chunks,
                similarity_scores=similarity_scores,
                retrieval_time_ms=retrieval_time,
                top_k=top_k
            )

            return query_result

        except Exception as e:
            logger.error(f"Error validating query '{query_text[:50]}...': {e}")
            raise

    def validate_batch_queries(self, queries: List[str], top_k: Optional[int] = None) -> List[QueryResult]:
        """
        Validate multiple queries and return results
        """
        results = []
        for query_text in queries:
            try:
                result = self.validate_single_query(query_text, top_k)
                results.append(result)
            except Exception as e:
                logger.error(f"Skipping query '{query_text}' due to error: {e}")
                # Continue with other queries
                continue
        return results

    def _categorize_query(self, query_text: str) -> Optional[str]:
        """
        Categorize the query based on keywords
        """
        query_lower = query_text.lower()
        if any(keyword in query_lower for keyword in ['ros', 'ros2', 'robot operating system']):
            return 'ROS2'
        elif any(keyword in query_lower for keyword in ['gazebo', 'simulation', 'physics engine']):
            return 'Gazebo'
        elif any(keyword in query_lower for keyword in ['isaac', 'sim', 'nvidia']):
            return 'Isaac'
        elif any(keyword in query_lower for keyword in ['vla', 'vision', 'language', 'action']):
            return 'VLA'
        else:
            return 'General'

    def execute_semantic_search(self, query_text: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute semantic search method that implements the core functionality for T019
        """
        query_result = self.validate_single_query(query_text, top_k)

        # Format response similar to API structure
        formatted_chunks = []
        for chunk, score in zip(query_result.retrieved_chunks, query_result.similarity_scores):
            formatted_chunks.append({
                'id': chunk.id,
                'content': chunk.content,
                'metadata': chunk.metadata,
                'similarity_score': score
            })

        return {
            'query_id': query_result.query_id,
            'original_query': query_text,
            'retrieved_chunks': formatted_chunks,
            'retrieval_time_ms': query_result.retrieval_time_ms,
            'top_k': query_result.top_k
        }

    def integrate_cohere_with_qdrant(self, query_text: str, top_k: int = 5) -> QueryResult:
        """
        Integrate Cohere embedder with Qdrant client for query execution (T021)
        """
        return self.validate_single_query(query_text, top_k=top_k)

    def validate_top_k_retrieval(self, query_text: str, top_k: int = 5) -> QueryResult:
        """
        Implement top-k retrieval functionality (T022)
        """
        return self.validate_single_query(query_text, top_k=top_k)

    def run_stability_check(self, query_text: str, runs: int = 10, top_k: int = 5) -> Dict[str, Any]:
        """
        Implement pipeline stability checks (T031)
        Execute the same query multiple times and check for consistency
        """
        import statistics
        results = []
        retrieval_times = []

        for i in range(runs):
            result = self.validate_single_query(query_text, top_k)
            results.append(result)
            retrieval_times.append(result.retrieval_time_ms)

        # Check if results are consistent (same chunks retrieved in same order)
        first_result = results[0]
        all_consistent = all(
            self._compare_query_results(first_result, result)
            for result in results[1:]
        )

        # Calculate statistics
        avg_time = statistics.mean(retrieval_times)
        time_std_dev = statistics.stdev(retrieval_times) if len(retrieval_times) > 1 else 0
        time_cv = time_std_dev / avg_time if avg_time > 0 else 0

        return {
            "query": query_text,
            "runs": runs,
            "consistent_results": all_consistent,
            "avg_retrieval_time_ms": avg_time,
            "time_std_dev": time_std_dev,
            "time_coefficient_of_variation": time_cv,
            "retrieval_times": retrieval_times
        }

    def _compare_query_results(self, result1: QueryResult, result2: QueryResult) -> bool:
        """
        Compare two query results for consistency
        """
        if len(result1.retrieved_chunks) != len(result2.retrieved_chunks):
            return False

        # Compare the chunk IDs in order (simplistic approach)
        ids1 = [chunk.id for chunk in result1.retrieved_chunks]
        ids2 = [chunk.id for chunk in result2.retrieved_chunks]

        return ids1 == ids2