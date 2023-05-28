import uvicorn

if __name__ == "__main__":
    uvicorn.run("Server.Api.api_Server:app", reload=True)
    uvicorn.run("Box.Api.api_frontend:app", reload=True)