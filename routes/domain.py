
import aiofiles
from utils.jwt_utils import encode_jwt
from utils.middleware import AuthRoute
from fastapi import APIRouter, Depends, Body
from fastapi.concurrency import run_in_threadpool
from datamodels.db import Domains, get_db_session, URLs
from fastapi.responses import HTMLResponse, JSONResponse
from utils.helper_functions import fetch_base_url, generate_id, estimate_domain_size
from datamodels.core_models import DomainSearchRequest, NewDomainRequest, Phase

router = APIRouter(route_class=AuthRoute)   # Protected Endpoint

def search_domain_fn(domain_base_url: str, session, is_ready: bool = True)-> None:
    """ Searches if the domain is present or not """
    domain_obj = session.query(Domains).filter(Domains.domain_base_url == domain_base_url, Domains.is_ready == is_ready).first()
    if domain_obj is None:
        return None
    
    return domain_obj

@router.get("/")
async def get_domain_page():
    """ Fetches the Domain page """

    html_content = None
    async with aiofiles.open("src/html/domain.html", 'r') as file:
        html_content = await file.read()
    
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/search")
def search_domain(session = Depends(get_db_session), request_data: DomainSearchRequest = Body(...)):
    """ Lets user search for a specific domain using base URL """
    print(request_data.__dict__)
    domain_url = request_data.domain_url
    domain_base_url = fetch_base_url(domain_url)
    print(f"Base URL - {domain_base_url}")

    if domain_base_url is None:
        # Raise Exception with domain url is wrong
        data = {"status_code": 420, "message": "URL is invalid"}
        response = JSONResponse(status_code404, content=data)
        return response
    
    domain_obj = search_domain_fn(domain_base_url=domain_base_url,session=session)
    if domain_obj is None:
        # This domain is not present
        data = {"status_code": 404, "message": "Domain Not Found"}
        response = JSONResponse(status_code=404, content=data)
        return response
    s
    domain_id = domain_obj.domain_id
    domain_name = domain_obj.domain_name
    total_number_of_urls = domain_obj.total_urls
    created_at = domain_obj.created_at

    domain_data = {
        "domain_id": domain_id,
        "domain_name": domain_name,
        "total_number_of_urls": total_number_of_urls,
        "created_at": created_at,
        "url": f"/domain/id/{domain_id}"
    }

    data = {"status_code": 200, "message": "Domain found with URL", "data": domain_data}
    return JSONResponse(status_code=200, content=data)

@router.post("/id/{domain_id}")
def get_domain_details(domain_id: int, session = Depends(get_db_session)):
    """ Fetch the details of the domain """
    url_objs = session.query(URLs).filter(URLs.domain_id == domain_id).all()

    if len(url_objs) == 0:
        # No URLs present
        data = {"status_code": 404, "message": "URLs not found"}
        return JSONResponse(status_code=404, content=data)

    total_urls = []
    for url_obj in url_objs:
        url_data = {
            "path": url_obj.path,
            "url_id": url_obj.url_id
        }
        total_urls.append(url_data)
    
    url_data = {
        "domain_id": domain_id,
        "urls": total_urls
    }
    data = {"status_code": 200, "message": "URLs loaded", "data": url_data}
    return JSONResponse(status_code=200, content=data)

@router.post("/new")
def add_new_domain(session=Depends(get_db_session), new_domain: NewDomainRequest = Body(...)):
    """ Add new domain to crawl """

    domain_base_url = fetch_base_url(new_domain.base_url)
    domain_name = new_domain.name

    domain_obj = search_domain_fn(domain_base_url=domain_base_url, session=session)

    if domain_obj:
        # The domain already exists
        data = {"status_code": 403, "message": "Domain already exists"}
        return JSONResponse(status_code=403, content=data)
    
    # If domain doesn't exists -> create a new domain
    new_domain_obj = Domains(domain_name=domain_name, domain_base_url=domain_base_url)
    session.add(new_domain_obj)
    session.commit()

    # The domain is created & needs to be crawled
    data = {"status_code": 200, "message": "Domain Crawling Initialized"}
    return JSONResponse(status_code=200, content=data)

