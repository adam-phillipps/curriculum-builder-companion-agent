from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from src.db.database import Base
from src.db.models.base import TimestampMixin, MetadataMixin
from src.config import BuilderConstants

prerequisites = Table(
    'content_prerequisites',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('learning_content.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('learning_content.id'), primary_key=True)
)

content_questions = Table(
    'content_questions',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('learning_content.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('assessment_questions.id'), primary_key=True)
)
    
question_dependencies = Table(
    'question_dependencies',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('assessment_questions.id'), primary_key=True),
    Column('dependency_id', Integer, ForeignKey('assessment_questions.id'), primary_key=True)
)

class LearningContent(Base, TimestampMixin, MetadataMixin):
    __tablename__ = "learning_content"
    id = Column(Integer, primary_key=True)
    code_title = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    content_type = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    personas = Column(JSON, nullable=False)

    learning_objectives = Column(JSON, nullable=False)
    estimated_duration = Column(Integer, nullable=False)

    sandbox_type = Column(String, nullable=False)
    aws_services = Column(JSON, nullable=True)
    technical_requirements = Column(JSON, nullable=True)

    prerequisites = relationship(
        'LearningContent',
        secondary=prerequisites,
        primaryjoin=id==prerequisites.c.content_id,
        secondaryjoin=id==prerequisites.c.prerequisite_id,
        backref='required_for'
    )

    assessment_questions = relationship(
        'AssessmentQuestion',
        secondary=content_questions,
        back_populates='related_content'
    )

    estimated_cost = Column(Float, nullable=False, default=0.0)
    cost_breakdown = Column(JSON, nullable=True)

    status = Column(String, nullable=False, default=BuilderConstants.STATES.DRAFT.name)
    review_status = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    tags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Author and source information
    author = Column(String, nullable=True)
    co_authors = Column(JSON, nullable=True)  # List of co-author names
    sources = Column(Text, nullable=True)
    artifacts = Column(Text, nullable=True)  # Links to supplementary materials
    ai_assisted = Column(String, nullable=True)  # AI tools used in creation

    pricing_estimates = relationship("PricingEstimate", back_populates="content")
    pathway_items = relationship("PathwayItem", back_populates="content")

class PricingEstimate(Base, TimestampMixin):
    __tablename__ = "pricing_estimates"
    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('learning_content.id'))
    estimate_type = Column(String, nullable=False)
    currency = Column(String, default="USD")
    
    compute_cost = Column(Float, default=0.0)
    storage_cost = Column(Float, default=0.0)
    network_cost = Column(Float, default=0.0)
    managed_services_cost = Column(Float, default=0.0)
    other_costs = Column(Float, default=0.0)

    cost_factors = Column(JSON, nullable=True)
    assumptions = Column(JSON, nullable=True)
    content = relationship("LearningContent", back_populates="pricing_estimates")

class LearningPathway(Base, TimestampMixin):
    __tablename__ = "learning_pathways"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    target_persona = Column(String, nullable=False)
    estimated_duration = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False, default=0.0)
    items = relationship("PathwayItem", back_populates="pathway")

class PathwayItem(Base, TimestampMixin):
    __tablename__ = "pathway_items"

    id = Column(Integer, primary_key=True)
    pathway_id = Column(Integer, ForeignKey('learning_pathways.id'))
    content_id = Column(Integer, ForeignKey('learning_content.id'))
    sequence = Column(Integer, nullable=False)

    pathway = relationship("LearningPathway", back_populates="items")
    content = relationship("LearningContent", back_populates="pathway_items")
    
class AssessmentQuestion(Base, TimestampMixin, MetadataMixin):
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    difficulty_tier = Column(String, nullable=False)

    options = Column(JSON, nullable=True)
    correct_answer = Column(Text, nullable=False)

    test_cases = Column(JSON, nullable=True)
    solution_template = Column(Text, nullable=True)

    knowledge_area = Column(String, nullable=False)
    subtopics = Column(JSON, nullable=True)
    personas = Column(JSON, nullable=False)
    weight = Column(Float, default=1.0)

    hints = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)

    related_content = relationship(
        'LearningContent',
        secondary=content_questions,
        back_populates='assessment_questions'
    )

    dependencies = relationship(
        'AssessmentQuestion',
        secondary=question_dependencies,
        primaryjoin=id==question_dependencies.c.question_id,
        secondaryjoin=id==question_dependencies.c.dependency_id,
        backref='dependent_questions'
    )

    validation_rules = Column(JSON, nullable=True)
    analytics = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<AssessmentQuestion(id={self.id}, tier={self.difficulty_tier}, type={self.question_type})>"
