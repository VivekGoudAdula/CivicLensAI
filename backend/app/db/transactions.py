"""Firestore transaction and batch write helpers."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from google.cloud.firestore_v1.transaction import transactional

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client as FirestoreClient
    from google.cloud.firestore_v1 import Transaction
    from google.cloud.firestore_v1.batch import WriteBatch

T = TypeVar("T")


def run_transaction(db: FirestoreClient, callback: Callable[[Transaction], T]) -> T:
    """Execute a callback inside a Firestore transaction."""

    @transactional
    def _execute(transaction: Transaction) -> T:
        return callback(transaction)

    return _execute(db.transaction())


def run_batch_write(
    db: FirestoreClient,
    callback: Callable[[WriteBatch], None],
    *,
    commit: bool = True,
) -> WriteBatch:
    """Execute operations inside a Firestore batch write."""
    batch = db.batch()
    callback(batch)
    if commit:
        batch.commit()
    return batch
