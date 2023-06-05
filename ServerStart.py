import matplotlib
import uvicorn

if __name__ == '__main__':
    matplotlib.use("TkAgg")
    uvicorn.run('Server.Api.api_Server:app', host='192.168.100.1')