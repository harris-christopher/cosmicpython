import pytest

from allocation.adapters import repository
from allocation.domain import model
from allocation.service_layer import services


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


class FakeRepository(repository.AbstractRepository):

    def __init__(self, batches, orderlines):
        self._batches = set(batches)
        self._orderlines = set(orderlines)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, entity_ref, entity=repository.Entity.BATCH):
        if entity == repository.Entity.BATCH:
            return next(b for b in self._batches if b.reference == entity_ref)
        elif entity == repository.Entity.ORDERLINE:
            return next(ol for ol in self._orderlines if ol.orderid == entity_ref)
        else:
            raise repository.InvalidEntity(f'Invalid Entity {entity}.')

    def list(self, entity=repository.Entity.BATCH):
        if entity == repository.Entity.BATCH:
            return list(self._batches)
        elif entity == repository.Entity.ORDERLINE:
            return list(self._orderlines)
        else:
            raise repository.InvalidEntity(f'Invalid Entity {entity}.')


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())


def test_commits():
    line = model.OrderLine('01', 'OMINOUS-MIRROR', 10)
    batch = model.Batch('b1', 'OMINOUS-MIRROR', 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([], []), FakeSession()
    new_batch = model.Batch("b1", "BLUE-PLINTH", 100, None)
    new_orderline = model.OrderLine("o1", "BLUE-PLINTH", 10)
    services.add_batch(new_batch, repo, session)
    services.allocate(new_orderline, repo, session)

    batch = repo.get(entity_ref="b1")
    assert batch.available_quantity == 90
    services.deallocate(new_orderline.orderid, repo, session)
    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity():
    ...  #  TODO


def test_trying_to_deallocate_unallocated_batch():
    repo, session = FakeRepository([]), FakeSession()
    unallocated_batch = model.Batch("b1", "ODD-CUP", 25, None)

    ...  #  TODO: should this error or pass silently? up to you.
