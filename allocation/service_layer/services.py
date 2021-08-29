from allocation.domain import model
from allocation.adapters.repository import AbstractRepository, Entity


class BatchAlreadyExists(Exception):
    pass


class OrderDoesNotExist(Exception):
    pass


class InvalidDeallocation(Exception):
    pass


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def add_batch(batch: model.Batch, repo: AbstractRepository, session):
    batches = repo.list()
    if batch in batches:
        raise BatchAlreadyExists(f'Batch {batch.sku} already exists.')
    repo.add(batch)
    session.commit()


def allocate(line: model.OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}.')
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(orderid: str, repo: AbstractRepository, session):
    batches = repo.list()
    orderline = repo.get(orderid, Entity.ORDERLINE)
    if not orderline:
        raise OrderDoesNotExist(f'Invalid orderid {orderid}.')

    for batch in batches:
        if batch.deallocate(orderline):
            session.commit()
            return

    # No allocated batch was found
    raise InvalidDeallocation(f'Orderline {orderline} not allocated to a batch.')
