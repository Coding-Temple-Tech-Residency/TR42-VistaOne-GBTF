"""initial schema

Revision ID: 58e9278aee5a
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "58e9278aee5a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # -------------------- EXTENSIONS --------------------
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "btree_gin"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # -------------------- CUSTOM DOMAINS --------------------
    op.execute("""
        CREATE DOMAIN phone_number AS VARCHAR(20)
        CHECK (VALUE ~ '^\\+?[0-9\\-\\(\\)\\s]{10,20}$');
    """)
    op.execute("""
        CREATE DOMAIN email_address AS VARCHAR(255)
        CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$');
    """)
    op.execute("""
        CREATE DOMAIN ssn_last_four AS CHAR(4)
        CHECK (VALUE ~ '^[0-9]{4}$');
    """)
    op.execute("""
        CREATE DOMAIN percent_value AS INTEGER
        CHECK (VALUE >= 0 AND VALUE <= 100);
    """)
    op.execute("""
        CREATE DOMAIN rating_value AS DECIMAL(3,2)
        CHECK (VALUE >= 0 AND VALUE <= 5);
    """)
    op.execute("""
        CREATE DOMAIN coordinate AS DECIMAL(10,8)
        CHECK (VALUE >= -180 AND VALUE <= 180);
    """)

    # -------------------- ENUMS --------------------
    op.execute(
        "CREATE TYPE account_status AS ENUM ('active', 'inactive', 'suspended', 'pending');"
    )
    op.execute(
        "CREATE TYPE job_status AS ENUM ('draft', 'scheduled', 'assigned', 'in_progress', 'on_hold', 'completed', 'cancelled');"
    )
    op.execute(
        "CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'urgent');"
    )
    op.execute(
        "CREATE TYPE issue_severity AS ENUM ('low', 'medium', 'high', 'critical', 'blocker');"
    )
    op.execute(
        "CREATE TYPE issue_status AS ENUM ('open', 'in_progress', 'resolved', 'closed', 'wont_fix');"
    )
    op.execute(
        "CREATE TYPE task_status AS ENUM ('pending', 'assigned', 'in_progress', 'completed', 'blocked', 'skipped');"
    )
    op.execute(
        "CREATE TYPE verification_type AS ENUM ('check_in', 'check_out', 'task', 'job_acceptance', 'job_completion', 'delivery', 'issue_report', 'identity_verify');"
    )
    op.execute(
        "CREATE TYPE device_type AS ENUM ('ios', 'android', 'tablet', 'desktop', 'web', 'other');"
    )
    op.execute(
        "CREATE TYPE sync_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'conflict');"
    )
    op.execute(
        "CREATE TYPE credential_type AS ENUM ('license', 'certification', 'training', 'award');"
    )
    op.execute(
        "CREATE TYPE vendor_sync_status AS ENUM ('pending', 'synced', 'failed', 'ignored');"
    )

    # -------------------- TABLES (in dependency order) --------------------
    # vendors
    op.execute("""
        CREATE TABLE vendors (
            vendor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            vendor_code VARCHAR(50) UNIQUE NOT NULL,
            vendor_name VARCHAR(255) NOT NULL,
            vendor_api_config JSONB,
            webhook_url TEXT,
            sync_frequency_minutes INTEGER DEFAULT 60,
            last_sync_at TIMESTAMPTZ,
            last_sync_status vendor_sync_status DEFAULT 'pending',
            sync_error_message TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # contractors
    op.execute("""
        CREATE TABLE contractors (
            contractor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            middle_initial CHAR(1),
            date_of_birth DATE,
            ssn_last_four ssn_last_four,
            email email_address UNIQUE NOT NULL,
            personal_phone phone_number,
            alternate_phone phone_number,
            address_street VARCHAR(255),
            address_city VARCHAR(100),
            address_state VARCHAR(50),
            address_zip VARCHAR(20),
            address_country VARCHAR(100) DEFAULT 'USA',
            profile_photo_url TEXT,
            years_experience INTEGER CHECK (years_experience >= 0),
            previous_projects_count INTEGER DEFAULT 0 CHECK (previous_projects_count >= 0),
            average_rating rating_value,
            total_reviews INTEGER DEFAULT 0 CHECK (total_reviews >= 0),
            background_check_passed BOOLEAN DEFAULT FALSE,
            background_check_date DATE,
            background_check_provider VARCHAR(255),
            background_check_document_url TEXT,
            drug_test_passed BOOLEAN DEFAULT FALSE,
            drug_test_date DATE,
            drug_test_document_url TEXT,
            safety_record_score INTEGER CHECK (safety_record_score >= 0 AND safety_record_score <= 100),
            account_status account_status DEFAULT 'active',
            account_verified BOOLEAN DEFAULT FALSE,
            account_verified_at TIMESTAMPTZ,
            last_login_at TIMESTAMPTZ,
            language_preference VARCHAR(50) DEFAULT 'en',
            work_hours_preference JSONB,
            preferred_job_types JSONB,
            max_travel_distance_miles INTEGER CHECK (max_travel_distance_miles >= 0),
            search_vector TSVECTOR GENERATED ALWAYS AS (
                to_tsvector('english',
                    coalesce(first_name, '') || ' ' ||
                    coalesce(last_name, '') || ' ' ||
                    coalesce(email, '') || ' ' ||
                    coalesce(address_city, '')
                )
            ) STORED,
            deleted_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # contractor_credentials
    op.execute("""
        CREATE TABLE contractor_credentials (
            credential_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            credential_type credential_type NOT NULL,
            credential_name VARCHAR(255) NOT NULL,
            issuing_organization VARCHAR(255),
            credential_number VARCHAR(100),
            issue_date DATE,
            expiration_date DATE,
            state VARCHAR(50),
            document_url TEXT,
            credential_data JSONB,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT valid_dates CHECK (issue_date <= expiration_date)
        );
    """)

    # contractor_insurance
    op.execute("""
        CREATE TABLE contractor_insurance (
            insurance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            insurance_type VARCHAR(50) NOT NULL CHECK (insurance_type IN ('general_liability', 'workers_comp', 'auto', 'professional', 'tools')),
            policy_number VARCHAR(100) NOT NULL,
            provider_name VARCHAR(255),
            provider_phone phone_number,
            coverage_amount DECIMAL(12,2) CHECK (coverage_amount >= 0),
            deductible DECIMAL(12,2) CHECK (deductible >= 0),
            effective_date DATE,
            expiration_date DATE,
            insurance_document_url TEXT,
            additional_insured_required BOOLEAN DEFAULT FALSE,
            additional_insured_certificate_url TEXT,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            CHECK (effective_date <= expiration_date)
        );
    """)

    # contractor_devices
    op.execute("""
        CREATE TABLE contractor_devices (
            device_registration_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            device_id VARCHAR(255) NOT NULL,
            device_name VARCHAR(255),
            device_type device_type,
            device_model VARCHAR(100),
            os_version VARCHAR(50),
            app_version VARCHAR(50),
            first_registered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMPTZ,
            biometric_enabled_on_device BOOLEAN DEFAULT FALSE,
            biometric_type VARCHAR(50) CHECK (biometric_type IN ('fingerprint', 'face_id', 'voice', 'none')),
            push_token VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(contractor_id, device_id)
        );
    """)

    # notification_preferences
    op.execute("""
        CREATE TABLE notification_preferences (
            preference_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            email_notifications BOOLEAN DEFAULT TRUE,
            sms_notifications BOOLEAN DEFAULT FALSE,
            push_notifications BOOLEAN DEFAULT TRUE,
            job_alerts BOOLEAN DEFAULT TRUE,
            job_alerts_radius_miles INTEGER CHECK (job_alerts_radius_miles >= 0),
            job_alerts_types JSONB,
            payment_notifications BOOLEAN DEFAULT TRUE,
            schedule_notifications BOOLEAN DEFAULT TRUE,
            issue_notifications BOOLEAN DEFAULT TRUE,
            marketing_notifications BOOLEAN DEFAULT FALSE,
            notification_schedule JSONB,
            quiet_hours_start TIME,
            quiet_hours_end TIME,
            quiet_hours_timezone VARCHAR(50),
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(contractor_id)
        );
    """)

    # jobs
    op.execute("""
        CREATE TABLE jobs (
            job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_number VARCHAR(100) NOT NULL,
            vendor_job_id VARCHAR(255),
            vendor_id UUID REFERENCES vendors(vendor_id),
            job_name VARCHAR(255),
            job_description TEXT,
            job_location TEXT,
            job_location_geography GEOGRAPHY(POINT),
            site_address_street VARCHAR(255),
            site_address_city VARCHAR(100),
            site_address_state VARCHAR(50),
            site_address_zip VARCHAR(20),
            site_contact_name VARCHAR(255),
            site_contact_phone phone_number,
            site_contact_email email_address,
            scheduled_start_date TIMESTAMPTZ,
            scheduled_end_date TIMESTAMPTZ,
            actual_start_date TIMESTAMPTZ,
            actual_end_date TIMESTAMPTZ,
            estimated_hours DECIMAL(5,2) CHECK (estimated_hours > 0),
            job_type VARCHAR(100),
            job_category VARCHAR(100),
            priority priority_level DEFAULT 'medium',
            status job_status DEFAULT 'scheduled',
            vendor_name VARCHAR(255),
            vendor_contact_name VARCHAR(255),
            vendor_contact_phone phone_number,
            vendor_contact_email email_address,
            vendor_instructions TEXT,
            po_number VARCHAR(100),
            quote_number VARCHAR(100),
            contract_number VARCHAR(100),
            documents_attached JSONB,
            materials_needed TEXT,
            special_requirements TEXT,
            safety_requirements TEXT,
            last_synced_with_vendor_at TIMESTAMPTZ,
            vendor_sync_status vendor_sync_status DEFAULT 'pending',
            vendor_data JSONB,
            search_vector TSVECTOR GENERATED ALWAYS AS (
                to_tsvector('english',
                    coalesce(job_number, '') || ' ' ||
                    coalesce(job_name, '') || ' ' ||
                    coalesce(job_description, '') || ' ' ||
                    coalesce(site_address_city, '') || ' ' ||
                    coalesce(site_address_state, '')
                )
            ) STORED,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMPTZ,
            CONSTRAINT valid_job_dates CHECK (
                scheduled_start_date <= scheduled_end_date AND
                (actual_start_date IS NULL OR actual_start_date <= actual_end_date)
            )
        );
    """)

    # job_assignments
    op.execute("""
        CREATE TABLE job_assignments (
            assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            assigned_role VARCHAR(100),
            is_primary BOOLEAN DEFAULT FALSE,
            assignment_status VARCHAR(50) DEFAULT 'active' CHECK (assignment_status IN ('active', 'completed', 'removed')),
            unassigned_at TIMESTAMPTZ,
            unassigned_reason TEXT,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # biometric_verifications
    op.execute("""
        CREATE TABLE biometric_verifications (
            biometric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            job_id UUID REFERENCES jobs(job_id) ON DELETE SET NULL,
            verification_type verification_type NOT NULL,
            verification_status VARCHAR(20) DEFAULT 'success' CHECK (verification_status IN ('success', 'failed', 'timeout', 'canceled')),
            biometric_type VARCHAR(50) CHECK (biometric_type IN ('fingerprint', 'face_id', 'voice', 'iris', 'multi_factor')),
            biometric_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            biometric_confidence_score INTEGER CHECK (biometric_confidence_score >= 0 AND biometric_confidence_score <= 100),
            biometric_device_id VARCHAR(255),
            biometric_method_used VARCHAR(100),
            biometric_failed_attempts INTEGER DEFAULT 0,
            biometric_error_message TEXT,
            biometric_image_hash VARCHAR(255),
            biometric_template_match BOOLEAN,
            multi_factor_completed BOOLEAN DEFAULT FALSE,
            multi_factor_methods JSONB,
            liveness_detection_passed BOOLEAN DEFAULT FALSE,
            liveness_score INTEGER CHECK (liveness_score >= 0 AND liveness_score <= 100),
            location GEOGRAPHY(POINT),
            ip_address INET,
            verification_duration_ms INTEGER,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # job_responses
    op.execute("""
        CREATE TABLE job_responses (
            response_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            response_type VARCHAR(20) NOT NULL CHECK (response_type IN ('accept', 'decline', 'counter', 'pending')),
            job_accepted BOOLEAN DEFAULT FALSE,
            job_accepted_at TIMESTAMPTZ,
            job_accepted_biometric_verified BOOLEAN DEFAULT FALSE,
            job_accepted_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            job_accepted_location GEOGRAPHY(POINT),
            estimated_arrival_time TIMESTAMPTZ,
            job_declined BOOLEAN DEFAULT FALSE,
            job_declined_reason TEXT,
            job_declined_category VARCHAR(50) CHECK (job_declined_category IN ('schedule', 'distance', 'skills', 'equipment', 'other')),
            job_declined_at TIMESTAMPTZ,
            counter_offer_amount DECIMAL(10,2) CHECK (counter_offer_amount >= 0),
            counter_offer_schedule TIMESTAMPTZ,
            counter_offer_notes TEXT,
            contractor_notes TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            UNIQUE(job_id, contractor_id)
        );
    """)

    # site_visits
    op.execute("""
        CREATE TABLE site_visits (
            visit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            visit_number INTEGER,
            visit_status VARCHAR(50) DEFAULT 'in_progress' CHECK (visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
            visit_type VARCHAR(50) DEFAULT 'regular' CHECK (visit_type IN ('regular', 'emergency', 'inspection', 'delivery_only')),
            check_in_time TIMESTAMPTZ NOT NULL,
            check_in_location GEOGRAPHY(POINT),
            check_in_accuracy_meters DECIMAL(10,2) CHECK (check_in_accuracy_meters >= 0),
            check_in_altitude_meters DECIMAL(10,2),
            check_in_photo_url TEXT,
            check_in_biometric_verified BOOLEAN DEFAULT FALSE,
            check_in_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            check_in_notes TEXT,
            on_site_contact_person VARCHAR(255),
            site_conditions_on_arrival TEXT,
            equipment_brought JSONB,
            check_out_time TIMESTAMPTZ,
            check_out_location GEOGRAPHY(POINT),
            check_out_accuracy_meters DECIMAL(10,2) CHECK (check_out_accuracy_meters >= 0),
            check_out_altitude_meters DECIMAL(10,2),
            check_out_photo_url TEXT,
            check_out_biometric_verified BOOLEAN DEFAULT FALSE,
            check_out_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            check_out_notes TEXT,
            site_conditions_on_departure TEXT,
            equipment_used JSONB,
            equipment_returned JSONB,
            total_hours_on_site DECIMAL(5,2),
            total_break_minutes INTEGER DEFAULT 0 CHECK (total_break_minutes >= 0),
            productive_hours DECIMAL(5,2) CHECK (productive_hours >= 0),
            travel_time_minutes INTEGER CHECK (travel_time_minutes >= 0),
            travel_distance_miles DECIMAL(8,2) CHECK (travel_distance_miles >= 0),
            device_id VARCHAR(255),
            device_model VARCHAR(100),
            app_version VARCHAR(50),
            offline_mode BOOLEAN DEFAULT FALSE,
            data_synced_at TIMESTAMPTZ,
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT valid_check_times CHECK (check_out_time IS NULL OR check_out_time >= check_in_time)
        );
    """)

    # progress_updates
    op.execute("""
        CREATE TABLE progress_updates (
            progress_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            visit_id UUID REFERENCES site_visits(visit_id) ON DELETE SET NULL,
            completion_percentage percent_value NOT NULL,
            completion_percentage_before percent_value,
            completion_percentage_after percent_value GENERATED ALWAYS AS (
                LEAST(completion_percentage_before + completion_percentage, 100)
            ) STORED,
            work_description TEXT NOT NULL,
            tasks_completed INTEGER DEFAULT 0,
            total_tasks INTEGER DEFAULT 0,
            hours_worked DECIMAL(5,2) CHECK (hours_worked >= 0),
            materials_used JSONB,
            materials_delivered JSONB,
            progress_photos JSONB,
            next_steps TEXT,
            blockers TEXT,
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # tasks
    op.execute("""
        CREATE TABLE tasks (
            task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            task_name VARCHAR(255) NOT NULL,
            task_code VARCHAR(50),
            task_description TEXT,
            task_category VARCHAR(100),
            estimated_duration_minutes INTEGER CHECK (estimated_duration_minutes >= 0),
            actual_duration_minutes INTEGER CHECK (actual_duration_minutes >= 0),
            sequence_order INTEGER,
            parent_task_id UUID REFERENCES tasks(task_id),
            dependent_task_ids JSONB,
            is_required BOOLEAN DEFAULT TRUE,
            is_milestone BOOLEAN DEFAULT FALSE,
            assigned_to UUID REFERENCES contractors(contractor_id),
            assigned_at TIMESTAMPTZ,
            task_status task_status DEFAULT 'pending',
            started_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            quality_check_required BOOLEAN DEFAULT FALSE,
            quality_check_passed BOOLEAN,
            quality_check_notes TEXT,
            safety_required BOOLEAN DEFAULT FALSE,
            safety_checklist JSONB,
            safety_verified BOOLEAN DEFAULT FALSE,
            materials_needed JSONB,
            tools_needed JSONB,
            search_vector TSVECTOR GENERATED ALWAYS AS (
                to_tsvector('english',
                    coalesce(task_name, '') || ' ' ||
                    coalesce(task_code, '') || ' ' ||
                    coalesce(task_description, '')
                )
            ) STORED,
            vendor_task_id VARCHAR(255),
            vendor_data JSONB,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT valid_task_dates CHECK (
                (started_at IS NULL OR completed_at IS NULL OR started_at <= completed_at)
            )
        );
    """)

    # task_executions
    op.execute("""
        CREATE TABLE task_executions (
            execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            visit_id UUID REFERENCES site_visits(visit_id) ON DELETE SET NULL,
            execution_status VARCHAR(50) DEFAULT 'pending' CHECK (execution_status IN ('pending', 'started', 'paused', 'completed', 'failed')),
            started_at TIMESTAMPTZ,
            paused_at TIMESTAMPTZ,
            resumed_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            task_completed BOOLEAN DEFAULT FALSE,
            task_completed_at TIMESTAMPTZ,
            task_completed_biometric BOOLEAN DEFAULT FALSE,
            task_completed_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            task_duration_minutes INTEGER CHECK (task_duration_minutes >= 0),
            task_quantity_completed DECIMAL(10,2) CHECK (task_quantity_completed >= 0),
            task_unit_of_measure VARCHAR(20),
            task_quality_rating INTEGER CHECK (task_quality_rating >= 1 AND task_quality_rating <= 5),
            task_quality_notes TEXT,
            issues_encountered BOOLEAN DEFAULT FALSE,
            issue_ids JSONB,
            task_notes TEXT,
            contractor_notes TEXT,
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT valid_execution_times CHECK (
                (started_at IS NULL OR completed_at IS NULL OR started_at <= completed_at) AND
                (paused_at IS NULL OR resumed_at IS NULL OR paused_at <= resumed_at)
            )
        );
    """)

    # issues
    op.execute("""
        CREATE TABLE issues (
            issue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            visit_id UUID REFERENCES site_visits(visit_id) ON DELETE SET NULL,
            task_id UUID REFERENCES tasks(task_id) ON DELETE SET NULL,
            issue_number VARCHAR(50) UNIQUE,
            issue_title VARCHAR(255) NOT NULL,
            issue_description TEXT,
            issue_category VARCHAR(50) CHECK (issue_category IN ('safety', 'quality', 'delay', 'equipment', 'material', 'site', 'personnel', 'design', 'other')),
            issue_subcategory VARCHAR(50),
            issue_severity issue_severity DEFAULT 'medium',
            issue_priority INTEGER CHECK (issue_priority >= 1 AND issue_priority <= 5),
            issue_reported_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            issue_reported_by_id UUID REFERENCES contractors(contractor_id),
            issue_reported_biometric BOOLEAN DEFAULT FALSE,
            issue_reported_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            issue_reported_location GEOGRAPHY(POINT),
            issue_photos JSONB,
            issue_status issue_status DEFAULT 'open',
            issue_status_updated_at TIMESTAMPTZ,
            issue_resolved BOOLEAN DEFAULT FALSE,
            issue_resolved_at TIMESTAMPTZ,
            issue_resolution_notes TEXT,
            issue_resolution_photos JSONB,
            impact_on_schedule_minutes INTEGER,
            impact_on_cost DECIMAL(10,2),
            impact_description TEXT,
            root_cause_category VARCHAR(50),
            root_cause_description TEXT,
            preventive_actions TEXT,
            search_vector TSVECTOR GENERATED ALWAYS AS (
                to_tsvector('english',
                    coalesce(issue_number, '') || ' ' ||
                    coalesce(issue_title, '') || ' ' ||
                    coalesce(issue_description, '')
                )
            ) STORED,
            vendor_issue_id VARCHAR(255),
            vendor_data JSONB,
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # photos
    op.execute("""
        CREATE TABLE photos (
            photo_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            visit_id UUID REFERENCES site_visits(visit_id) ON DELETE SET NULL,
            task_id UUID REFERENCES tasks(task_id) ON DELETE SET NULL,
            issue_id UUID REFERENCES issues(issue_id) ON DELETE SET NULL,
            photo_url TEXT NOT NULL,
            photo_thumbnail_url TEXT,
            photo_filename VARCHAR(255),
            photo_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            photo_location GEOGRAPHY(POINT),
            photo_direction_degrees INTEGER CHECK (photo_direction_degrees >= 0 AND photo_direction_degrees < 360),
            photo_category VARCHAR(50) CHECK (photo_category IN ('before', 'during', 'after', 'issue', 'progress', 'delivery', 'safety', 'signature', 'general')),
            photo_tags JSONB,
            photo_description TEXT,
            uploaded_by_id UUID REFERENCES contractors(contractor_id),
            uploaded_by_biometric BOOLEAN DEFAULT FALSE,
            uploaded_by_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            uploaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            photo_size_bytes BIGINT CHECK (photo_size_bytes >= 0),
            photo_metadata JSONB,
            ai_processed BOOLEAN DEFAULT FALSE,
            ai_analysis JSONB,
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            vendor_photo_url TEXT,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # job_completions
    op.execute("""
        CREATE TABLE job_completions (
            completion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            job_completed BOOLEAN DEFAULT FALSE,
            job_completed_at TIMESTAMPTZ,
            job_completed_biometric BOOLEAN DEFAULT FALSE,
            job_completed_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            job_completed_location GEOGRAPHY(POINT),
            job_completed_photos JSONB,
            job_completed_documents JSONB,
            job_completed_notes TEXT,
            final_completion_percentage percent_value,
            punch_list_items JSONB,
            punch_list_completed BOOLEAN DEFAULT FALSE,
            punch_list_completed_at TIMESTAMPTZ,
            total_job_duration_hours DECIMAL(8,2) CHECK (total_job_duration_hours >= 0),
            total_labor_hours DECIMAL(8,2) CHECK (total_labor_hours >= 0),
            total_overtime_hours DECIMAL(8,2) CHECK (total_overtime_hours >= 0),
            vendor_confirmed BOOLEAN DEFAULT FALSE,
            vendor_confirmed_at TIMESTAMPTZ,
            vendor_confirmation_data JSONB,
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            vendor_completion_id VARCHAR(255),
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(job_id, contractor_id)
        );
    """)

    # submissions
    op.execute("""
        CREATE TABLE submissions (
            submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_id UUID NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            completion_id UUID REFERENCES job_completions(completion_id) ON DELETE SET NULL,
            submission_number VARCHAR(50) UNIQUE,
            submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            submitted_by_id UUID REFERENCES contractors(contractor_id),
            submitted_by_biometric BOOLEAN DEFAULT FALSE,
            submitted_biometric_id UUID REFERENCES biometric_verifications(biometric_id),
            submitted_location GEOGRAPHY(POINT),
            submission_status VARCHAR(50) DEFAULT 'draft' CHECK (submission_status IN ('draft', 'partial', 'complete', 'pending_vendor', 'confirmed_by_vendor', 'rejected')),
            status_updated_at TIMESTAMPTZ,
            data_complete BOOLEAN DEFAULT FALSE,
            data_completeness_percentage percent_value,
            missing_required_fields JSONB,
            total_photos_submitted INTEGER DEFAULT 0 CHECK (total_photos_submitted >= 0),
            total_documents_submitted INTEGER DEFAULT 0 CHECK (total_documents_submitted >= 0),
            total_signatures_submitted INTEGER DEFAULT 0 CHECK (total_signatures_submitted >= 0),
            total_tasks_completed INTEGER DEFAULT 0 CHECK (total_tasks_completed >= 0),
            total_issues_reported INTEGER DEFAULT 0 CHECK (total_issues_reported >= 0),
            submission_package_url TEXT,
            submission_package_hash VARCHAR(255),
            version_number INTEGER DEFAULT 1 CHECK (version_number >= 1),
            previous_submission_id UUID REFERENCES submissions(submission_id),
            synced_to_vendor BOOLEAN DEFAULT FALSE,
            synced_to_vendor_at TIMESTAMPTZ,
            vendor_submission_id VARCHAR(255),
            vendor_confirmation_data JSONB,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # contractor_sessions
    op.execute("""
        CREATE TABLE contractor_sessions (
            session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            job_id UUID REFERENCES jobs(job_id) ON DELETE SET NULL,
            visit_id UUID REFERENCES site_visits(visit_id) ON DELETE SET NULL,
            session_token VARCHAR(255) UNIQUE,
            session_type VARCHAR(50) CHECK (session_type IN ('mobile', 'web', 'api')),
            device_id VARCHAR(255),
            device_name VARCHAR(255),
            device_type device_type,
            device_model VARCHAR(100),
            app_version VARCHAR(50),
            os_version VARCHAR(50),
            ip_address INET,
            battery_level_at_start INTEGER CHECK (battery_level_at_start >= 0 AND battery_level_at_start <= 100),
            network_type VARCHAR(20) CHECK (network_type IN ('wifi', '4G', '5G', '3G', 'offline', 'unknown')),
            offline_mode_active BOOLEAN DEFAULT FALSE,
            data_synced BOOLEAN DEFAULT FALSE,
            last_sync_at TIMESTAMPTZ,
            pending_sync_items INTEGER DEFAULT 0 CHECK (pending_sync_items >= 0),
            started_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # vendor_sync_queue (partitioned)
    op.execute("""
        CREATE TABLE vendor_sync_queue (
            sync_id UUID DEFAULT uuid_generate_v4(),
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            vendor_id UUID NOT NULL REFERENCES vendors(vendor_id) ON DELETE CASCADE,
            direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
            entity_type VARCHAR(50) NOT NULL,
            entity_id UUID,
            vendor_entity_id VARCHAR(255),
            payload JSONB NOT NULL,
            transformed_payload JSONB,
            sync_status vendor_sync_status DEFAULT 'pending',
            attempts INTEGER DEFAULT 0,
            last_attempt_at TIMESTAMPTZ,
            next_attempt_at TIMESTAMPTZ,
            error_message TEXT,
            updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMPTZ,
            PRIMARY KEY (sync_id, created_at)
        ) PARTITION BY RANGE (created_at);
    """)
    op.execute(
        "CREATE TABLE vendor_sync_queue_202401 PARTITION OF vendor_sync_queue FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');"
    )
    op.execute(
        "CREATE TABLE vendor_sync_queue_202402 PARTITION OF vendor_sync_queue FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');"
    )
    # (Add more partitions as needed)

    # local_sync_queue (partitioned)
    op.execute("""
        CREATE TABLE local_sync_queue (
            sync_item_id UUID DEFAULT uuid_generate_v4(),
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            contractor_id UUID NOT NULL REFERENCES contractors(contractor_id) ON DELETE CASCADE,
            device_id VARCHAR(255),
            session_id UUID REFERENCES contractor_sessions(session_id) ON DELETE SET NULL,
            table_name VARCHAR(100) NOT NULL,
            record_id UUID NOT NULL,
            operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
            data JSONB,
            sync_status sync_status DEFAULT 'pending',
            sync_attempts INTEGER DEFAULT 0 CHECK (sync_attempts >= 0),
            last_attempt_at TIMESTAMPTZ,
            next_attempt_at TIMESTAMPTZ,
            error_message TEXT,
            priority INTEGER DEFAULT 0 CHECK (priority >= 0),
            PRIMARY KEY (sync_item_id, created_at)
        ) PARTITION BY RANGE (created_at);
    """)
    op.execute(
        "CREATE TABLE local_sync_queue_202401 PARTITION OF local_sync_queue FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');"
    )

    # audit_log (partitioned)
    op.execute("""
        CREATE TABLE audit_log (
            audit_id UUID DEFAULT uuid_generate_v4(),
            changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
            table_name VARCHAR(100) NOT NULL,
            record_id UUID NOT NULL,
            action VARCHAR(10) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
            contractor_id UUID REFERENCES contractors(contractor_id) ON DELETE SET NULL,
            session_id UUID REFERENCES contractor_sessions(session_id) ON DELETE SET NULL,
            ip_address INET,
            old_data JSONB,
            new_data JSONB,
            changed_fields JSONB,
            PRIMARY KEY (audit_id, changed_at)
        ) PARTITION BY RANGE (changed_at);
    """)
    op.execute(
        "CREATE TABLE audit_log_202401 PARTITION OF audit_log FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');"
    )

    # -------------------- INDEXES (after tables exist) --------------------
    # vendors
    op.execute(
        "CREATE INDEX idx_vendors_code ON vendors(vendor_code) WHERE is_active = true;"
    )
    op.execute(
        "CREATE INDEX idx_vendors_sync ON vendors(last_sync_status, last_sync_at) WHERE is_active = true;"
    )

    # vendor_sync_queue
    op.execute(
        "CREATE INDEX idx_vendor_sync_status ON vendor_sync_queue(vendor_id, sync_status, next_attempt_at);"
    )
    op.execute(
        "CREATE INDEX idx_vendor_sync_entity ON vendor_sync_queue(entity_type, vendor_entity_id) WHERE vendor_entity_id IS NOT NULL;"
    )

    # contractors
    op.execute(
        "CREATE INDEX idx_contractors_email ON contractors(email) WHERE deleted_at IS NULL;"
    )
    op.execute(
        "CREATE INDEX idx_contractors_phone ON contractors(personal_phone) WHERE deleted_at IS NULL;"
    )
    op.execute(
        "CREATE INDEX idx_contractors_status ON contractors(account_status) WHERE deleted_at IS NULL;"
    )
    op.execute(
        "CREATE INDEX idx_contractors_location ON contractors(address_state, address_city) WHERE deleted_at IS NULL;"
    )
    op.execute(
        "CREATE INDEX idx_contractors_search ON contractors USING GIN(search_vector);"
    )

    # contractor_credentials
    op.execute(
        "CREATE INDEX idx_credentials_contractor ON contractor_credentials(contractor_id);"
    )
    op.execute(
        "CREATE INDEX idx_credentials_type ON contractor_credentials(credential_type);"
    )
    op.execute(
        "CREATE INDEX idx_credentials_expiration ON contractor_credentials(expiration_date);"
    )
    op.execute(
        "CREATE UNIQUE INDEX unique_contractor_credential ON contractor_credentials(contractor_id, credential_type, credential_number, state) WHERE credential_number IS NOT NULL;"
    )

    # contractor_insurance
    op.execute(
        "CREATE INDEX idx_insurance_contractor ON contractor_insurance(contractor_id);"
    )
    op.execute(
        "CREATE INDEX idx_insurance_expiration ON contractor_insurance(expiration_date);"
    )

    # contractor_devices
    op.execute(
        "CREATE INDEX idx_devices_contractor ON contractor_devices(contractor_id, is_active);"
    )
    op.execute(
        "CREATE INDEX idx_devices_last_used ON contractor_devices(last_used_at) WHERE is_active = true;"
    )

    # jobs
    op.execute(
        "CREATE INDEX idx_jobs_number ON jobs(job_number) WHERE deleted_at IS NULL;"
    )
    op.execute(
        "CREATE INDEX idx_jobs_status ON jobs(status) WHERE deleted_at IS NULL;")
    op.execute(
        "CREATE INDEX idx_jobs_dates ON jobs(scheduled_start_date, scheduled_end_date) WHERE deleted_at IS NULL;"
    )
    op.execute(
        "CREATE INDEX idx_jobs_vendor ON jobs(vendor_id, vendor_sync_status) WHERE deleted_at IS NULL;"
    )
    op.execute(
        "CREATE INDEX idx_jobs_location ON jobs USING GIST (job_location_geography) WHERE deleted_at IS NULL;"
    )
    op.execute("CREATE INDEX idx_jobs_search ON jobs USING GIN(search_vector);")
    op.execute(
        "CREATE INDEX idx_jobs_vendor_lookup ON jobs(vendor_id, vendor_job_id) WHERE vendor_job_id IS NOT NULL;"
    )
    op.execute(
        "CREATE UNIQUE INDEX unique_vendor_job ON jobs(vendor_id, vendor_job_id) WHERE vendor_job_id IS NOT NULL;"
    )

    # job_assignments
    op.execute(
        "CREATE INDEX idx_assignments_job ON job_assignments(job_id) INCLUDE (contractor_id) WHERE assignment_status = 'active';"
    )
    op.execute(
        "CREATE INDEX idx_assignments_contractor ON job_assignments(contractor_id) INCLUDE (job_id) WHERE assignment_status = 'active';"
    )
    op.execute(
        "CREATE UNIQUE INDEX unique_active_assignment ON job_assignments(job_id, contractor_id, assignment_status) WHERE assignment_status = 'active';"
    )

    # biometric_verifications
    op.execute(
        "CREATE INDEX idx_biometric_contractor ON biometric_verifications(contractor_id, biometric_timestamp);"
    )
    op.execute(
        "CREATE INDEX idx_biometric_job ON biometric_verifications(job_id, biometric_timestamp);"
    )

    # job_responses
    op.execute(
        "CREATE INDEX idx_responses_job ON job_responses(job_id, response_type);"
    )
    op.execute(
        "CREATE INDEX idx_responses_contractor ON job_responses(contractor_id);")
    op.execute(
        "CREATE INDEX idx_responses_sync ON job_responses(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # site_visits
    op.execute(
        "CREATE INDEX idx_visits_job ON site_visits(job_id, check_in_time);")
    op.execute(
        "CREATE INDEX idx_visits_contractor ON site_visits(contractor_id, check_in_time);"
    )
    op.execute(
        "CREATE INDEX idx_visits_sync ON site_visits(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # progress_updates
    op.execute(
        "CREATE INDEX idx_progress_job ON progress_updates(job_id, created_at);")
    op.execute(
        "CREATE INDEX idx_progress_sync ON progress_updates(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # tasks
    op.execute("CREATE INDEX idx_tasks_job ON tasks(job_id, sequence_order);")
    op.execute("CREATE INDEX idx_tasks_status ON tasks(task_status, assigned_to);")
    op.execute("CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);")

    # task_executions
    op.execute(
        "CREATE INDEX idx_executions_task ON task_executions(task_id, completed_at);"
    )
    op.execute(
        "CREATE INDEX idx_executions_sync ON task_executions(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # issues
    op.execute("CREATE INDEX idx_issues_job ON issues(job_id, issue_status);")
    op.execute(
        "CREATE INDEX idx_issues_status ON issues(issue_status, issue_severity);"
    )
    op.execute(
        "CREATE INDEX idx_issues_search ON issues USING GIN(search_vector);")
    op.execute(
        "CREATE INDEX idx_issues_sync ON issues(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # photos
    op.execute(
        "CREATE INDEX idx_photos_job ON photos(job_id, photo_category, photo_timestamp);"
    )
    op.execute(
        "CREATE INDEX idx_photos_sync ON photos(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # job_completions
    op.execute("CREATE INDEX idx_completions_job ON job_completions(job_id);")
    op.execute(
        "CREATE INDEX idx_completions_sync ON job_completions(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # submissions
    op.execute(
        "CREATE INDEX idx_submissions_job ON submissions(job_id, submission_status);"
    )
    op.execute(
        "CREATE INDEX idx_submissions_sync ON submissions(synced_to_vendor) WHERE synced_to_vendor = false;"
    )

    # contractor_sessions
    op.execute(
        "CREATE INDEX idx_sessions_contractor ON contractor_sessions(contractor_id, started_at);"
    )
    op.execute(
        "CREATE INDEX idx_sessions_token ON contractor_sessions(session_token) WHERE ended_at IS NULL;"
    )

    # local_sync_queue
    op.execute(
        "CREATE INDEX idx_local_sync_status ON local_sync_queue(sync_status, next_attempt_at, priority) WHERE sync_status = 'pending';"
    )
    op.execute(
        "CREATE INDEX idx_local_sync_contractor ON local_sync_queue(contractor_id, sync_status, created_at);"
    )

    # audit_log
    op.execute(
        "CREATE INDEX idx_audit_record ON audit_log(table_name, record_id, changed_at);"
    )
    op.execute(
        "CREATE INDEX idx_audit_contractor ON audit_log(contractor_id, changed_at);"
    )

    # -------------------- TRIGGER FUNCTIONS --------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_site_visit_hours()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.check_out_time IS NOT NULL THEN
                NEW.total_hours_on_site := EXTRACT(EPOCH FROM (NEW.check_out_time - NEW.check_in_time)) / 3600;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION queue_vendor_sync()
        RETURNS TRIGGER AS $$
        DECLARE
            v_vendor_id UUID;
            v_job_id UUID;
        BEGIN
            IF TG_TABLE_NAME IN ('site_visits', 'progress_updates', 'task_executions', 'issues', 'photos', 'job_completions', 'submissions') THEN
                SELECT vendor_id INTO v_vendor_id
                FROM jobs
                WHERE job_id = NEW.job_id;
                IF v_vendor_id IS NOT NULL THEN
                    INSERT INTO vendor_sync_queue (vendor_id, direction, entity_type, entity_id, payload)
                    VALUES (v_vendor_id, 'outbound', TG_TABLE_NAME, NEW.contractor_id, to_jsonb(NEW));
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # -------------------- TRIGGERS --------------------
    # Apply updated_at triggers to all tables with updated_at column
    op.execute("""
        DO $$
        DECLARE
            t text;
        BEGIN
            FOR t IN
                SELECT table_name
                FROM information_schema.columns
                WHERE column_name = 'updated_at'
                AND table_schema = 'public'
                AND table_name NOT LIKE '%partition%'
            LOOP
                EXECUTE format('
                    DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;
                    CREATE TRIGGER update_%I_updated_at
                    BEFORE UPDATE ON %I
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()',
                    t, t, t, t
                );
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER calculate_site_visit_hours_trigger
        BEFORE INSERT OR UPDATE OF check_out_time ON site_visits
        FOR EACH ROW
        EXECUTE FUNCTION calculate_site_visit_hours();
    """)

    op.execute("""
        CREATE TRIGGER sync_site_visits AFTER INSERT OR UPDATE ON site_visits
        FOR EACH ROW WHEN (NEW.synced_to_vendor = false)
        EXECUTE FUNCTION queue_vendor_sync();
    """)

    op.execute("""
        CREATE TRIGGER sync_progress_updates AFTER INSERT OR UPDATE ON progress_updates
        FOR EACH ROW WHEN (NEW.synced_to_vendor = false)
        EXECUTE FUNCTION queue_vendor_sync();
    """)

    op.execute("""
        CREATE TRIGGER sync_task_executions AFTER INSERT OR UPDATE ON task_executions
        FOR EACH ROW WHEN (NEW.synced_to_vendor = false)
        EXECUTE FUNCTION queue_vendor_sync();
    """)

    op.execute("""
        CREATE TRIGGER sync_issues AFTER INSERT OR UPDATE ON issues
        FOR EACH ROW WHEN (NEW.synced_to_vendor = false)
        EXECUTE FUNCTION queue_vendor_sync();
    """)

    op.execute("""
        CREATE TRIGGER sync_photos AFTER INSERT OR UPDATE ON photos
        FOR EACH ROW WHEN (NEW.synced_to_vendor = false)
        EXECUTE FUNCTION queue_vendor_sync();
    """)

    op.execute("""
        CREATE TRIGGER sync_job_completions AFTER INSERT OR UPDATE ON job_completions
        FOR EACH ROW WHEN (NEW.synced_to_vendor = false)
        EXECUTE FUNCTION queue_vendor_sync();
    """)

    op.execute("""
        CREATE TRIGGER sync_submissions AFTER INSERT OR UPDATE ON submissions
        FOR EACH ROW WHEN (NEW.synced_to_vendor = false)
        EXECUTE FUNCTION queue_vendor_sync();
    """)

    # -------------------- ROW LEVEL SECURITY --------------------
    op.execute("ALTER TABLE contractors ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE site_visits ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE progress_updates ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE issues ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE task_executions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE photos ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE job_completions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE local_sync_queue ENABLE ROW LEVEL SECURITY;")

    op.execute("""
        CREATE OR REPLACE FUNCTION get_current_contractor_id()
        RETURNS UUID AS $$
        BEGIN
            RETURN NULLIF(current_setting('app.current_contractor_id', TRUE), '')::UUID;
        EXCEPTION WHEN OTHERS THEN
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    op.execute("""
        CREATE POLICY contractor_self_access ON contractors
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY job_access ON jobs
            FOR SELECT USING (
                EXISTS (
                    SELECT 1 FROM job_assignments
                    WHERE job_id = jobs.job_id
                    AND contractor_id = get_current_contractor_id()
                )
            );
    """)

    op.execute("""
        CREATE POLICY site_visits_access ON site_visits
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY progress_updates_access ON progress_updates
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY issues_access ON issues
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY task_executions_access ON task_executions
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY photos_access ON photos
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY job_completions_access ON job_completions
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY submissions_access ON submissions
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    op.execute("""
        CREATE POLICY local_sync_queue_access ON local_sync_queue
            FOR ALL USING (contractor_id = get_current_contractor_id());
    """)

    # -------------------- VIEWS --------------------
    op.execute("""
        CREATE OR REPLACE VIEW job_status_summary AS
        WITH latest_progress AS (
            SELECT DISTINCT ON (job_id)
                job_id,
                completion_percentage_after,
                created_at as last_progress_update
            FROM progress_updates
            ORDER BY job_id, created_at DESC
        )
        SELECT
            j.job_id,
            j.job_number,
            j.job_name,
            j.job_description,
            j.status,
            j.priority,
            j.scheduled_start_date,
            j.scheduled_end_date,
            j.actual_start_date,
            j.actual_end_date,
            j.job_type,
            j.job_category,
            j.vendor_name,
            j.site_address_city as site_city,
            j.site_address_state as site_state,
            COUNT(DISTINCT ja.contractor_id) as assigned_contractors,
            COUNT(DISTINCT sv.visit_id) as total_visits,
            MAX(sv.check_in_time) as last_check_in,
            COUNT(DISTINCT i.issue_id) FILTER (WHERE i.issue_status NOT IN ('resolved', 'closed')) as open_issues,
            COALESCE(lp.completion_percentage_after, 0) as current_completion_percentage,
            COUNT(DISTINCT t.task_id) FILTER (WHERE t.task_status != 'completed') as pending_tasks,
            COUNT(DISTINCT t.task_id) as total_tasks,
            CASE
                WHEN jc.job_completed THEN 'Completed'
                WHEN j.actual_start_date IS NOT NULL THEN 'In Progress'
                ELSE 'Not Started'
            END as progress_status,
            jc.vendor_confirmed,
            jc.vendor_confirmed_at,
            j.vendor_sync_status
        FROM jobs j
        LEFT JOIN job_assignments ja ON j.job_id = ja.job_id AND ja.assignment_status = 'active'
        LEFT JOIN site_visits sv ON j.job_id = sv.job_id
        LEFT JOIN issues i ON j.job_id = i.job_id
        LEFT JOIN tasks t ON j.job_id = t.job_id
        LEFT JOIN job_completions jc ON j.job_id = jc.job_id
        LEFT JOIN latest_progress lp ON j.job_id = lp.job_id
        WHERE j.deleted_at IS NULL
        GROUP BY j.job_id, j.job_number, j.job_name, j.job_description, j.status, j.priority,
                 j.scheduled_start_date, j.scheduled_end_date, j.actual_start_date, j.actual_end_date,
                 j.job_type, j.job_category, j.vendor_name, j.site_address_city, j.site_address_state,
                 jc.job_completed, lp.completion_percentage_after, lp.last_progress_update,
                 jc.vendor_confirmed, jc.vendor_confirmed_at, j.vendor_sync_status;
    """)

    op.execute("""
        CREATE OR REPLACE VIEW vendor_sync_status_view AS
        SELECT
            v.vendor_id,
            v.vendor_name,
            v.last_sync_at,
            v.last_sync_status,
            COUNT(DISTINCT CASE WHEN vsq.direction = 'outbound' AND vsq.sync_status = 'pending' THEN vsq.sync_id END) as pending_outbound,
            COUNT(DISTINCT CASE WHEN vsq.direction = 'inbound' AND vsq.sync_status = 'pending' THEN vsq.sync_id END) as pending_inbound,
            COUNT(DISTINCT CASE WHEN j.vendor_sync_status = 'pending' THEN j.job_id END) as jobs_pending_sync,
            MAX(vsq.created_at) as last_queue_item
        FROM vendors v
        LEFT JOIN vendor_sync_queue vsq ON v.vendor_id = vsq.vendor_id
        LEFT JOIN jobs j ON v.vendor_id = j.vendor_id AND j.vendor_sync_status = 'pending'
        WHERE v.is_active = true
        GROUP BY v.vendor_id, v.vendor_name, v.last_sync_at, v.last_sync_status;
    """)


def downgrade():
    # Drop views
    op.execute("DROP VIEW IF EXISTS vendor_sync_status_view;")
    op.execute("DROP VIEW IF EXISTS job_status_summary;")

    # Drop RLS policies
    op.execute(
        "DROP POLICY IF EXISTS local_sync_queue_access ON local_sync_queue;")
    op.execute("DROP POLICY IF EXISTS submissions_access ON submissions;")
    op.execute("DROP POLICY IF EXISTS job_completions_access ON job_completions;")
    op.execute("DROP POLICY IF EXISTS photos_access ON photos;")
    op.execute("DROP POLICY IF EXISTS task_executions_access ON task_executions;")
    op.execute("DROP POLICY IF EXISTS issues_access ON issues;")
    op.execute(
        "DROP POLICY IF EXISTS progress_updates_access ON progress_updates;")
    op.execute("DROP POLICY IF EXISTS site_visits_access ON site_visits;")
    op.execute("DROP POLICY IF EXISTS job_access ON jobs;")
    op.execute("DROP POLICY IF EXISTS contractor_self_access ON contractors;")

    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS sync_submissions ON submissions;")
    op.execute("DROP TRIGGER IF EXISTS sync_job_completions ON job_completions;")
    op.execute("DROP TRIGGER IF EXISTS sync_photos ON photos;")
    op.execute("DROP TRIGGER IF EXISTS sync_issues ON issues;")
    op.execute("DROP TRIGGER IF EXISTS sync_task_executions ON task_executions;")
    op.execute("DROP TRIGGER IF EXISTS sync_progress_updates ON progress_updates;")
    op.execute("DROP TRIGGER IF EXISTS sync_site_visits ON site_visits;")
    op.execute(
        "DROP TRIGGER IF EXISTS calculate_site_visit_hours_trigger ON site_visits;"
    )
    op.execute("""
        DO $$
        DECLARE
            t text;
        BEGIN
            FOR t IN
                SELECT table_name
                FROM information_schema.columns
                WHERE column_name = 'updated_at'
                AND table_schema = 'public'
                AND table_name NOT LIKE '%partition%'
            LOOP
                EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;', t, t);
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Drop trigger functions
    op.execute("DROP FUNCTION IF EXISTS queue_vendor_sync() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS calculate_site_visit_hours() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS get_current_contractor_id() CASCADE;")

    # Drop tables (order matters due to dependencies)
    op.execute("DROP TABLE IF EXISTS audit_log CASCADE;")
    op.execute("DROP TABLE IF EXISTS local_sync_queue CASCADE;")
    op.execute("DROP TABLE IF EXISTS vendor_sync_queue CASCADE;")
    op.execute("DROP TABLE IF EXISTS submissions CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_completions CASCADE;")
    op.execute("DROP TABLE IF EXISTS photos CASCADE;")
    op.execute("DROP TABLE IF EXISTS issues CASCADE;")
    op.execute("DROP TABLE IF EXISTS task_executions CASCADE;")
    op.execute("DROP TABLE IF EXISTS tasks CASCADE;")
    op.execute("DROP TABLE IF EXISTS progress_updates CASCADE;")
    op.execute("DROP TABLE IF EXISTS site_visits CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_responses CASCADE;")
    op.execute("DROP TABLE IF EXISTS biometric_verifications CASCADE;")
    op.execute("DROP TABLE IF EXISTS job_assignments CASCADE;")
    op.execute("DROP TABLE IF EXISTS jobs CASCADE;")
    op.execute("DROP TABLE IF EXISTS contractor_sessions CASCADE;")
    op.execute("DROP TABLE IF EXISTS notification_preferences CASCADE;")
    op.execute("DROP TABLE IF EXISTS contractor_devices CASCADE;")
    op.execute("DROP TABLE IF EXISTS contractor_insurance CASCADE;")
    op.execute("DROP TABLE IF EXISTS contractor_credentials CASCADE;")
    op.execute("DROP TABLE IF EXISTS contractors CASCADE;")
    op.execute("DROP TABLE IF EXISTS vendors CASCADE;")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS vendor_sync_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS credential_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS sync_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS device_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS verification_type CASCADE;")
    op.execute("DROP TYPE IF EXISTS task_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS issue_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS issue_severity CASCADE;")
    op.execute("DROP TYPE IF EXISTS priority_level CASCADE;")
    op.execute("DROP TYPE IF EXISTS job_status CASCADE;")
    op.execute("DROP TYPE IF EXISTS account_status CASCADE;")

    # Drop domains
    op.execute("DROP DOMAIN IF EXISTS coordinate CASCADE;")
    op.execute("DROP DOMAIN IF EXISTS rating_value CASCADE;")
    op.execute("DROP DOMAIN IF EXISTS percent_value CASCADE;")
    op.execute("DROP DOMAIN IF EXISTS ssn_last_four CASCADE;")
    op.execute("DROP DOMAIN IF EXISTS email_address CASCADE;")
    op.execute("DROP DOMAIN IF EXISTS phone_number CASCADE;")

    # Drop extensions (optional)
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm" CASCADE;')
    op.execute('DROP EXTENSION IF EXISTS "btree_gin" CASCADE;')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto" CASCADE;')
    op.execute('DROP EXTENSION IF EXISTS "postgis" CASCADE;')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp" CASCADE;')
