"""
API module for Qdrant retrieval validation
"""
from typing import Dict, Any, List
from ..config.settings import config
from .qdrant_client import qdrant_client
from .entities import Query, TextChunk


def test_connection() -> Dict[str, Any]:
    """
    Test connection to Qdrant Cloud
    Returns connection status and response time
    """
    import time

    start_time = time.time()

    try:
        is_connected = qdrant_client.validate_connection()
        response_time_ms = (time.time() - start_time) * 1000  # Convert to milliseconds

        if is_connected:
            return {
                "success": True,
                "message": "Successfully connected to Qdrant Cloud",
                "response_time_ms": response_time_ms
            }
        else:
            return {
                "success": False,
                "error": "Failed to connect to Qdrant Cloud",
                "response_time_ms": response_time_ms
            }
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        return {
            "success": False,
            "error": str(e),
            "response_time_ms": response_time_ms
        }


def validate_query(query_text: str, top_k: int = 5, validate_embedding: bool = True) -> Dict[str, Any]:
    """
    Validate a single query against Qdrant
    Execute a query against Qdrant and return validation metrics
    """
    import time
    import uuid
    from .cohere_embedder import CohereEmbedder

    start_time = time.time()

    try:
        # Validate input
        if not query_text or len(query_text.strip()) == 0:
            return {
                "error": "Query text is required"
            }

        # Generate query ID
        query_id = f"query-{uuid.uuid4().hex[:8]}"

        # Initialize Cohere embedder
        embedder = CohereEmbedder()

        # Generate embedding for the query
        query_embedding = embedder.embed_text(query_text)

        # Execute search in Qdrant
        search_results = qdrant_client.search(query_embedding, top_k=top_k)

        # Format the results
        formatted_chunks = []
        similarity_scores = []

        for result in search_results:
            chunk = TextChunk(
                id=result['id'],
                content=result['content'],
                metadata=result['metadata']
            )
            formatted_chunks.append(chunk)
            similarity_scores.append(result['similarity_score'])

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        return {
            "query_id": query_id,
            "original_query": query_text,
            "retrieved_chunks": formatted_chunks,
            "validation_result": None,  # Will be filled by result evaluator later
            "retrieval_time_ms": response_time_ms
        }
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        return {
            "error": str(e),
            "response_time_ms": response_time_ms
        }


def execute_semantic_search(query_text: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Create semantic search endpoint (T025)
    Execute semantic search and return results with validation metrics
    """
    import time
    import uuid
    from .query_validator import QueryValidator

    start_time = time.time()

    try:
        # Validate input
        if not query_text or len(query_text.strip()) == 0:
            return {
                "error": "Query text is required"
            }

        # Generate query ID
        query_id = f"query-{uuid.uuid4().hex[:8]}"

        # Use QueryValidator to execute semantic search
        validator = QueryValidator()
        result = validator.execute_semantic_search(query_text, top_k=top_k)

        # Add query ID to the result
        result["query_id"] = query_id

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        result["retrieval_time_ms"] = response_time_ms

        return result
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        return {
            "error": str(e),
            "response_time_ms": response_time_ms
        }


def run_batch_validation(queries: List[str], top_k: int = 5) -> Dict[str, Any]:
    """
    Run batch validation for multiple queries
    Execute multiple test queries and return comprehensive validation report
    """
    import time
    import uuid
    from .result_evaluator import ResultEvaluator

    start_time = time.time()

    try:
        # Validate input
        if not queries:
            return {
                "error": "At least one query is required"
            }

        # Generate batch ID
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"

        # Use QueryValidator to process queries
        from .query_validator import QueryValidator
        validator = QueryValidator()

        # Process each query and collect QueryResult objects
        query_results = []
        detailed_results = []
        for query_text in queries:
            try:
                query_result = validator.validate_single_query(query_text, top_k=top_k)
                query_results.append(query_result)

                detailed_results.append({
                    "query": query_text,
                    "result": {
                        "query_id": query_result.query_id,
                        "retrieved_chunks": [
                            {
                                "id": chunk.id,
                                "content": chunk.content,
                                "metadata": chunk.metadata,
                                "similarity_score": score
                            }
                            for chunk, score in zip(query_result.retrieved_chunks, query_result.similarity_scores)
                        ],
                        "retrieval_time_ms": query_result.retrieval_time_ms
                    }
                })
            except Exception as e:
                # Log error but continue with other queries
                import logging
                logging.error(f"Error processing query '{query_text}': {e}")
                continue

        # Calculate overall metrics using ResultEvaluator
        evaluator = ResultEvaluator()
        overall_metrics = evaluator.calculate_validation_metrics(query_results)

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        return {
            "batch_id": batch_id,
            "total_queries": len(queries),
            "completed_queries": len(detailed_results),
            "overall_metrics": overall_metrics,
            "detailed_results": detailed_results,
            "execution_time_ms": execution_time_ms
        }
    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000
        return {
            "error": str(e),
            "execution_time_ms": execution_time_ms
        }


def run_comprehensive_batch_validation(queries: List[str], top_k: int = 5) -> Dict[str, Any]:
    """
    Implement batch validation endpoint (T036)
    Execute comprehensive validation with full reporting
    """
    import time
    import uuid
    from .result_evaluator import ResultEvaluator

    start_time = time.time()

    try:
        # Validate input
        if not queries:
            return {
                "error": "At least one query is required"
            }

        # Generate batch ID
        batch_id = f"batch-{uuid.uuid4().hex[:8]}"

        # Use ResultEvaluator to run comprehensive validation
        evaluator = ResultEvaluator()
        comprehensive_report = evaluator.run_comprehensive_validation(queries, top_k=top_k)

        # Add batch-specific information
        comprehensive_report["batch_id"] = batch_id
        comprehensive_report["total_input_queries"] = len(queries)

        return comprehensive_report
    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000
        return {
            "error": str(e),
            "execution_time_ms": execution_time_ms
        }