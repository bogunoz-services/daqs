from pydantic import BaseModel, Field, field_validator

ALLOWED_FILTERS = {"time", "device", "device_ids", "t1", "t2", "voltage"}


class ListMeasurementsRequest(BaseModel):
    filters: list[dict] = Field(default_factory=list)
    page_index: int = Field(default=0, ge=0)
    page_size: int = Field(default=20, gt=0, le=50)

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, filters: list[dict]):
        for f in filters:
            filter_id = f.get("id")
            if filter_id not in ALLOWED_FILTERS:
                raise ValueError(f"Unsupported filter: {filter_id}")
        return filters