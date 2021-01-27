from typing import NamedTuple
from typing import Union, Any, List, Tuple
import asyncpg
import os

User = NamedTuple('User', [('id', int), ('point', int), ('name', str)])


class Database:
    """CREATE TABLE users (user_id bigint, point integer, name strings, PRIMARY KEY(user_id))"""

    def __init__(self, bot: Any):
        self.bot = bot
        self.conn: Union[asyncpg.Connection, None] = None

    async def check_database(self) -> None:
        conn = self.conn or await self.setup()
        try:
            await conn.execute('select "users"::regclass')
        except asyncpg.exceptions.UndefinedColumnError:
            await conn.execute('CREATE TABLE users (user_id bigint, point INT, name VARCHAR(45), PRIMARY KEY(user_id))')

    async def setup(self) -> asyncpg.Connection:
        self.conn = await asyncpg.connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            password = os.environ['SQL'],
            database = "point",
            loop=self.bot.loop,
        )
        return self.conn

    async def close(self) -> None:
        if self.conn is not None:
            await self.conn.close()

    async def get_user(self, user_id: int) -> Union[None, User]:
        conn = self.conn or await self.setup()
        data = await conn.fetch('SELECT * FROM users WHERE user_id=$1', user_id)
        if not data:
            return None

        target = list(data[0])
        return User(target[0], target[1], target[2])

    async def get_user_rankings(self) -> List[Tuple[User, int]]:
        conn = self.conn or await self.setup()
        users_data = await conn.fetch('SELECT *, RANK() OVER(ORDER BY point DESC) AS rank FROM users LIMIT 10')
        return [(User(user_data[0], user_data[1], user_data[2]), user_data[3]) for user_data in users_data]

    async def get_user_ranking(self, id: int) -> int:
        conn = self.conn or await self.setup()
        return await conn.fetchval('SELECT (SELECT COUNT(*) FROM users AS u WHERE u.point > users.point) + 1 FROM users WHERE user_id=$1', id)

    async def create_user(self, user_id: int, user_name) -> Union[None, User]:
        conn = self.conn or await self.setup()
        await conn.execute('INSERT INTO users (user_id, point, name) VALUES ($1, $2, $3)', user_id, 1, user_name)
        return await self.get_user(user_id)

    async def add_point(self, user_id: int) -> Union[None, User]:
        conn = self.conn or await self.setup()
        await conn.execute('UPDATE users SET point + 1 WHERE user_id = $1', user_id)
        return await self.get_user(user_id)

    async def update_user(self, user_id: int, point: int) -> Union[None, User]:
        conn = self.conn or await self.setup()
        await conn.execute('UPDATE users SET point = $1 WHERE user_id = $3', point, user_id)
        return await self.get_user(user_id)
