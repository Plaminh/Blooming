-- Seed catalog data idempotently
INSERT INTO plants (species, name, description, unlock_cost)
VALUES
    ('monstera', 'Monstera Deliciosa', 'A classic houseplant with large, beautiful split leaves.', 0),
    ('sunflower', 'Sunflower', 'Bright and cheerful, turning to face the sun.', 10),
    ('bonsai', 'Bonsai Tree', 'Requires patience and care, but brings deep peace.', 20),
    ('jasmine', 'Jasmine', 'A fragrant climber that blooms in the evening.', 15),
    ('lavender', 'Lavender', 'A calming, aromatic herb with lovely purple flowers.', 15)
ON CONFLICT (species) DO NOTHING;
