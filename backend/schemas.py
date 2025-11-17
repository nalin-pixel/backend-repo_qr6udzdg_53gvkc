from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# Each model corresponds to a MongoDB collection with the lowercase name of the class
# Example: class Booking -> "booking" collection


class Instructor(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    bio: Optional[str] = None


class Course(BaseModel):
    title: str
    duration: str
    price: str
    description: str
    active: bool = True


class Booking(BaseModel):
    name: str = Field(..., description="Kontaktpersonens namn")
    company: Optional[str] = Field(None, description="Företag")
    phone: Optional[str] = None
    email: EmailStr
    course: str
    message: Optional[str] = None


class BookingResponse(BaseModel):
    success: bool
    message: str
    booking_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    database: str
