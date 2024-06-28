from pydantic import BaseModel, Field

class ExperimentBase(BaseModel):
    test_type: str = Field(..., max_length=100)
    laboratory_number: str = Field(..., max_length=100)
    object_number: str = Field(..., max_length=50)
    description: str = Field(..., max_length=1000)

class Experiment(ExperimentBase):
    id: int
    link: str = Field(..., max_length=200)

    class Config:
        from_attributes = True

class ExperimentCreate(ExperimentBase):
    pass