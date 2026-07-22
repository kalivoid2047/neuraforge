"""Neuraforge API — modular monolith (ADR-0001).

Module layout mirrors ARCHITECTURE.md §3: each domain module exposes
models / schemas / service / router; cross-module side effects go through
core.events; routers contain no business logic.
"""
