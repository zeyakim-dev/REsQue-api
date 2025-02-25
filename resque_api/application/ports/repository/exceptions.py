class AggregateNotFoundError(Exception):
    """Aggregate를 찾을 수 없을 때 발생하는 예외"""
    ...

class DeleteNonExistentAggregateError(Exception):
    """존재하지 않는 Aggregate를 삭제하려고 할 때 발생하는 예외"""
    ...
