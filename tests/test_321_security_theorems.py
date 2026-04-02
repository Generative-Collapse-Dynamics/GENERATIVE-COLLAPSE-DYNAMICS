"""Tests for security theorems closure (security domain).

Validates 10 cross-cutting theorems (T-SEC-1 through T-SEC-10)
that operate on the security-kernel entity set.
"""

from __future__ import annotations

import pytest

from closures.security.security_kernel import SKKernelResult, compute_all_entities
from closures.security.security_theorems import (
    verify_all_theorems,
    verify_t_sec_1,
    verify_t_sec_2,
    verify_t_sec_3,
    verify_t_sec_4,
    verify_t_sec_5,
    verify_t_sec_6,
    verify_t_sec_7,
    verify_t_sec_8,
    verify_t_sec_9,
    verify_t_sec_10,
)


@pytest.fixture(scope="module")
def all_results() -> list[SKKernelResult]:
    return compute_all_entities()


class TestSecurityTheorems:
    def test_t_sec_1(self, all_results):
        assert verify_t_sec_1(all_results)["passed"]

    def test_t_sec_2(self, all_results):
        assert verify_t_sec_2(all_results)["passed"]

    def test_t_sec_3(self, all_results):
        assert verify_t_sec_3(all_results)["passed"]

    def test_t_sec_4(self, all_results):
        assert verify_t_sec_4(all_results)["passed"]

    def test_t_sec_5(self, all_results):
        assert verify_t_sec_5(all_results)["passed"]

    def test_t_sec_6(self, all_results):
        assert verify_t_sec_6(all_results)["passed"]

    def test_t_sec_7(self, all_results):
        assert verify_t_sec_7(all_results)["passed"]

    def test_t_sec_8(self, all_results):
        assert verify_t_sec_8(all_results)["passed"]

    def test_t_sec_9(self, all_results):
        assert verify_t_sec_9(all_results)["passed"]

    def test_t_sec_10(self, all_results):
        assert verify_t_sec_10(all_results)["passed"]

    def test_all_theorems_pass(self):
        for t in verify_all_theorems():
            assert t["passed"], f"{t['name']} failed: {t}"
