import uuid
from sqlalchemy.exc import SQLAlchemyError
from database.models import (
    SessionLocal,
    User,
    Document,
    DocumentChunk,
    ChatSession,
    ChatMessage,
)

def seed_database():
    session = SessionLocal()
    try:
        # Seed Users
        user1 = User(
            id=str(uuid.uuid4()),
            email="user1@example.com",
            hashed_password="hashed_password_1",
            created_at=None,
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="user2@example.com",
            hashed_password="hashed_password_2",
            created_at=None,
        )
        user3 = User(
            id=str(uuid.uuid4()),
            email="user3@example.com",
            hashed_password="hashed_password_3",
            created_at=None,
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # Seed Documents
        document1 = Document(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            filename="document1.txt",
            file_path="/path/to/document1.txt",
            file_size=1024,
            status="processed",
            uploaded_at=None,
            processed_at=None,
        )
        document2 = Document(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            filename="document2.txt",
            file_path="/path/to/document2.txt",
            file_size=2048,
            status="uploaded",
            uploaded_at=None,
            processed_at=None,
        )
        document3 = Document(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            filename="document3.txt",
            file_path="/path/to/document3.txt",
            file_size=4096,
            status="failed",
            uploaded_at=None,
            processed_at=None,
        )
        session.add_all([document1, document2, document3])
        session.commit()

        # Seed DocumentChunks
        chunk1 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=0,
            content="This is the first chunk of document1.",
            embedding=[0.1] * 1536,
            metadata=None,
            created_at=None,
        )
        chunk2 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document1.id,
            chunk_index=1,
            content="This is the second chunk of document1.",
            embedding=[0.2] * 1536,
            metadata=None,
            created_at=None,
        )
        chunk3 = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=document2.id,
            chunk_index=0,
            content="This is the first chunk of document2.",
            embedding=[0.3] * 1536,
            metadata=None,
            created_at=None,
        )
        session.add_all([chunk1, chunk2, chunk3])
        session.commit()

        # Seed ChatSessions
        session1 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            document_id=document1.id,
            title="Session 1",
            created_at=None,
            updated_at=None,
        )
        session2 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            document_id=document2.id,
            title="Session 2",
            created_at=None,
            updated_at=None,
        )
        session3 = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user3.id,
            document_id=document3.id,
            title="Session 3",
            created_at=None,
            updated_at=None,
        )
        session.add_all([session1, session2, session3])
        session.commit()

        # Seed ChatMessages
        message1 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session1.id,
            role="user",
            content="What is the content of document1?",
            chunk_ids=None,
            created_at=None,
        )
        message2 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session1.id,
            role="assistant",
            content="The content of document1 is...",
            chunk_ids=None,
            created_at=None,
        )
        message3 = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session2.id,
            role="user",
            content="Can you summarize document2?",
            chunk_ids=None,
            created_at=None,
        )
        session.add_all([message1, message2, message3])
        session.commit()

        print("Database seeded successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()