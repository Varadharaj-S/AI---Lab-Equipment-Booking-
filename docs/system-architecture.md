# System Architecture

```text
Student
   |
   v
Supervisor Agent
   |
   +------------------------+
   |                        |
   v                        v
Equipment Specialist    Booking Agent
(Read Only)             (Read + Write)
   |                        |
   +------------+-----------+
                |
                v
             Tool Layer
                |
                v
          Neon PostgreSQL
```

Domain tables store students, equipment, policies, training, bookings and notifications.

Agent tables store runs, leases, messages and idempotency keys.
