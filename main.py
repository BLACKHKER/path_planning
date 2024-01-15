# 所需库函数
from MQTT_broadcast import mqtt_run
from fastapi import FastAPI,applications,WebSocket,WebSocketDisconnect
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from router import info
import uvicorn

# Actual monkey patch
def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.29/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.29/swagger-ui.css")
applications.get_swagger_ui_html = swagger_monkey_patch

app = FastAPI()
# 跨域
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加路由
app.include_router(info.router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="172.22.109.32", port=8008, reload=True, debug=True)
