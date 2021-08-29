import abc
from enum import Enum, auto
from typing import List, Union

from allocation.domain import model


class InvalidEntity(Exception):
    pass


class Entity(Enum):
    BATCH = auto()
    ORDERLINE = auto()


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, entity_ref, entity: Entity = Entity.BATCH) -> Union[model.Batch, model.OrderLine]:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, entity: Entity = Entity.BATCH) -> Union[List[model.Batch], List[model.OrderLine]]:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, entity_ref, entity: Entity = Entity.BATCH):
        if entity == Entity.BATCH:
            return self.session.query(model.Batch).filter_by(reference=entity_ref).one()
        elif entity == Entity.ORDERLINE:
            return self.session.query(model.OrderLine).filter_by(orderid=entity_ref).one()
        else:
            raise InvalidEntity

    def list(self, entity: Entity = Entity.BATCH):
        if entity == Entity.BATCH:
            return self.session.query(model.Batch).all()
        elif entity == Entity.ORDERLINE:
            return self.session.query(model.OrderLine).all()
        else:
            raise InvalidEntity
