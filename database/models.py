import os
import uuid
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    JSON,
    ARRAY,
    text,
    Index,
)
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase
from pgvector.sqlalchemy import Vector

DATABASE_URL_ENV = "DATABASE_URL"
DATABASE_URL = os.environ.get(DATABASE_URL_ENV)

if not DATABASE_URL:
    raise ValueError(f"Environment variable {DATABASE_URL_ENV} is not set.")

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

    documents = relationship("Document", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    uploaded_at = Column(TIMESTAMP, server_default=text("now()"))
    processed_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="documents")
    document_chunks = relationship("DocumentChunk", back_populates="document")
    chat_sessions = relationship("ChatSession", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

    document = relationship("Document", back_populates="document_chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, chunk_index={self.chunk_index})>"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"))

    user = relationship("User", back_populates="chat_sessions")
    document = relationship("Document", back_populates="chat_sessions")
    chat_messages = relationship("ChatMessage", back_populates="session")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, title={self.title})>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    chunk_ids = Column(ARRAY(String), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

    session = relationship("ChatSession", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role})>"


# Index definitions
Index("ix_documents_user_id", Document.user_id)
Index("ix_document_chunks_document_id", DocumentChunk.document_id)
Index("ix_chat_sessions_user_id", ChatSession.user_id)
Index("ix_chat_sessions_document_id", ChatSession.document_id)
Index("ix_chat_messages_session_id", ChatMessage.session_id)