from fastapi import FastAPI

from src.routes.v1 import get_queued_job, multi_file_parse, single_search

app = FastAPI()


app.add_api_route(
    path="/",
    endpoint=lambda: {"status": "success", "message": "The server is running"},
    description="Default root endpoint",
    methods=['GET'],
)
app.add_api_route(
    path="/parse/single/", endpoint=single_search, description="Endpoint to parse a single PDF file.", methods=['POST']
)
app.add_api_route(
    path="/parse/multi/",
    endpoint=multi_file_parse,
    description="Endpoint to queue multiple PDF files.",
    methods=['POST'],
)
app.add_api_route(
    path="/parse/query/{_id}",
    endpoint=get_queued_job,
    description="Endpoint to query a job based on its Id.",
    methods=['GET'],
)
