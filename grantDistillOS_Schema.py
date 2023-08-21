from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Literal
from pydantic import BaseModel as BaseModel, Field
from linkml_runtime.linkml_model import Decimal

metamodel_version = "None"
version = "0.1"

class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'
    
class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = True, 
                validate_all = True, 
                underscore_attrs_are_private = True, 
                extra = 'forbid', 
                arbitrary_types_allowed = True):
    pass                    


class worktype(str, Enum):
    
    research = "research"
    curation = "curation"
    service_provision = "service provision"
    coordination = "coordination"
    infrastructure_devops = "infrastructure devops"
    implementation = "implementation"
    
    

class workdomain(str, Enum):
    
    biosciences = "biosciences"
    pysical_sciences = "pysical sciences"
    engineering = "engineering"
    mathematics = "mathematics"
    social_sciences = "social sciences"
    interdisciplinary = "interdisciplinary"
    
    

class opensciencetraits(str, Enum):
    
    data_sharing = "data sharing"
    data_storage = "data storage"
    data_preservation = "data preservation"
    metadata_standards = "metadata standards"
    metadata = "metadata"
    data_repositories = "data repositories"
    data_management_plans = "data management plans"
    data_management = "data management"
    data_curation = "data curation"
    data_citation = "data citation"
    data_reuse = "data reuse"
    metadata_schema = "metadata schema"
    data_quality = "data quality"
    data_privacy = "data privacy"
    data_security = "data security"
    data_access = "data access"
    open_access_policies = "open access policies"
    open_access = "open access"
    public_access = "public access"
    publisher_agreements = "publisher agreements"
    article_processing_charges = "article processing charges"
    open_data = "open data"
    open_source = "open source"
    data_sharing_agreement = "data sharing agreement"
    collaborative_workflow = "collaborative workflow"
    open_peer_review = "open peer review"
    peer_review = "peer review"
    reproducible_research = "reproducible research"
    data_science = "data science"
    database = "database"
    python = "python"
    workflow = "workflow"
    openness = "openness"
    research_data = "research data"
    academic_libraries = "academic libraries"
    bibliometrics = "bibliometrics"
    citizen_science = "citizen science"
    repositories = "repositories"
    
    

class grantrecord(ConfiguredBaseModel):
    
    grantid: Optional[str] = Field(None, description="""The alpha-numeric code corresponding grant-record entry in the corresponding database or grant record-keeping system.  Likely specific to the associated record-keeping system and not valid / functional outside of that system (i.e. across agencies).""")
    grantingagencyorg: Optional[str] = Field(None, description="""The top-level organization or agency which is providing / furnishing the grant.  If this information cannot be parsed from the input data source, a null value instead.""")
    grantingsubdivision: Optional[str] = Field(None, description="""The immediate sub-division, under the 'grantingAgency' organization structure, corresponding to the current grant.  If this information cannot be parsed from the input data source, a null value instead.""")
    grantvalue: Optional[int] = Field(None, description="""The monetary value of grant""")
    grantbegindate: Optional[datetime ] = Field(None, description="""The date at which the grant went or will go into effect.""")
    grantenddate: Optional[datetime ] = Field(None, description="""The date at which the grant did or will conclude.""")
    amendmentdates: Optional[List[str]] = Field(default_factory=list, description="""The dates on, for, or at which the grant was modified or ammended.""")
    grantrecipient_individual: Optional[List[str]] = Field(default_factory=list, description="""The *individual* (or enumerated persons) who is (are) the designated recipient(s) of the grant.""")
    grantrecipient_org: Optional[str] = Field(None, description="""The relevant (e.g. managing indirect costs) *organization* associated with the grantRecipient_individual.  If not explicitly designated or stated, presumably the grantRecipient_individual's primary organization or affiliation.""")
    worktype: Optional[List[worktype]] = Field(default_factory=list, description="""The type(s) of work that the grant might seek to support, elicit, or engender.  Lowercased. If it cannot be parsed or determined, then null.""")
    workdomain: Optional[List[workdomain]] = Field(default_factory=list, description="""The broad categorical / topical domain(s) of the associated grant, across, in, or with which the work is to be done. If it cannot be parsed or determined, then null.""")
    opensciencetraits: Optional[List[opensciencetraits]] = Field(default_factory=list, description="""The aspects or characteristics of the associated grant which are relevant to Public Access and/or Open-Science. If no such aspects are found, then an empty list, [].""")
    


class ExtractionResult(ConfiguredBaseModel):
    """
    A result of extracting knowledge on text
    """
    input_id: Optional[str] = Field(None)
    input_title: Optional[str] = Field(None)
    input_text: Optional[str] = Field(None)
    raw_completion_output: Optional[str] = Field(None)
    prompt: Optional[str] = Field(None)
    extracted_object: Optional[Any] = Field(None, description="""The complex objects extracted from the text""")
    named_entities: Optional[List[Any]] = Field(default_factory=list, description="""Named entities extracted from the text""")
    


class NamedEntity(ConfiguredBaseModel):
    
    id: Optional[str] = Field(None, description="""A unique identifier for the named entity""")
    label: Optional[str] = Field(None, description="""The label (name) of the named thing""")
    


class CompoundExpression(ConfiguredBaseModel):
    
    None
    


class Triple(CompoundExpression):
    """
    Abstract parent for Relation Extraction tasks
    """
    subject: Optional[str] = Field(None)
    predicate: Optional[str] = Field(None)
    object: Optional[str] = Field(None)
    qualifier: Optional[str] = Field(None, description="""A qualifier for the statements, e.g. \"NOT\" for negation""")
    subject_qualifier: Optional[str] = Field(None, description="""An optional qualifier or modifier for the subject of the statement, e.g. \"high dose\" or \"intravenously administered\"""")
    object_qualifier: Optional[str] = Field(None, description="""An optional qualifier or modifier for the object of the statement, e.g. \"severe\" or \"with additional complications\"""")
    


class TextWithTriples(ConfiguredBaseModel):
    
    publication: Optional[Publication] = Field(None)
    triples: Optional[List[Triple]] = Field(default_factory=list)
    


class RelationshipType(NamedEntity):
    
    id: str = Field(None, description="""A unique identifier for the named entity""")
    label: Optional[str] = Field(None, description="""The label (name) of the named thing""")
    


class Publication(ConfiguredBaseModel):
    
    id: Optional[str] = Field(None, description="""The publication identifier""")
    title: Optional[str] = Field(None, description="""The title of the publication""")
    abstract: Optional[str] = Field(None, description="""The abstract of the publication""")
    combined_text: Optional[str] = Field(None)
    full_text: Optional[str] = Field(None, description="""The full text of the publication""")
    


class AnnotatorResult(ConfiguredBaseModel):
    
    subject_text: Optional[str] = Field(None)
    object_id: Optional[str] = Field(None)
    object_text: Optional[str] = Field(None)
    



# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
grantrecord.update_forward_refs()
ExtractionResult.update_forward_refs()
NamedEntity.update_forward_refs()
CompoundExpression.update_forward_refs()
Triple.update_forward_refs()
TextWithTriples.update_forward_refs()
RelationshipType.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()

