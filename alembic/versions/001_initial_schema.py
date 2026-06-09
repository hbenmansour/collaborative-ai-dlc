"""initial schema - all domain models

Revision ID: 001
Revises:
Create Date: 2026-06-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Configuration context
    op.create_table(
        "currencies",
        sa.Column("code", sa.String(3), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("exchange_rate_to_usd", sa.Numeric(18, 8), nullable=False, server_default="1.0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "countries",
        sa.Column("code", sa.String(3), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("currency_code", sa.String(3), sa.ForeignKey("currencies.code"), nullable=False),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "tax_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_code", sa.String(3), sa.ForeignKey("countries.code"), nullable=False),
        sa.Column("tax_type", sa.String(20), nullable=False),
        sa.Column("rate", sa.Numeric(8, 5), nullable=False),
        sa.Column("description", sa.String(300)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Customer context
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(300), nullable=False, index=True),
        sa.Column("email", sa.String(254)),
        sa.Column("phone", sa.String(50)),
        sa.Column("address", sa.Text()),
        sa.Column("country_code", sa.String(3), sa.ForeignKey("countries.code"), nullable=False),
        sa.Column("tax_id", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "kyc_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doc_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("file_reference", sa.String(500)),
        sa.Column("expiry_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Contract context
    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_number", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("lease_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("country_code", sa.String(3), sa.ForeignKey("countries.code"), nullable=False),
        sa.Column("asset_description", sa.Text()),
        sa.Column("asset_value", sa.Numeric(18, 2)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "contract_terms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("duration_months", sa.Numeric(5, 0), nullable=False),
        sa.Column("payment_frequency", sa.String(20), nullable=False, server_default="monthly"),
        sa.Column("interest_rate", sa.Numeric(8, 5), nullable=False),
        sa.Column("residual_value", sa.Numeric(18, 2), server_default="0"),
        sa.Column("down_payment", sa.Numeric(18, 2), server_default="0"),
        sa.Column("currency_code", sa.String(3), sa.ForeignKey("currencies.code"), nullable=False),
    )

    op.create_table(
        "amendments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("changes", sa.Text(), nullable=False),
        sa.Column("previous_terms_snapshot", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "contract_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_code", sa.String(3), sa.ForeignKey("countries.code"), nullable=False),
        sa.Column("lease_type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("template_config", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Billing context
    op.create_table(
        "payment_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("total_installments", sa.Integer(), nullable=False),
        sa.Column("currency_code", sa.String(3), sa.ForeignKey("currencies.code"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "installments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("schedule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("payment_schedules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("installment_number", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("principal", sa.Numeric(18, 2), nullable=False),
        sa.Column("interest", sa.Numeric(18, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("paid_date", sa.Date()),
    )


def downgrade() -> None:
    op.drop_table("installments")
    op.drop_table("payment_schedules")
    op.drop_table("contract_templates")
    op.drop_table("amendments")
    op.drop_table("contract_terms")
    op.drop_table("contracts")
    op.drop_table("kyc_documents")
    op.drop_table("customers")
    op.drop_table("tax_rules")
    op.drop_table("countries")
    op.drop_table("currencies")
