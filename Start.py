# import uvicorn
#
# if __name__ == "__main__":
#     uvicorn.run("Server.Api.api_Server:app", reload=True)
#     uvicorn.run("Box.Api.api_frontend:app", reload=True)
# from Server.Service import DB
import Server.Service.DatabaseService
ddd = Server.Service.DatabaseService.DatabaseService()
states = ddd.DeleteAllCamera()