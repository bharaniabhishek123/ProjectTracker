import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from backend.config import get_settings

settings = get_settings()


class VectorStore:
    """ChromaDB vector store for semantic search."""

    def __init__(self):
        """Initialize ChromaDB client."""
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection for status updates
        self.collection = self.client.get_or_create_collection(
            name="status_updates",
            metadata={"hnsw:space": "cosine"}
        )

    def add_status_update(
        self,
        status_id: int,
        text: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add a status update to the vector store.

        Args:
            status_id: Unique ID of the status update
            text: Status update text content
            metadata: Additional metadata (team_member_id, date, etc.)
        """
        self.collection.add(
            ids=[str(status_id)],
            documents=[text],
            metadatas=[metadata]
        )

    def search_similar(
        self,
        query: str,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar status updates using semantic search.

        Args:
            query: Search query text
            n_results: Number of results to return

        Returns:
            List of matching status updates with metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids']) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': int(results['ids'][0][i]),
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

        return formatted_results

    def delete_status_update(self, status_id: int) -> None:
        """
        Delete a status update from the vector store.

        Args:
            status_id: ID of the status update to delete
        """
        try:
            self.collection.delete(ids=[str(status_id)])
        except Exception as e:
            print(f"Error deleting status update {status_id}: {e}")

    def update_status_update(
        self,
        status_id: int,
        text: str,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update a status update in the vector store.

        Args:
            status_id: ID of the status update
            text: Updated text content
            metadata: Updated metadata
        """
        self.collection.update(
            ids=[str(status_id)],
            documents=[text],
            metadatas=[metadata]
        )

    def get_collection_count(self) -> int:
        """Get the total number of items in the collection."""
        return self.collection.count()


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
