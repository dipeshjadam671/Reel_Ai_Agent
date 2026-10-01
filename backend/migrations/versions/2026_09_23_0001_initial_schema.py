"""initial_schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-09-23 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Users & Workspaces
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False, unique=True),
        sa.Column('monthly_budget_usd', sa.Float(), nullable=False, default=50.0),
        sa.Column('current_spend_usd', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_workspaces_slug', 'workspaces', ['slug'])

    op.create_table(
        'workspace_members',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, default='editor'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Tasks
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('topic', sa.String(length=500), nullable=False),
        sa.Column('seed_script', sa.String(length=5000), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, default='en'),
        sa.Column('target_platforms', sa.JSON(), nullable=False),
        sa.Column('presenter_config', sa.JSON(), nullable=False),
        sa.Column('schedule_config', sa.JSON(), nullable=False),
        sa.Column('brand_preferences', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_tasks_workspace_id', 'tasks', ['workspace_id'])

    # Cycles
    op.create_table(
        'cycles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_id', sa.String(length=36), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('thread_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='created'),
        sa.Column('current_agent', sa.String(length=100), nullable=True),
        sa.Column('novelty_score', sa.Float(), nullable=True),
        sa.Column('estimated_cost_usd', sa.Float(), nullable=False, default=0.0),
        sa.Column('actual_cost_usd', sa.Float(), nullable=False, default=0.0),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_cycles_workspace_id', 'cycles', ['workspace_id'])
    op.create_index('ix_cycles_task_id', 'cycles', ['task_id'])
    op.create_index('ix_cycles_status', 'cycles', ['status'])

    # Sources
    op.create_table(
        'sources',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('claims', sa.JSON(), nullable=False),
        sa.Column('credibility_score', sa.Float(), nullable=False, default=1.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Scripts
    op.create_table(
        'scripts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('hook', sa.Text(), nullable=False),
        sa.Column('raw_content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, default='en'),
        sa.Column('scenes', sa.JSON(), nullable=False),
        sa.Column('claims', sa.JSON(), nullable=False),
        sa.Column('call_to_action', sa.String(length=500), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Assets
    op.create_table(
        'assets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('storage_url', sa.String(length=2048), nullable=False),
        sa.Column('license_type', sa.String(length=100), nullable=False),
        sa.Column('license_url', sa.String(length=2048), nullable=True),
        sa.Column('attribution_text', sa.String(length=500), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Renders
    op.create_table(
        'renders',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('video_url', sa.String(length=2048), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=2048), nullable=True),
        sa.Column('captions_url', sa.String(length=2048), nullable=True),
        sa.Column('resolution', sa.String(length=20), nullable=False, default='1080x1920'),
        sa.Column('aspect_ratio', sa.String(length=10), nullable=False, default='9:16'),
        sa.Column('duration_seconds', sa.Float(), nullable=False, default=0.0),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, default=0),
        sa.Column('render_time_seconds', sa.Float(), nullable=False, default=0.0),
        sa.Column('c2pa_manifest_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Approvals
    op.create_table(
        'approvals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Publications
    op.create_table(
        'publications',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('platform_post_id', sa.String(length=255), nullable=True),
        sa.Column('permalink', sa.String(length=2048), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata_payload', sa.JSON(), nullable=False),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Post Metrics
    op.create_table(
        'post_metrics',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('publication_id', sa.String(length=36), sa.ForeignKey('publications.id', ondelete='CASCADE'), nullable=False),
        sa.Column('views', sa.Integer(), nullable=False, default=0),
        sa.Column('likes', sa.Integer(), nullable=False, default=0),
        sa.Column('shares', sa.Integer(), nullable=False, default=0),
        sa.Column('comments', sa.Integer(), nullable=False, default=0),
        sa.Column('retention_rate_pct', sa.Float(), nullable=False, default=0.0),
        sa.Column('watch_time_seconds', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Task Preferences
    op.create_table(
        'task_preferences',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('task_id', sa.String(length=36), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tone_of_voice', sa.String(length=100), nullable=False, default='informative_engaging'),
        sa.Column('content_rules', sa.JSON(), nullable=False),
        sa.Column('prohibited_keywords', sa.JSON(), nullable=False),
        sa.Column('compliance_overrides', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Spend Ledger
    op.create_table(
        'spend_ledger',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('operation', sa.String(length=100), nullable=False),
        sa.Column('units', sa.Float(), nullable=False, default=1.0),
        sa.Column('unit_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, default='USD'),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Audit Log
    op.create_table(
        'audit_log',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # RAG Chunks
    op.create_table(
        'doc_chunks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('source_url', sa.String(length=2048), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('chunk_metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'script_chunks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workspace_id', sa.String(length=36), nullable=False),
        sa.Column('cycle_id', sa.String(length=36), sa.ForeignKey('cycles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(length=500), nullable=False),
        sa.Column('hook', sa.Text(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('claims', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('script_chunks')
    op.drop_table('doc_chunks')
    op.drop_table('audit_log')
    op.drop_table('spend_ledger')
    op.drop_table('task_preferences')
    op.drop_table('post_metrics')
    op.drop_table('publications')
    op.drop_table('approvals')
    op.drop_table('renders')
    op.drop_table('assets')
    op.drop_table('scripts')
    op.drop_table('sources')
    op.drop_table('cycles')
    op.drop_table('tasks')
    op.drop_table('workspace_members')
    op.drop_table('workspaces')
    op.drop_table('users')
