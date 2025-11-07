import ollama
from typing import List, Dict, Any
from backend.config import get_settings

settings = get_settings()


class LLMService:
    """Service for interacting with Ollama LLM."""

    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.client = ollama.Client(host=self.base_url)

    def generate_summary(self, status_updates: List[Dict[str, Any]]) -> str:
        """
        Generate a summary from multiple status updates.

        Args:
            status_updates: List of status update dictionaries with text and metadata

        Returns:
            Generated summary text
        """
        if not status_updates:
            return "No status updates found for the specified period."

        # Build context from status updates
        context = self._build_context(status_updates)

        # Create prompt
        prompt = f"""You are an AI assistant helping to summarize team progress.
Below are status updates from team members. Please provide a concise summary of what was accomplished, organized by key themes or projects.

Status Updates:
{context}

Please provide a well-organized summary that highlights:
1. Key accomplishments
2. Main projects or themes
3. Any notable progress or milestones

Keep the summary clear, concise, and professional."""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def generate_weekly_summary(
        self,
        status_updates: List[Dict[str, Any]],
        team_member_name: str = None
    ) -> str:
        """
        Generate a weekly summary from status updates.

        Args:
            status_updates: List of status updates for the week
            team_member_name: Optional team member name to focus on

        Returns:
            Generated weekly summary
        """
        if not status_updates:
            return "No status updates found for this week."

        context = self._build_context(status_updates)

        team_filter = f" for {team_member_name}" if team_member_name else ""
        prompt = f"""You are an AI assistant creating a weekly progress report{team_filter}.

Status Updates from this week:
{context}

Please create a professional weekly summary that includes:
1. Overview of the week's activities
2. Key accomplishments and deliverables
3. Main focus areas or projects
4. Any blockers or challenges mentioned

Format the summary in a clear, structured manner suitable for management review."""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            return f"Error generating weekly summary: {str(e)}"

    def answer_query(self, query: str, relevant_updates: List[Dict[str, Any]]) -> str:
        """
        Answer a natural language query using relevant status updates.

        Args:
            query: User's question
            relevant_updates: Relevant status updates from semantic search

        Returns:
            Generated answer
        """
        if not relevant_updates:
            return "I couldn't find any relevant information to answer your question."

        context = self._build_context(relevant_updates)

        prompt = f"""You are an AI assistant helping to answer questions about team activities and progress.

User Question: {query}

Relevant Status Updates:
{context}

Based on the status updates above, please provide a clear and accurate answer to the user's question.
If the information is not sufficient to fully answer the question, please state what information is available and what is missing."""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def _build_context(self, status_updates: List[Dict[str, Any]]) -> str:
        """
        Build context string from status updates.

        Args:
            status_updates: List of status update dictionaries

        Returns:
            Formatted context string
        """
        context_parts = []
        for i, update in enumerate(status_updates, 1):
            text = update.get('status_text') or update.get('text', '')
            member = update.get('team_member', {})
            member_name = member.get('name', update.get('metadata', {}).get('team_member_name', 'Unknown'))
            date = update.get('date') or update.get('metadata', {}).get('date', 'Unknown date')

            context_parts.append(
                f"{i}. [{member_name}] on {date}:\n   {text}\n"
            )

        return "\n".join(context_parts)

    def check_connection(self) -> bool:
        """
        Check if Ollama service is available.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.client.list()
            return True
        except Exception:
            return False


# Global instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
