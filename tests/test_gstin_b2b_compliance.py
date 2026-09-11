import uuid
import pytest
from backend.app.b2b.invoice_store import InvoiceStore, InvoiceRecord

def test_gstin_statutory_validation():
    # Valid Indian GSTINs (State 29 = Karnataka, 36 = Telangana, 27 = Maharashtra)
    assert InvoiceStore.validate_gstin_format("29AABCU9603R1Z2") is True
    assert InvoiceStore.validate_gstin_format("36AAACB9876Q1Z1") is True
    assert InvoiceStore.validate_gstin_format("27AABCN1234F1Z8") is True
    assert InvoiceStore.validate_gstin_format("UNREGISTERED") is True

    # Invalid GSTINs
    assert InvoiceStore.validate_gstin_format("INVALID_GSTIN") is False
    assert InvoiceStore.validate_gstin_format("1234567890") is False
    assert InvoiceStore.validate_gstin_format("99AABCU9603R1Z2") is False  # State code 99 is invalid
    assert InvoiceStore.validate_gstin_format("00AABCU9603R1Z2") is False  # State code 00 is invalid
    assert InvoiceStore.validate_gstin_format("29AABCU9603R1Z") is False   # 14 chars, too short

def test_invoice_store_persistence_and_mutation(tmp_path):
    db_file = str(tmp_path / f"test_inv_{uuid.uuid4().hex[:8]}.db")
    store = InvoiceStore(db_path=db_file)

    inv = store.get_invoice("inv_enterprise_998")
    assert inv is not None
    assert inv.customer_name == "Acme Pvt Ltd"

    # Mutate to valid GSTIN
    updated = store.mutate_invoice_field(
        invoice_id="inv_enterprise_998",
        field="gstin",
        new_value="29AABCU9603R1Z2",
        reason="Customer updated GSTIN during audit"
    )
    assert updated.gstin == "29AABCU9603R1Z2"
    assert updated.status == "MUTATED"

    # Attempt mutation to invalid GSTIN -> must raise ValueError
    with pytest.raises(ValueError, match="Statutory Validation Failed"):
        store.mutate_invoice_field(
            invoice_id="inv_enterprise_998",
            field="gstin",
            new_value="GARBAGE_GST_123"
        )

    # Re-instantiate store from same DB -> verify persistence
    fresh_store = InvoiceStore(db_path=db_file)
    persisted_inv = fresh_store.get_invoice("inv_enterprise_998")
    assert persisted_inv is not None
    assert persisted_inv.gstin == "29AABCU9603R1Z2"
    assert persisted_inv.status == "MUTATED"
    assert len(persisted_inv.mutations) >= 1
