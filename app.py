from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
from jinja2 import Environment, FileSystemLoader
# from slowapi import Limiter
# from slowapi.errors import RateLimitExceeded
# from slowapi.util import get_remote_address
import logging
from netcine import catalog_search, search_link, ntc_search_catalog, meta_ntc, get_stream_ntc
import os
from urllib.parse import quote_plus, quote, unquote
import get_channels

templates = Environment(loader=FileSystemLoader("templates"))
# limiter = Limiter(key_func=get_remote_address)
# rate_limit = '3/second'

app = FastAPI()


# Configure o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
VERSION = "1.0.1-ver2"
logger.info(f"Versão da aplicação: {VERSION}")



MANIFEST = {
    "id": "com.skyflix",
    "version": "1.0.1",
    "name": "SKYFLIX",
    "description": "Tenha o melhor dos filmes e séries com Skyflix",
    "logo": "https://i.imgur.com/qVgkbYn.png",
    "resources": ["catalog", "meta", "stream"],
    "types": ["tv", "movie", "series"],
    "catalogs": [
        {
            "type": "tv",
            "id": "skyflix",
            "name": "SKYFLIX",
            "extra": [
                {
                    "name": "genre",
                    "options": [
                        "Abertos",
                        "Reality",
                        "Esportes",
                        "NBA",
                        "PPV",
                        "Paramount plus",
                        "DAZN",
                        "Nosso Futebol",
                        "UFC",
                        "Combate",
                        "NFL",
                        "Documentarios",
                        "Infantil",
                        "Filmes e Series",
                        "Telecine",
                        "HBO",
                        "Cine Sky",
                        "Noticias",
                        "Musicas",
                        "Variedades",
                        "Cine 24h",
                        "Desenhos",
                        "Series 24h",
                        "Religiosos",
                        "4K",
                        "Radios"
                    ],
                    "isRequired": False
                }
            ]
        },
        {
            "type": "movie",
            "id": "skyflix",
            "name": "SKYFLIX",
            "extraSupported": ["search"]
        },
        {
            "type": "series",
            "id": "skyflix",
            "name": "SKYFLIX",
            "extraSupported": ["search"]
        }
    ],
    "idPrefixes": ["skyflix", "tt"]
}

# def get_external_ip():
#     try:
#         response = requests.get("https://api64.ipify.org?format=json")
#         return response.json().get("ip")
#     except requests.RequestException:
#         return None

# @app.exception_handler(RateLimitExceeded)
# async def rate_limit_handler(request, exc):
#     return JSONResponse(content={"error": "Too many requests"}, status_code=429)

def add_cors(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    template = templates.get_template("index.html")
    response = HTMLResponse(template.render(
        name=MANIFEST['name'],
        types=MANIFEST['types'],
        logo=MANIFEST['logo'],
        description=MANIFEST['description'],
        version=MANIFEST['version']
    ))
    return add_cors(response)


@app.get("/manifest.json")
async def manifest(request: Request):
    return add_cors(JSONResponse(content=MANIFEST))

@app.get("/catalog/tv/skyflix/genre={id}.json")
async def genres(id: str, request: Request):
    try:
        api = get_channels.get_api()
        canais_ = [canal for canal in api.list_channels(id)]
    except:
        canais_ = []
    return add_cors(JSONResponse(content={"metas": canais_}))

@app.get("/catalog/{type}/{id}.json")
async def catalog_route(type: str, id: str, request: Request):    
    if type == 'tv':
        try: 
            api = get_channels.get_api()       
            itens = [canal for canal in api.list_channels('Abertos')]
        except:
            itens = []
    else:
        itens = []
    return add_cors(JSONResponse(content={"metas": itens}))

@app.get("/catalog/{type}/skyflix/search={query}.json")
async def search(type: str, query: str, request: Request):
    catalog = ntc_search_catalog(query)
    results = [item for item in catalog if item.get("type") == type] if catalog else []
    return add_cors(JSONResponse(content={"metas": results}))

@app.get("/meta/{type}/{id}.json")
async def meta(type: str, id: str, request: Request):
    if type == 'tv':
        try:
            m = get_channels.get_meta_tv(id)
        except:
            m = {}
    else:
        try:
            m = meta_ntc(type, id)
        except:
            m = {}
    return add_cors(JSONResponse(content={"meta": m}))

@app.get("/stream/{type}/{id}.json")
async def stream(type: str, id: str, request: Request):
    if type == "tv":
        try:
            streams = get_channels.get_stream_tv(id).get('streams', [])
        except:
            streams = []
    elif 'tt' in id and type in ["movie", "series"]:
        try:
            streams = search_link(id)
        except:
            streams = []
    else:
        try:
            streams = get_stream_ntc(type, id)
        except:
            streams = []
    return add_cors(JSONResponse(content={"streams": streams}))

@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    return add_cors(Response(status_code=204))


