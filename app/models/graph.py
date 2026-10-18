from datetime import datetime
from sqlalchemy import (
    UniqueConstraint, Column, Unicode, BigInteger, Integer,
    Boolean, DateTime, ForeignKey, Table, func, event, DDL
)
from sqlalchemy.orm import relationship, DeclarativeBase

# SQLite only autocrements INTEGER (exact type) PKs.
# This type maps to INTEGER in SQLite and BIGINT in PostgreSQL.
BigIntPK = BigInteger().with_variant(Integer(), "sqlite")


class Base(DeclarativeBase):
    def dict(self, **kwargs):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


user_subscribed_tags = Table(
    'user_to_tags', Base.metadata,
    Column('user_id', BigInteger, ForeignKey('users.id'), primary_key=True,
           nullable=False, onupdate="CASCADE"),
    Column('tag_id', BigInteger, ForeignKey('tags.id'), primary_key=True,
           nullable=False, onupdate="CASCADE"),
    Column('created', DateTime(timezone=False), default=datetime.utcnow, nullable=False),
    UniqueConstraint('user_id', 'tag_id', name='user_tag_uix'),
)

question_tags = Table(
    'question_to_tags', Base.metadata,
    Column('question_id', BigInteger, ForeignKey('questions.id'), primary_key=True,
           nullable=False, onupdate="CASCADE"),
    Column('tag_id', BigInteger, ForeignKey('tags.id'), primary_key=True,
           nullable=False, onupdate="CASCADE"),
    Column('created', DateTime(timezone=False), default=datetime.utcnow, nullable=False),
    UniqueConstraint('question_id', 'tag_id', name='question_tag_uix'),
)

question_answers = Table(
    'question_to_answers', Base.metadata,
    Column('question_id', BigInteger, ForeignKey('questions.id'), primary_key=True,
           nullable=False, onupdate="CASCADE"),
    Column('answer_id', BigInteger, ForeignKey('answers.id'), primary_key=True,
           nullable=False, onupdate="CASCADE"),
    Column('created', DateTime(timezone=False), default=datetime.utcnow, nullable=False),
    UniqueConstraint('question_id', 'answer_id', name='question_answer_uix'),
)

question_questions = Table(
    'question_to_questions', Base.metadata,
    Column('question_parent_id', BigInteger, ForeignKey('questions.id'),
           primary_key=True, nullable=False, onupdate="CASCADE"),
    Column('question_child_id', BigInteger, ForeignKey('questions.id'),
           primary_key=True, nullable=False, onupdate="CASCADE"),
    Column('created', DateTime(timezone=False), default=datetime.utcnow, nullable=False),
    UniqueConstraint('question_parent_id', 'question_child_id',
                     name='question_parent_child_uix'),
)

# Prevent redundant bidirectional links (PostgreSQL only — uses least/greatest).
# SQLite (used in tests) doesn't support these functions so we use a DDL event.
event.listen(
    question_questions,
    "after_create",
    DDL(
        "CREATE UNIQUE INDEX IF NOT EXISTS question_to_questions_uix "
        "ON question_to_questions "
        "(least(question_parent_id, question_child_id), "
        " greatest(question_parent_id, question_child_id))"
    ).execute_if(dialect="postgresql"),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(BigIntPK, primary_key=True)
    name = Column(Unicode, unique=True)


class User(Base):
    __tablename__ = "users"

    id = Column(BigIntPK, primary_key=True)
    username = Column(Unicode, unique=True)
    email = Column(Unicode, unique=True)
    tags_subscriptions = relationship('Tag', secondary='user_to_tags',
                                      backref="subscribed_users")

    def dict(self, **kwargs):
        u = super().dict()
        del u['email']
        return u


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint('user_id', 'answer_id', name='user_vote_answer_uix'),)

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    answer_id = Column(Integer, ForeignKey('answers.id'), primary_key=True)
    rating = Column(Integer, default=1)
    created = Column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)
    user = relationship('User', backref="users_votes")
    answer = relationship('Answer', backref="answer_votes")


class View(Base):
    __tablename__ = "views"
    __table_args__ = (UniqueConstraint('user_id', 'question_id', name='user_view_question_uix'),)

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True, nullable=False)
    bookmark = Column(Boolean, default=False)
    user = relationship('User', backref="questions_viewed")
    question = relationship('Question', backref="viewers")


class Learn(Base):
    __tablename__ = "masteries"
    __table_args__ = (UniqueConstraint('user_id', 'question_id', name='user_knows_question_uix'),)

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True, nullable=False)
    user = relationship('User', backref="questions_learned")
    question = relationship('Question', backref="learners")


class Question(Base):
    __tablename__ = "questions"

    id = Column(BigIntPK, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(Unicode, unique=True)
    dark = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)

    tags = relationship('Tag', secondary='question_to_tags', backref='questions')
    user = relationship('User', backref="questions")
    answers = relationship('Answer', secondary='question_to_answers', backref='questions')
    children = relationship(
        'Question',
        secondary=question_questions,
        primaryjoin=(id == question_questions.c.question_parent_id),
        secondaryjoin=(id == question_questions.c.question_child_id),
        backref="parents",
    )

    def dict(self, verbose=False, minimal=False, **kwargs):
        q = super().dict()
        del q['user_id']
        q['submitter'] = self.user.username if self.user else None
        if verbose:
            q['tags'] = [t.dict() for t in self.tags]
        q['learners'] = len(self.learners)
        q['views'] = len(self.viewers)
        q['answers'] = len(self.answers) if minimal else [
            a.dict(minimal=minimal) for a in self.answers
        ]
        return q


class Answer(Base):
    __tablename__ = "answers"

    id = Column(BigIntPK, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    url = Column(Unicode, nullable=False)
    start = Column(Integer, default=None)
    stop = Column(Integer, default=None)
    dark = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)
    user = relationship("User")

    def dict(self, verbose=False, minimal=False, **kwargs):
        a = super().dict()
        a['submitter'] = self.user.username if self.user else None
        a['dependencies'] = [d.dict(minimal=minimal) for d in self.followup_questions]
        return a


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(BigIntPK, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    answer_id = Column(BigInteger, ForeignKey('answers.id'), nullable=False)
    question_id = Column(BigInteger, ForeignKey('questions.id'), nullable=False)
    start = Column(Integer, default=None)
    stop = Column(Integer, default=None)
    dark = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)

    answer = relationship('Answer', backref="followup_questions")
    question = relationship('Question', backref="unsatisfactory_answers")
    user = relationship('User')

    def dict(self, verbose=False, minimal=False, **kwargs):
        d = super().dict()
        del d['user_id']
        d['submitter'] = self.user.username if self.user else None
        d['question'] = self.question.dict(minimal=True)
        return d
