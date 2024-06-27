from pydantic import BaseModel

class ExperimentBase(BaseModel):
    test_type: str
    description: str

class Experiment(ExperimentBase):
    id: int
    link: str

    class Config:
        from_attributes = True

class ExperimentCreate(ExperimentBase):
    pass