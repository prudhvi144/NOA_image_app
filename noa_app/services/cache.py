from __future__ import annotations

from collections import OrderedDict
from typing import Generic, TypeVar, Optional
from pathlib import Path
import hashlib
import pickle

K = TypeVar("K")
V = TypeVar("V")


class LRUCache(Generic[K, V]):
	def __init__(self, capacity: int = 256, disk_dir: Optional[Path] = None) -> None:
		self.capacity = capacity
		self.store: OrderedDict[K, V] = OrderedDict()
		self.disk_dir = disk_dir
		if disk_dir is not None:
			disk_dir.mkdir(parents=True, exist_ok=True)

	def _key_to_path(self, key: K) -> Optional[Path]:
		if self.disk_dir is None:
			return None
		h = hashlib.sha1(repr(key).encode("utf-8")).hexdigest()
		return self.disk_dir / f"{h}.pkl"

	def get(self, key: K) -> Optional[V]:
		if key in self.store:
			self.store.move_to_end(key)
			return self.store[key]
		p = self._key_to_path(key)
		if p is not None and p.exists():
			with p.open("rb") as f:
				val: V = pickle.load(f)
				self.store[key] = val
				self.store.move_to_end(key)
				self._evict()
				return val
		return None

	def put(self, key: K, value: V) -> None:
		self.store[key] = value
		self.store.move_to_end(key)
		self._evict()
		p = self._key_to_path(key)
		if p is not None:
			with p.open("wb") as f:
				pickle.dump(value, f)

	def _evict(self) -> None:
		while len(self.store) > self.capacity:
			self.store.popitem(last=False)
