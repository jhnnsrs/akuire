import asyncio
from typing import (
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Collection,
    TypeVar,
)

from akuire.events.data_event import UncollectedBufferEvent, ZipEvent

_T = TypeVar("_T")


async def _await_next(iterator: AsyncIterator[_T]) -> _T:
    return await iterator.__anext__()


def _as_task(iterator: AsyncIterator[_T]) -> asyncio.Task[_T]:
    return asyncio.create_task(_await_next(iterator))


async def amerge(*iterators: Collection[AsyncIterator[_T]]) -> AsyncIterable[_T]:
    next_tasks = {iterator: _as_task(iterator) for iterator in iterators}
    while next_tasks:
        done, _ = await asyncio.wait(
            next_tasks.values(), return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            iterator = next(it for it, t in next_tasks.items() if t == task)

            try:
                yield task.result()
            except StopAsyncIteration:
                del next_tasks[iterator]
            except Exception:
                for t in next_tasks.values():
                    t.cancel()

                await asyncio.gather(*next_tasks.values(), return_exceptions=True)

                raise task.exception()
            else:
                next_tasks[iterator] = _as_task(iterator)


async def _amerge(*iterators: Collection[AsyncIterator[_T]]) -> AsyncIterable[_T]:
    next_tasks = {iterator: _as_task(iterator) for iterator in iterators}
    while next_tasks:
        done, _ = await asyncio.wait(
            next_tasks.values(), return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            iterator = next(it for it, t in next_tasks.items() if t == task)
            index = iterators.index(iterator)
            try:
                yield index, task.result()
            except StopAsyncIteration:
                del next_tasks[iterator]
            except Exception:
                pass
            else:
                next_tasks[iterator] = _as_task(iterator)


async def azip(*generators):

    collected_values = [None for i in generators]
    buffer = [[] for i in generators]

    async for i in _amerge(*generators):
        index, value = i
        buffer[index].append(value)

        if all(len(i) > 0 for i in buffer):
            collected_values = [i.pop(0) for i in buffer]
            yield ZipEvent(collected_values)

    if any(len(i) > 0 for i in buffer):
        yield UncollectedBufferEvent(collected_values)


async def azip_longest(*generators):
    generators = [i.__aiter__() for i in generators]

    while True:
        try:
            yield ZipEvent([await i.__anext__() for i in generators])
        except StopAsyncIteration:
            yield ZipEvent([None for i in generators])


async def aenumerate(generator):
    i = 0
    async for j in generator:
        yield i, j
        i += 1


async def achain(*generators):
    for i in generators:
        async for j in i:
            yield j


async def auntil(
    generator: AsyncGenerator[object, None],
    condition: Callable[[object], Awaitable[bool]],
):
    async for i in generator:
        yield i
        if await condition(i):
            break


async def ainterupting(
    generator: AsyncGenerator[object, None],
    interrupter: AsyncGenerator[object, None],
    condition: Callable[[object], Awaitable[bool]],
    restarts: int = None,
):

    broken = False
    async for i in generator:
        if await condition(i):
            broken = True
            break
            yield i
        else:
            yield i

    if broken:
        async for i in interrupter:
            yield i

    if restarts is not None:
        if restarts == 0:
            return

        async for i in ainterupting(generator, interrupter, condition, restarts - 1):
            yield i
