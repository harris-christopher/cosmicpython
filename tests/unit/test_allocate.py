from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, OutOfStock, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)
    assert batch.available_quantity == 18


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "BLUE-CHAIR", qty=20, eta=None)
    shipment_batch = Batch("shipment_batch", "BLUE-CHAIR", qty=20, eta=tomorrow)
    line = OrderLine("oref", "BLUE-CHAIR", 3)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 17
    assert shipment_batch.available_quantity == 20


def test_prefers_earlier_batches():
    earliest = Batch("earliest-batch", "WEIRD-LAMP", qty=20, eta=today)
    medium = Batch("medium-batch", "WEIRD-LAMP", qty=20, eta=tomorrow)
    latest = Batch("latest-batch", "WEIRD-LAMP", qty=20, eta=later)
    line = OrderLine("oref", "WEIRD-LAMP", qty=10)

    allocate(line, [earliest, medium, latest])

    assert earliest.available_quantity == 10
    assert medium.available_quantity == 20
    assert latest.available_quantity == 20


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "POMPOUS-POSTER", 20, eta=today)
    shipment_batch = Batch("shipment_batch", "POMPOUS-POSTER", 20, eta=tomorrow)
    line = OrderLine("oref", "POMPOUS-POSTER", 5)

    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch('batch1', 'SMALL-FORK', 10, eta=today)
    allocate(OrderLine('order1', 'SMALL-FORK', 10), [batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine('order2', 'SMALL-FORK', 1), [batch])

