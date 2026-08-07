"""Add tax_debt_fetched_at column to track when tax debt data was last fetched.

The column stores the timestamp of the last successful SFS fetch.
NULL means data has never been fetched.
"""

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    import sqlalchemy as sa

    op.add_column(
        "companies",
        sa.Column("tax_debt_fetched_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_companies_tax_debt_fetched_at",
        "companies",
        ["tax_debt_fetched_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_companies_tax_debt_fetched_at", table_name="companies")
    op.drop_column("companies", "tax_debt_fetched_at")
