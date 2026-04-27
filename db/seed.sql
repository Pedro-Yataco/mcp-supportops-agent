INSERT INTO roles (name, description) VALUES
('support_agent', 'Can view and update basic support tickets'),
('support_manager', 'Can manage escalations and view SLA risk'),
('admin', 'Can access administrative tools');

INSERT INTO users (username, full_name, role_id) VALUES
('ana.agent', 'Ana Support Agent', 1),
('marco.manager', 'Marco Support Manager', 2),
('sofia.admin', 'Sofia Admin', 3);

INSERT INTO permissions (code, description) VALUES
('tickets.read', 'Read support tickets'),
('tickets.comment.internal', 'Add internal ticket comments'),
('tickets.escalate', 'Escalate high priority tickets'),
('customers.read', 'Read customer profile'),
('sla.read', 'Read customer SLA information'),
('sla.risk.detect', 'Detect SLA risk');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p
WHERE r.name = 'support_agent'
  AND p.code IN (
    'tickets.read',
    'tickets.comment.internal',
    'customers.read',
    'sla.read'
  );

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p
WHERE r.name = 'support_manager'
  AND p.code IN (
    'tickets.read',
    'tickets.comment.internal',
    'tickets.escalate',
    'customers.read',
    'sla.read',
    'sla.risk.detect'
  );

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'admin';

INSERT INTO customers (name, tier, industry) VALUES
('Acme Corp', 'enterprise', 'Manufacturing'),
('Globex', 'premium', 'Finance'),
('Initech', 'standard', 'Software');

INSERT INTO customer_slas (customer_id, priority, response_time_hours, resolution_time_hours) VALUES
(1, 'P1', 1, 8),
(1, 'P2', 4, 24),
(1, 'P3', 8, 72),
(2, 'P1', 2, 12),
(2, 'P2', 6, 36),
(2, 'P3', 12, 96),
(3, 'P1', 4, 24),
(3, 'P2', 8, 48),
(3, 'P3', 24, 120);

INSERT INTO tickets (customer_id, title, description, priority, status, assigned_to) VALUES
(1, 'Production API outage', 'Customer reports that the production API is returning 503 errors.', 'P1', 'open', 1),
(1, 'Intermittent login failures', 'Some users are unable to log in during peak hours.', 'P2', 'in_progress', 1),
(2, 'Billing sync delay', 'Invoices are not syncing to the external accounting system.', 'P2', 'open', 1),
(3, 'Feature request: export reports', 'Customer wants CSV export for monthly support reports.', 'P3', 'waiting_customer', NULL);

INSERT INTO ticket_comments (ticket_id, author_user_id, comment, is_internal) VALUES
(1, 1, 'Initial investigation started. API gateway logs show elevated 5xx errors.', TRUE),
(2, 1, 'Auth service latency increased around 10:00 UTC.', TRUE),
(3, 2, 'May require coordination with billing integration team.', TRUE);