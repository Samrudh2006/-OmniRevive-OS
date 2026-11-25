import pytest
from backend.app.b2b.invoice_store import InvoiceStore


def test_protected_fields_cannot_be_mutated(tmp_path):
    store = InvoiceStore(db_path=str(tmp_path / "inv.db"))
    for field in ("invoice_id", "mutations", "created_at", "updated_at", "__class__"):
        with pytest.raises(ValueError):
            store.mutate_invoice_field("inv_enterprise_998", field, "x")


def test_bad_type_is_rejected_and_record_unchanged(tmp_path):
    store = InvoiceStore(db_path=str(tmp_path / "inv2.db"))
    before = store.get_invoice("inv_enterprise_998").amount
    with pytest.raises(ValueError):
        store.mutate_invoice_field("inv_enterprise_998", "amount", "not-a-number")
    assert store.get_invoice("inv_enterprise_998").amount == before


def test_valid_amount_mutation_still_works(tmp_path):
    store = InvoiceStore(db_path=str(tmp_path / "inv3.db"))
    inv = store.mutate_invoice_field("inv_enterprise_998", "amount", "1234.5")
    assert inv.amount == 1234.5 and inv.status == "MUTATED" and len(inv.mutations) == 1
