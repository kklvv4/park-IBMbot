"""
Pydantic response models for the FastAPI backend.
"""

from typing import Optional, List
from pydantic import BaseModel


class ParkingLocation(BaseModel):
    id: int
    name: str
    operator: Optional[str] = None
    type: Optional[str] = None
    parking_class: Optional[str] = "normal"
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rate_per_hour: Optional[float] = None
    motorcycle_rate: Optional[float] = None
    valet_rate: Optional[float] = None
    first_hour_rate: Optional[float] = None
    first_hour_free: Optional[str] = "NO"
    daily_max_cap: Optional[float] = None
    overnight_rate: Optional[float] = None
    operating_hours: Optional[str] = None
    payment_method: Optional[str] = None
    is_online_bookable: Optional[str] = "NO"
    booking_platform: Optional[str] = None
    total_bays: Optional[int] = None
    ev_charging: Optional[str] = "NO"
    disabled_bays: Optional[str] = "NO"
    source_url: Optional[str] = None
    last_updated: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: dict


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class Zone(BaseModel):
    zone_id: str
    council: Optional[str] = None
    zone_name: Optional[str] = None
    rate_per_hour: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    notes: Optional[str] = None


class RateTier(BaseModel):
    tier_id: str
    location_name: Optional[str] = None
    duration: Optional[str] = None
    rate: Optional[float] = None
    currency: Optional[str] = "MYR"
    notes: Optional[str] = None


class Stats(BaseModel):
    total_locations: int
    total_valet: int
    total_airport: int
    avg_rate_per_hour: Optional[float] = None
    cities: List[str]
    types: List[str]
