"""initial

Revision ID: 6b880abb4c9a
Revises: ccd7fc2ab3f6
Create Date: 2026-03-22 00:11:32.379626

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import FetchedValue

# revision identifiers, used by Alembic.
revision = '6b880abb4c9a'
down_revision = 'ccd7fc2ab3f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('local_sync_queue_202401', schema=None) as batch_op:
       op.execute('DROP INDEX IF EXISTS local_sync_queue_202401_contractor_id_sync_status_created_a_idx')
       op.execute('DROP INDEX IF EXISTS local_sync_queue_202401_sync_status_next_attempt_at_priorit_idx')

       op.execute('DROP TABLE IF EXISTS local_sync_queue_202401')
       op.execute('DROP INDEX IF EXISTS vendor_sync_queue_202402_entity_type_vendor_entity_id_idx')
       op.execute('DROP INDEX IF EXISTS vendor_sync_queue_202402_vendor_id_sync_status_next_attempt_idx')

       op.execute('DROP TABLE IF EXISTS vendor_sync_queue_202402')

       op.execute('DROP INDEX IF EXISTS audit_log_202401_contractor_id_changed_at_idx')

       op.execute('DROP INDEX IF EXISTS audit_log_202401_table_name_record_id_changed_at_idx')

       op.execute('DROP TABLE IF EXISTS audit_log_202401')

       op.execute('DROP INDEX IF EXISTS vendor_sync_queue_202401_entity_type_vendor_entity_id_idx')

       op.execute('DROP INDEX IF EXISTS vendor_sync_queue_202401_vendor_id_sync_status_next_attempt_idx')

       op.execute('DROP TABLE IF EXISTS vendor_sync_queue_202401')
       op.execute('CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_log (session_id)')

       op.execute('CREATE INDEX IF NOT EXISTS idx_biometric_verifications_location ON biometric_verifications USING gist (location)')

    with op.batch_alter_table('contractor_credentials', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('contractor_devices', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.execute('ALTER TABLE contractor_devices DROP CONSTRAINT IF EXISTS contractor_devices_contractor_id_device_id_key')
    with op.batch_alter_table('contractor_devices', schema=None) as batch_op:
       op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_constraint
              WHERE conname = 'unique_contractor_device'
       ) THEN
              ALTER TABLE contractor_devices ADD CONSTRAINT unique_contractor_device UNIQUE (contractor_id, device_id);
       END IF;
END$$;
''')

    with op.batch_alter_table('contractor_insurance', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM information_schema.columns 
              WHERE table_name='contractor_sessions' AND column_name='session_duration_minutes'
       ) THEN
              ALTER TABLE contractor_sessions ADD COLUMN session_duration_minutes INTEGER;
       END IF;
END$$;
''')
    with op.batch_alter_table('contractor_sessions', schema=None) as batch_op:
        batch_op.alter_column('created_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_sessions_job' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_sessions_job ON contractor_sessions (job_id);
       END IF;
END$$;
''')
    with op.batch_alter_table('contractor_sessions', schema=None) as batch_op:
       op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_sessions_visit' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_sessions_visit ON contractor_sessions (visit_id);
       END IF;
END$$;
''')

    with op.batch_alter_table('contractors', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_index('idx_contractors_email')
        batch_op.create_index('idx_contractors_email', ['email'], unique=True, postgresql_where=sa.text('deleted_at IS NULL'))

    op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM information_schema.columns 
              WHERE table_name='issues' AND column_name='assigned_contractor_id'
       ) THEN
              ALTER TABLE issues ADD COLUMN assigned_contractor_id UUID;
       END IF;
END$$;
''')
    with op.batch_alter_table('issues', schema=None) as batch_op:
        batch_op.alter_column('contractor_id',
                        existing_type=sa.UUID(),
                        nullable=True)
        batch_op.alter_column('created_at',
                        existing_type=postgresql.TIMESTAMP(timezone=True),
                        nullable=False,
                        existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
                        existing_type=postgresql.TIMESTAMP(timezone=True),
                        nullable=False,
                        existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_issues_assigned' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_issues_assigned ON issues (assigned_contractor_id);
       END IF;
END$$;
''')
    batch_op.create_index('idx_issues_biometric', ['issue_reported_biometric_id'], unique=False)
    batch_op.create_index('idx_issues_contractor', ['contractor_id'], unique=False)
    batch_op.create_index('idx_issues_issue_reported_location', ['issue_reported_location'], unique=False, postgresql_using='gist')
    batch_op.create_index('idx_issues_reporter', ['issue_reported_by_id'], unique=False)
    batch_op.create_index('idx_issues_task', ['task_id'], unique=False)
    batch_op.create_index('idx_issues_visit', ['visit_id'], unique=False)
    batch_op.drop_constraint('issues_contractor_id_fkey', type_='foreignkey')
    batch_op.create_foreign_key(None, 'contractors', ['assigned_contractor_id'], ['contractor_id'])
    batch_op.create_foreign_key(None, 'contractors', ['contractor_id'], ['contractor_id'])

    with op.batch_alter_table('job_assignments', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('job_completions', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('''
DO $$
BEGIN
       IF EXISTS (
              SELECT 1 FROM pg_constraint WHERE conname = 'job_completions_job_id_contractor_id_key'
       ) THEN
              ALTER TABLE job_completions DROP CONSTRAINT job_completions_job_id_contractor_id_key;
       END IF;
END$$;
''')
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_completions_biometric' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_completions_biometric ON job_completions (job_completed_biometric_id);
       END IF;
END$$;
''')
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_completions_contractor' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_completions_contractor ON job_completions (contractor_id);
       END IF;
END$$;
''')
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_job_completions_job_completed_location' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_job_completions_job_completed_location ON job_completions USING gist (job_completed_location);
       END IF;
END$$;
''')
        batch_op.create_unique_constraint(None, ['job_id'])

    with op.batch_alter_table('job_responses', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('''
DO $$
BEGIN
       IF EXISTS (
              SELECT 1 FROM pg_constraint WHERE conname = 'job_responses_job_id_contractor_id_key'
       ) THEN
              ALTER TABLE job_responses DROP CONSTRAINT job_responses_job_id_contractor_id_key;
       END IF;
END$$;
''')
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_job_responses_job_accepted_location' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_job_responses_job_accepted_location ON job_responses USING gist (job_accepted_location);
       END IF;
END$$;
''')
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_responses_biometric' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_responses_biometric ON job_responses (job_accepted_biometric_id);
       END IF;
END$$;
''')
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_constraint WHERE conname = 'unique_job_contractor_response'
       ) THEN
              ALTER TABLE job_responses ADD CONSTRAINT unique_job_contractor_response UNIQUE (job_id, contractor_id);
       END IF;
END$$;
''')

    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM pg_class WHERE relname = 'idx_jobs_job_location_geography' AND relkind = 'i'
       ) THEN
              CREATE INDEX idx_jobs_job_location_geography ON jobs USING gist (job_location_geography);
       END IF;
END$$;
''')

    with op.batch_alter_table('local_sync_queue', schema=None) as batch_op:
        op.execute('''
DO $$
BEGIN
       IF NOT EXISTS (
              SELECT 1 FROM information_schema.columns 
              WHERE table_name='local_sync_queue' AND column_name='updated_at'
       ) THEN
              ALTER TABLE local_sync_queue ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL;
       END IF;
END$$;
''')
        op.execute('CREATE INDEX IF NOT EXISTS idx_local_sync_session ON local_sync_queue (session_id);')

    with op.batch_alter_table('notification_preferences', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('photos', schema=None) as batch_op:
       op.execute('CREATE INDEX IF NOT EXISTS idx_photos_biometric ON photos (uploaded_by_biometric_id);')
       op.execute('CREATE INDEX IF NOT EXISTS idx_photos_contractor ON photos (contractor_id);')
       op.execute('CREATE INDEX IF NOT EXISTS idx_photos_issue ON photos (issue_id);')
       op.execute('CREATE INDEX IF NOT EXISTS idx_photos_photo_location ON photos USING gist (photo_location);')
       op.execute('CREATE INDEX IF NOT EXISTS idx_photos_task ON photos (task_id);')
       op.execute('CREATE INDEX IF NOT EXISTS idx_photos_uploaded_by ON photos (uploaded_by_id);')
       op.execute('CREATE INDEX IF NOT EXISTS idx_photos_visit ON photos (visit_id);')

    with op.batch_alter_table('progress_updates', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('CREATE INDEX IF NOT EXISTS idx_progress_contractor ON progress_updates (contractor_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_progress_visit ON progress_updates (visit_id);')
        op.execute('ALTER TABLE progress_updates DROP COLUMN IF EXISTS completion_percentage_before;')
        op.execute('ALTER TABLE progress_updates DROP COLUMN IF EXISTS completion_percentage;')

    with op.batch_alter_table('site_visits', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('CREATE INDEX IF NOT EXISTS idx_site_visits_check_in_location ON site_visits USING gist (check_in_location);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_site_visits_check_out_location ON site_visits USING gist (check_out_location);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_visits_checkin_bio ON site_visits (check_in_biometric_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_visits_checkout_bio ON site_visits (check_out_biometric_id);')

    with op.batch_alter_table('submissions', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('CREATE INDEX IF NOT EXISTS idx_submissions_biometric ON submissions (submitted_biometric_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_submissions_completion ON submissions (completion_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_submissions_contractor ON submissions (contractor_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_submissions_previous ON submissions (previous_submission_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_submissions_submitted_by ON submissions (submitted_by_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_submissions_submitted_location ON submissions USING gist (submitted_location);')

    with op.batch_alter_table('task_executions', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('CREATE INDEX IF NOT EXISTS idx_executions_biometric ON task_executions (task_completed_biometric_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_executions_contractor ON task_executions (contractor_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_executions_job ON task_executions (job_id);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_executions_visit ON task_executions (visit_id);')

    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks (assigned_to);')
        op.execute('CREATE INDEX IF NOT EXISTS idx_tasks_parent ON tasks (parent_task_id);')

    with op.batch_alter_table('vendor_sync_queue', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('vendors', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vendors', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('vendor_sync_queue', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_index('idx_tasks_parent')
        batch_op.drop_index('idx_tasks_assigned')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('task_executions', schema=None) as batch_op:
        batch_op.drop_index('idx_executions_visit')
        batch_op.drop_index('idx_executions_job')
        batch_op.drop_index('idx_executions_contractor')
        batch_op.drop_index('idx_executions_biometric')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('submissions', schema=None) as batch_op:
        batch_op.drop_index('idx_submissions_submitted_location', postgresql_using='gist')
        batch_op.drop_index('idx_submissions_submitted_by')
        batch_op.drop_index('idx_submissions_previous')
        batch_op.drop_index('idx_submissions_contractor')
        batch_op.drop_index('idx_submissions_completion')
        batch_op.drop_index('idx_submissions_biometric')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('site_visits', schema=None) as batch_op:
        batch_op.drop_index('idx_visits_checkout_bio')
        batch_op.drop_index('idx_visits_checkin_bio')
        batch_op.drop_index('idx_site_visits_check_out_location', postgresql_using='gist')
        batch_op.drop_index('idx_site_visits_check_in_location', postgresql_using='gist')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('progress_updates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completion_percentage', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('completion_percentage_before', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_index('idx_progress_visit')
        batch_op.drop_index('idx_progress_contractor')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('photos', schema=None) as batch_op:
        batch_op.drop_index('idx_photos_visit')
        batch_op.drop_index('idx_photos_uploaded_by')
        batch_op.drop_index('idx_photos_task')
        batch_op.drop_index('idx_photos_photo_location', postgresql_using='gist')
        batch_op.drop_index('idx_photos_issue')
        batch_op.drop_index('idx_photos_contractor')
        batch_op.drop_index('idx_photos_biometric')

    with op.batch_alter_table('notification_preferences', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('local_sync_queue', schema=None) as batch_op:
        batch_op.drop_index('idx_local_sync_session')
        batch_op.drop_column('updated_at')

    with op.batch_alter_table('jobs', schema=None) as batch_op:
        batch_op.drop_index('idx_jobs_job_location_geography', postgresql_using='gist')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('job_responses', schema=None) as batch_op:
        batch_op.drop_constraint('unique_job_contractor_response', type_='unique')
        batch_op.drop_index('idx_responses_biometric')
        batch_op.drop_index('idx_job_responses_job_accepted_location', postgresql_using='gist')
        batch_op.create_unique_constraint('job_responses_job_id_contractor_id_key', ['job_id', 'contractor_id'])
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('job_completions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_index('idx_job_completions_job_completed_location', postgresql_using='gist')
        batch_op.drop_index('idx_completions_contractor')
        batch_op.drop_index('idx_completions_biometric')
        batch_op.create_unique_constraint('job_completions_job_id_contractor_id_key', ['job_id', 'contractor_id'])
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('job_assignments', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('issues', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('issues_contractor_id_fkey', 'contractors', ['contractor_id'], ['contractor_id'], ondelete='CASCADE')
        batch_op.drop_index('idx_issues_visit')
        batch_op.drop_index('idx_issues_task')
        batch_op.drop_index('idx_issues_reporter')
        batch_op.drop_index('idx_issues_issue_reported_location', postgresql_using='gist')
        batch_op.drop_index('idx_issues_contractor')
        batch_op.drop_index('idx_issues_biometric')
        batch_op.drop_index('idx_issues_assigned')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('contractor_id',
               existing_type=sa.UUID(),
               nullable=False)
        batch_op.drop_column('assigned_contractor_id')

    with op.batch_alter_table('contractors', schema=None) as batch_op:
        batch_op.drop_index('idx_contractors_email', postgresql_where=sa.text('deleted_at IS NULL'))
        batch_op.create_index('idx_contractors_email', ['email'], unique=False)
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('contractor_sessions', schema=None) as batch_op:
        batch_op.drop_index('idx_sessions_visit')
        batch_op.drop_index('idx_sessions_job')
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.drop_column('session_duration_minutes')

    with op.batch_alter_table('contractor_insurance', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('contractor_devices', schema=None) as batch_op:
        batch_op.drop_constraint('unique_contractor_device', type_='unique')
        batch_op.create_unique_constraint('contractor_devices_contractor_id_device_id_key', ['contractor_id', 'device_id'])
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('contractor_credentials', schema=None) as batch_op:
        batch_op.alter_column('updated_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(timezone=True),
               nullable=True,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))

    with op.batch_alter_table('biometric_verifications', schema=None) as batch_op:
        batch_op.drop_index('idx_biometric_verifications_location', postgresql_using='gist')

    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.drop_index('idx_audit_session')

    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.CheckConstraint('srid > 0 AND srid <= 998999', name='spatial_ref_sys_srid_check'),
    sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )
    op.create_table('vendor_sync_queue_202401',
    sa.Column('sync_id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=False),
    sa.Column('vendor_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('direction', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('entity_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('entity_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('vendor_entity_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('transformed_payload', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('sync_status', postgresql.ENUM('pending', 'synced', 'failed', 'ignored', name='vendor_sync_status'), server_default=sa.text("'pending'::vendor_sync_status"), autoincrement=False, nullable=True),
    sa.Column('attempts', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.Column('last_attempt_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('next_attempt_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('error_message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.Column('processed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.CheckConstraint("direction::text = ANY (ARRAY['inbound'::character varying, 'outbound'::character varying]::text[])", name='vendor_sync_queue_direction_check'),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.vendor_id'], name='vendor_sync_queue_vendor_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('sync_id', 'created_at', name='vendor_sync_queue_202401_pkey')
    )
    with op.batch_alter_table('vendor_sync_queue_202401', schema=None) as batch_op:
        batch_op.create_index('vendor_sync_queue_202401_vendor_id_sync_status_next_attempt_idx', ['vendor_id', 'sync_status', 'next_attempt_at'], unique=False)
        batch_op.create_index('vendor_sync_queue_202401_entity_type_vendor_entity_id_idx', ['entity_type', 'vendor_entity_id'], unique=False)

    op.create_table('audit_log_202401',
    sa.Column('audit_id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), autoincrement=False, nullable=False),
    sa.Column('changed_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=False),
    sa.Column('table_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('record_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('action', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('contractor_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('session_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('ip_address', postgresql.INET(), autoincrement=False, nullable=True),
    sa.Column('old_data', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('new_data', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('changed_fields', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.CheckConstraint("action::text = ANY (ARRAY['INSERT'::character varying, 'UPDATE'::character varying, 'DELETE'::character varying]::text[])", name='audit_log_action_check'),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractors.contractor_id'], name='audit_log_contractor_id_fkey', ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['session_id'], ['contractor_sessions.session_id'], name='audit_log_session_id_fkey', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('audit_id', 'changed_at', name='audit_log_202401_pkey')
    )
    with op.batch_alter_table('audit_log_202401', schema=None) as batch_op:
        batch_op.create_index('audit_log_202401_table_name_record_id_changed_at_idx', ['table_name', 'record_id', 'changed_at'], unique=False)
        batch_op.create_index('audit_log_202401_contractor_id_changed_at_idx', ['contractor_id', 'changed_at'], unique=False)

    op.create_table('vendor_sync_queue_202402',
    sa.Column('sync_id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=False),
    sa.Column('vendor_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('direction', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('entity_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('entity_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('vendor_entity_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('transformed_payload', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('sync_status', postgresql.ENUM('pending', 'synced', 'failed', 'ignored', name='vendor_sync_status'), server_default=sa.text("'pending'::vendor_sync_status"), autoincrement=False, nullable=True),
    sa.Column('attempts', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.Column('last_attempt_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('next_attempt_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('error_message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.Column('processed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.CheckConstraint("direction::text = ANY (ARRAY['inbound'::character varying, 'outbound'::character varying]::text[])", name='vendor_sync_queue_direction_check'),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.vendor_id'], name='vendor_sync_queue_vendor_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('sync_id', 'created_at', name='vendor_sync_queue_202402_pkey')
    )
    with op.batch_alter_table('vendor_sync_queue_202402', schema=None) as batch_op:
        batch_op.create_index('vendor_sync_queue_202402_vendor_id_sync_status_next_attempt_idx', ['vendor_id', 'sync_status', 'next_attempt_at'], unique=False)
        batch_op.create_index('vendor_sync_queue_202402_entity_type_vendor_entity_id_idx', ['entity_type', 'vendor_entity_id'], unique=False)

    op.create_table('local_sync_queue_202401',
    sa.Column('sync_item_id', sa.UUID(), server_default=sa.text('uuid_generate_v4()'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=False),
    sa.Column('contractor_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('device_id', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('session_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.Column('table_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('record_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('operation', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('sync_status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', 'conflict', name='sync_status'), server_default=sa.text("'pending'::sync_status"), autoincrement=False, nullable=True),
    sa.Column('sync_attempts', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.Column('last_attempt_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('next_attempt_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('error_message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('priority', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.CheckConstraint("operation::text = ANY (ARRAY['INSERT'::character varying, 'UPDATE'::character varying, 'DELETE'::character varying]::text[])", name='local_sync_queue_operation_check'),
    sa.CheckConstraint('priority >= 0', name='local_sync_queue_priority_check'),
    sa.CheckConstraint('sync_attempts >= 0', name='local_sync_queue_sync_attempts_check'),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractors.contractor_id'], name='local_sync_queue_contractor_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['contractor_sessions.session_id'], name='local_sync_queue_session_id_fkey', ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('sync_item_id', 'created_at', name='local_sync_queue_202401_pkey')
    )
    with op.batch_alter_table('local_sync_queue_202401', schema=None) as batch_op:
        batch_op.create_index('local_sync_queue_202401_sync_status_next_attempt_at_priorit_idx', ['sync_status', 'next_attempt_at', 'priority'], unique=False)
        batch_op.create_index('local_sync_queue_202401_contractor_id_sync_status_created_a_idx', ['contractor_id', 'sync_status', 'created_at'], unique=False)

    # ### end Alembic commands ###
