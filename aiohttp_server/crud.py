import asyncpg


async def create_task(pool: asyncpg.Pool, data: dict):
    async with pool.acquire() as conn:
        query = """
            INSERT INTO tasks (title, description, status, user_id)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """
        task = await conn.fetchrow(query, *data.values())
    return dict(task)


async def get_tasks(pool: asyncpg.Pool, status: str = None):
    async with pool.acquire() as conn:
        if status:
            query = "SELECT * FROM tasks WHERE status = $1"
            tasks = await conn.fetch(query, status)
        else:
            query = "SELECT * FROM tasks"
            tasks = await conn.fetch(query)
        return {"tasks": [dict(task) for task in tasks]}


async def update_task(pool: asyncpg.Pool, data: dict):
    async with pool.acquire() as conn:
        query = """
                 UPDATE tasks
                 SET title = $1, description = $2, status = $3
                 WHERE id = $4
                 RETURNING *
                 """
        updated_rows = await conn.fetchrow(query, *data.values())
        if updated_rows:
            return dict(updated_rows)


async def delete_task(pool: asyncpg.Pool, task_id: int):
    async with pool.acquire() as conn:
        query = """
            DELETE FROM tasks
            WHERE id = $1
            RETURNING *
                 """
        deleted_task = await conn.fetchrow(query, task_id)
    if deleted_task:
        return dict(deleted_task)
