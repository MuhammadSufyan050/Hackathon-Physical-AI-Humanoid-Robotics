#!/usr/bin/env python3
"""
Main validation script for Qdrant retrieval pipeline validation
Provides CLI options for various validation tasks
"""
import argparse
import sys
import json
import logging
from typing import List
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rag_validation.qdrant_client import qdrant_client
from rag_validation.api import test_connection, execute_semantic_search, run_comprehensive_batch_validation
from rag_validation.test_queries import PREDEFINED_QUERIES
from config.settings import config


def setup_logging(verbose: bool = False):
    """Set up logging based on verbosity level"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_connection(args):
    """Validate Qdrant connection"""
    print("Testing Qdrant Cloud connection...")
    try:
        result = test_connection()
        if result.get("success"):
            print(f"✅ {result['message']}")
            print(f"Response time: {result['response_time_ms']:.2f}ms")
            return 0
        else:
            print(f"❌ {result.get('error', 'Unknown error')}")
            print(f"Response time: {result['response_time_ms']:.2f}ms")
            return 1
    except Exception as e:
        print(f"❌ Error during connection test: {e}")
        return 1
    finally:
        qdrant_client.close()


def run_sample_query(args):
    """Run a sample query validation"""
    print(f"Running sample query: '{args.query_text}'")
    try:
        result = execute_semantic_search(args.query_text, top_k=args.top_k)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return 1

        print(f"Query ID: {result['query_id']}")
        print(f"Original query: {result['original_query']}")
        print(f"Retrieved {len(result['retrieved_chunks'])} chunks in {result['retrieval_time_ms']:.2f}ms")

        print("\nTop results:")
        for i, chunk in enumerate(result['retrieved_chunks'][:args.top_k], 1):
            print(f"  {i}. Score: {chunk['similarity_score']:.3f}")
            print(f"     Content: {chunk['content'][:100]}...")
            print(f"     URL: {chunk['metadata'].get('url', 'N/A')}")
            print()

        return 0
    except Exception as e:
        print(f"❌ Error during query validation: {e}")
        return 1
    finally:
        qdrant_client.close()


def run_all_tests(args):
    """Run all validation tests"""
    print("Running comprehensive validation tests...")

    try:
        # Use predefined queries or custom ones if provided
        queries = args.queries if args.queries else PREDEFINED_QUERIES[:5]  # Use first 5 predefined queries

        print(f"Validating with {len(queries)} queries...")
        result = run_comprehensive_batch_validation(queries, top_k=args.top_k)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return 1

        print(f"Validation completed for {result['total_queries']} queries")
        print(f"Total execution time: {result['total_execution_time_ms']:.2f}ms")

        # Print summary
        summary = result.get('validation_summary', {})
        print("\nValidation Summary:")
        print(f"  - Metadata accuracy passed: {summary.get('metadata_accuracy_pass', 'N/A')}")
        print(f"  - Semantic alignment passed: {summary.get('semantic_alignment_pass', 'N/A')}")
        print(f"  - Query time passed: {summary.get('query_time_pass', 'N/A')}")
        print(f"  - Pipeline stability: {summary.get('pipeline_stability', 'N/A')}")

        # Print overall metrics
        metrics = result.get('overall_metrics', {})
        print(f"\nOverall Metrics:")
        print(f"  - Average query time: {metrics.get('avg_query_time_ms', 'N/A'):.2f}ms")
        print(f"  - Average semantic alignment: {metrics.get('avg_semantic_alignment', 'N/A'):.3f}")
        print(f"  - Metadata accuracy rate: {metrics.get('metadata_accuracy_rate', 'N/A'):.3f}")

        return 0
    except Exception as e:
        print(f"❌ Error during comprehensive validation: {e}")
        return 1
    finally:
        qdrant_client.close()


def generate_report(args):
    """Generate validation report"""
    print("Generating validation report...")

    try:
        # For now, just run the comprehensive validation which includes reporting
        queries = PREDEFINED_QUERIES[:3]  # Use fewer queries for report generation
        result = run_comprehensive_batch_validation(queries, top_k=args.top_k)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return 1

        # Save report to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"Report saved to {args.output}")
        else:
            print("Validation Report:")
            print(json.dumps(result, indent=2, default=str))

        return 0
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return 1
    finally:
        qdrant_client.close()


def verify_config(args):
    """Verify configuration settings"""
    print("Verifying configuration...")

    # Print relevant config values (without sensitive information)
    print(f"Qdrant collection: {config.qdrant_collection}")
    print(f"Top-K: {config.top_k}")
    print(f"Validation threshold: {config.validation_threshold}")
    print(f"Cohere model: {config.cohere_model}")

    # Check if required environment variables are set
    required_vars = ['QDRANT_HOST', 'QDRANT_API_KEY', 'COHERE_API_KEY']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return 1
    else:
        print("✅ All required configuration variables are set")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Qdrant Retrieval Pipeline Validation Tool")

    # Global arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Connection test command
    conn_parser = subparsers.add_parser('test-connection', help='Test connection to Qdrant Cloud')
    conn_parser.set_defaults(func=validate_connection)

    # Sample query command
    query_parser = subparsers.add_parser('sample-query', help='Run a sample query validation')
    query_parser.add_argument('query_text', nargs='?', default='What is ROS2?',
                             help='Query text to validate (default: "What is ROS2?")')
    query_parser.add_argument('--top-k', type=int, default=5, help='Number of results to retrieve (default: 5)')
    query_parser.set_defaults(func=run_sample_query)

    # Run all tests command
    tests_parser = subparsers.add_parser('run-all-tests', help='Run comprehensive validation tests')
    tests_parser.add_argument('--top-k', type=int, default=5, help='Number of results to retrieve (default: 5)')
    tests_parser.add_argument('queries', nargs='*', help='Optional custom queries to test')
    tests_parser.set_defaults(func=run_all_tests)

    # Generate report command
    report_parser = subparsers.add_parser('generate-report', help='Generate validation report')
    report_parser.add_argument('--top-k', type=int, default=5, help='Number of results to retrieve (default: 5)')
    report_parser.add_argument('--output', '-o', help='Output file for the report')
    report_parser.set_defaults(func=generate_report)

    # Verify config command
    config_parser = subparsers.add_parser('verify-config', help='Verify configuration settings')
    config_parser.set_defaults(func=verify_config)

    # Parse arguments
    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)

    # If no command is specified, show help
    if not hasattr(args, 'func'):
        parser.print_help()
        return 0

    # Run the appropriate function
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())