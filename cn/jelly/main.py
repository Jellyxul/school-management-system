
import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# 全局配置：方案二
from cn.jelly.student.api import router as student_router
from cn.jelly.teacher.api import router as teacher_router
from cn.jelly.subject.api import router as subject_router
from cn.jelly.clazz.api import router as clazz_router
from cn.jelly.arrangement.api import router as arrangement_router
from cn.jelly.enrollment.api import router as enrollment_router
from cn.jelly.dashboard.api import router as dashboard_router

app = FastAPI(
    title="management system",
    description="use management system to manage students and teachers modules"
)

app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(subject_router)
app.include_router(clazz_router)
app.include_router(arrangement_router)
app.include_router(enrollment_router)
app.include_router(dashboard_router)
# 挂载静态资源：项目根目录 static（js/css/html 分开存放，html 按后端模块分目录）
# 用 __file__ 定位，不受启动时工作目录影响
STATIC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static")
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# 全局配置，方案一
# # 可改变输出级别，优先级大于等于设定级别的全部输出
# logging.basicConfig(
#     # 配置日志输出优先级
#     level=logging.INFO,
#     # 格式化输出
#     # 时间-线程-输出级别-模块名：日志信息
#     format='%(asctime)s - %(threadName)s - [%(levelname)s] - %(name)s:%(message)s',
#     handlers=[
#         # 配置日志输出目标类型
#         logging.FileHandler('user information.log', encoding='utf-8'),
#         # 控制台输出
#         logging.StreamHandler()
#     ],
# )


@app.get("/")
def home():
    """home page: redirect to admin index"""
    return RedirectResponse(url="/static/html/index.html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

