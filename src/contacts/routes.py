import contacts.schemas as schemas
import contacts.models as models
from fastapi.responses import JSONResponse
from fastapi import status, APIRouter, Depends, HTTPException, Query
from typing import Optional
import calendar

import src.batabase as database
from sqlalchemy import or_, extract, and_


from datetime import datetime, timedelta, date


router = APIRouter(prefix="/contacts", tags=["contacts"])


# @router.get("/")
# async def root(db=Depends(database.get_database)) -> schemas.TestResponseSchema:
#     return schemas.TestResponseSchema(
#         id=1, name="Vlad", email="", phone="", age=25, born_date=None
#     )


@router.get("/birth_list")
async def get_upcoming_birthdays(
    db=Depends(database.get_database),
) -> list[schemas.TestResponseSchema]:
    today = datetime.now().date()
    in_a_week = today + timedelta(days=7)

    birth_list = []

    if today.month == in_a_week.month:
        birth_list = (
            db.query(models.Contact)
            .filter(
                and_(
                    extract("month", models.Contact.born_date) == today.month,
                    extract("day", models.Contact.born_date) >= today.day,
                    extract("day", models.Contact.born_date) <= in_a_week.day,
                )
            )
            .all()
        )
    else:
        end_of_month = today.replace(
            day=calendar.monthrange(today.year, today.month)[1]
        )

        end_of_month_birthdays = (
            db.query(models.Contact)
            .filter(
                and_(
                    extract("month", models.Contact.born_date) == today.month,
                    extract("day", models.Contact.born_date) >= today.day,
                )
            )
            .all()
        )

        start_of_month_birthdays = (
            db.query(models.Contact)
            .filter(
                and_(
                    extract("month", models.Contact.born_date) == in_a_week.month,
                    extract("day", models.Contact.born_date) <= in_a_week.day,
                )
            )
            .all()
        )

        birth_list = end_of_month_birthdays + start_of_month_birthdays

    return [schemas.TestResponseSchema.from_orm(contact) for contact in birth_list]


@router.get("/contact")
async def search_contact_by_query(
    name: Optional[str] = Query(None, description="search by name"),
    email: Optional[str] = Query(None, description="search by email"),
    phone: Optional[str] = Query(None, description="search by phone"),
    db=Depends(database.get_database),
) -> list[schemas.TestResponseSchema]:
    search_criteria = {"name": name, "email": email, "phone": phone}
    query = db.query(models.Contact)
    filter_conditions = [
        getattr(models.Contact, key).contains(value)
        for key, value in search_criteria.items()
        if value
    ]

    if filter_conditions:
        query = query.filter(or_(*filter_conditions))

    contacts = query.all()
    return [contact for contact in contacts]


@router.get("/all")
async def get_all_contacts(
    db=Depends(database.get_database),
) -> list[schemas.TestResponseSchema]:
    return [contact for contact in db.query(models.Contact).all()]


@router.get("/get_contact/{id}")
async def get_contact(
    id: int, db=Depends(database.get_database)
) -> schemas.TestResponseSchema:
    contact = db.query(models.Contact).filter(models.Contact.id == id).first()

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    return contact


@router.post("/create_contact")
async def create_contact(
    contact_data: schemas.TestRequestSchema, db=Depends(database.get_database)
) -> JSONResponse:
    new_contact = models.Contact(
        name=contact_data.name.lower(),
        age=contact_data.age,
        email=contact_data.email,
        phone=contact_data.phone,
        born_date=contact_data.born_date,
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Contact created", "id": new_contact.id},
    )


@router.delete("/remove_contact/{id}")
async def delete_contact(id: int, db=Depends(database.get_database)) -> JSONResponse:
    contact = db.query(models.Contact).filter(models.Contact.id == id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Contact was delete", "id": contact.id},
    )
