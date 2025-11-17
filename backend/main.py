from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from schemas import Instructor, Course, Booking, BookingResponse, HealthResponse
from database import create_document, get_documents

app = FastAPI(title="JK Utbildning API", version="1.0.0")

# Allow all origins for dev convenience
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test", response_model=HealthResponse)
async def test_connection():
    return HealthResponse(status="ok", database="connected")


# Seed endpoint (optional) to prefill instructors and courses if empty
@app.post("/seed")
async def seed():
    # Instructors
    instructors = [
        Instructor(
            name="Therese Janerup Kolstad",
            email="therese@jk-utbildning.se",
            bio="Erfaren utbildare med fokus på säkerhetskultur och arbetsmiljö.",
        ),
        Instructor(
            name="Martin Wistarnd",
            email="martin@jk-utbildning.se",
            bio="Specialist på byggsäkerhet, fallskydd och lyftutbildningar.",
        ),
        Instructor(
            name="Marko Bogdanski",
            email=None,
            bio="Expert på asbest, sanering och praktiska utbildningar i fält.",
        ),
    ]

    courses = [
        Course(
            title="Asbest Grundkurs",
            duration="4 dagar",
            price="11 500 kr",
            description="Hantera asbest enligt AFS 2006:1 §36. Ger full behörighet för rivning och sanering.",
        ),
        Course(
            title="Fallskydd – användare",
            duration="4 timmar",
            price="2 300 kr",
            description="Förstå riskerna vid arbete över 2 meter och använd personlig skyddsutrustning rätt.",
        ),
        Course(
            title="Säkra lyft och signalman",
            duration="4 timmar",
            price="2 100 kr",
            description="Säker användning av lyftanordningar och minska risken för olyckor.",
        ),
        Course(
            title="Brandfarliga heta arbeten",
            duration="1 dag",
            price="2 600 kr",
            description="Obligatorisk kurs för alla som arbetar med värme och gnistor.",
        ),
        Course(
            title="Lift / Mobila arbetsplattformar",
            duration="1 dag",
            price="2 600 kr",
            description="Arbeta effektivt och säkert med mobila plattformar.",
        ),
    ]

    # Insert if collections are empty
    existing_instructors = await get_documents("instructor")
    existing_courses = await get_documents("course")

    if not existing_instructors:
        for i in instructors:
            await create_document("instructor", i.dict())

    if not existing_courses:
        for c in courses:
            await create_document("course", c.dict())

    return {"status": "seeded"}


@app.get("/instructors", response_model=List[Instructor])
async def list_instructors():
    docs = await get_documents("instructor")
    # Convert to Pydantic models (ignore _id)
    return [Instructor(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.get("/courses", response_model=List[Course])
async def list_courses():
    docs = await get_documents("course")
    return [Course(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]


@app.post("/book", response_model=BookingResponse)
async def book_course(payload: Booking):
    # persist booking
    doc = await create_document("booking", payload.dict())
    if not doc:
        raise HTTPException(status_code=500, detail="Kunde inte skapa bokning")
    return BookingResponse(success=True, message="Tack! Vi kontaktar dig inom kort.", booking_id=str(doc.get("_id")))
