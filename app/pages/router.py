from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from app.hotels.router import find_all

router = APIRouter(
    prefix='/pages',
    tags=['Странички']
)

templates = Jinja2Templates(directory='app/templates')


@router.get('/hotels')
async def get_hotel_page(request: Request, hotels=Depends(find_all)):
    return templates.TemplateResponse(name='hotels.html', context={'request': request, 'hotels': hotels})
