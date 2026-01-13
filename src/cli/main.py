"""CLI entry point for the Book Q&A Retrieval Agent."""

import sys
import argparse
import logging
from typing import Optional
from src.agents.book_qna_agent import BookQnaAgent
from src.config.settings import settings


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Book Q&A Retrieval Agent - Ask questions about book content"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Ask a single question and exit"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive mode (default behavior)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    return parser


def single_query_mode(agent: BookQnaAgent, query: str):
    """Handle a single query and exit."""
    try:
        logger.info(f"Processing single query: {query}")
        answer = agent.process_question(query)

        print(f"\nAnswer: {answer.content}")

        if answer.source_chunks:
            print(f"\nSources ({len(answer.source_chunks)}):")
            for i, chunk in enumerate(answer.source_chunks, 1):
                source_info = []
                if chunk.source_url:
                    source_info.append(f"URL: {chunk.source_url}")
                if chunk.page_number:
                    source_info.append(f"Page: {chunk.page_number}")
                if chunk.section_title:
                    source_info.append(f"Section: {chunk.section_title}")

                print(f"  {i}. {' | '.join(source_info) if source_info else 'Unknown source'}")
                print(f"     Relevance: {chunk.score:.2f}")
        else:
            print("\nNo sources found - answer may not be based on book content.")

        print(f"\nConfidence: {answer.confidence:.2f}")

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def interactive_mode(agent: BookQnaAgent):
    """Run the agent in interactive mode."""
    print("Welcome to the Book Q&A Agent!")
    print("Ask your questions about the book content (type 'quit' or 'exit' to exit):\n")

    while True:
        try:
            user_input = input("Your question: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                print("Please enter a question.\n")
                continue

            answer = agent.process_question(user_input)

            print(f"\nAnswer: {answer.content}")

            if answer.source_chunks:
                print(f"\nSources ({len(answer.source_chunks)}):")
                for i, chunk in enumerate(answer.source_chunks, 1):
                    source_info = []
                    if chunk.source_url:
                        source_info.append(f"URL: {chunk.source_url}")
                    if chunk.page_number:
                        source_info.append(f"Page: {chunk.page_number}")
                    if chunk.section_title:
                        source_info.append(f"Section: {chunk.section_title}")

                    print(f"  {i}. {' | '.join(source_info) if source_info else 'Unknown source'}")
                    print(f"     Relevance: {chunk.score:.2f}")
            else:
                print("\nNo relevant content found in the book.")

            print(f"\nConfidence: {answer.confidence:.2f}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error in interactive mode: {str(e)}")
            print(f"Error: {str(e)}\n")


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate settings before proceeding
    try:
        from src.config.settings import validate_settings
        validate_settings()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Initialize the agent
    try:
        agent = BookQnaAgent()

        # Initialize assistant
        assistant_id = agent.initialize_assistant()
        logger.info(f"Assistant initialized with ID: {assistant_id}")

        # Check connectivity
        connection_status = agent.check_connection()
        if not all(connection_status.values()):
            logger.warning(f"Connection issues: {connection_status}")
            print("Warning: Some services may have connection issues:")
            for service, connected in connection_status.items():
                if not connected:
                    print(f"  - {service}: NOT CONNECTED")
            print()

    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        print(f"Error initializing agent: {str(e)}")
        sys.exit(1)

    # Run in appropriate mode
    try:
        if args.query:
            # Single query mode
            single_query_mode(agent, args.query)
        else:
            # Interactive mode (default)
            interactive_mode(agent)
    except Exception as e:
        logger.error(f"Runtime error: {str(e)}")
        print(f"Runtime error: {str(e)}")
        sys.exit(1)
    finally:
        # Clean up
        agent.close()


if __name__ == "__main__":
    main()