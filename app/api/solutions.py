# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.core.crud import get_match
# import logging
#
# router = APIRouter()
#
# logger = logging.getLogger(__name__)
#
# @router.get("/matches")
# def get_all_matches(db: Session = Depends(get_db)):
#     return get_match(db)
