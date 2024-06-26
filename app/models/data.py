from pydantic import BaseModel

class ResonantColumn(BaseModel):
    G: list
    shear_strain: list

