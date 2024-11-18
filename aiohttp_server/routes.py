from aiohttp import web

from aiohttp_server.crud import create_task, delete_task, get_tasks, update_task

routes = web.RouteTableDef()


@routes.get("/tasks")
async def get_task_endpoint(request):
    data = request.query.get("status")
    result = await get_tasks(pool=request.app["pool"], status=data)
    return web.json_response(result)


@routes.post("/tasks")
async def create_task_endpoint(request):
    data = await request.json()
    result = await create_task(request.app["pool"], data)
    return web.json_response(result)


@routes.put("/tasks")
async def update_task_endpoint(request):
    data = await request.json()
    result = await update_task(request.app["pool"], data)
    return web.json_response(result)


@routes.delete("/tasks/{id}")
async def delete_task_endpoint(request):
    idx = request.match_info["id"]
    result = await delete_task(pool=request.app["pool"], task_id=int(idx))
    return web.json_response(result)
