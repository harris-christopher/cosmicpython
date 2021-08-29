from datetime import date

from model import Batch, OrderLine


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty)
    )


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("100", 10, 3)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("100", 3, 10)
    assert not small_batch.can_allocate(large_line)


def test_can_allocate_if_available_equal_to_required():
    equal_batch, equal_line = make_batch_and_line("100", 10, 10)
    assert equal_batch.can_allocate(equal_line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "100", 10)
    bad_line = OrderLine("order-234", "555", 3)
    assert not batch.can_allocate(bad_line)


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("IKEA-LAMP", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 10, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 8


