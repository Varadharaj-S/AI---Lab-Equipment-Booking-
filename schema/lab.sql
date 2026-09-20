CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS equipment (
    equipment_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS equipment_policy (
    equipment_id TEXT PRIMARY KEY REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    training_required BOOLEAN NOT NULL DEFAULT FALSE,
    max_hours INTEGER NOT NULL CHECK (max_hours > 0)
);

CREATE TABLE IF NOT EXISTS training (
    student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
    equipment_id TEXT REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id,equipment_id)
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id),
    equipment_id TEXT NOT NULL REFERENCES equipment(equipment_id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    CHECK (end_time > start_time)
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id BIGSERIAL PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id),
    message TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookings_equipment_time ON bookings(equipment_id,start_time,end_time);
CREATE INDEX IF NOT EXISTS idx_training_student ON training(student_id);
