-- Seed database with categories and questions
INSERT INTO categories (id, title, description, icon, display_order) VALUES
('password_auth', 'Passord og Autentisering', 'Forståelse av passord beste praksis og flerfaktor-autentisering', 'fas fa-key', 1),
('email_phishing', 'E-postsikkerhet og Phishing-gjenkjenning', 'Identifisering av mistenkelige e-poster og sosial manipulering', 'fas fa-envelope-open-text', 2),
('device_security', 'Enhet og Endepunkt-sikkerhet', 'Sikring av arbeidsenheter og opprettholdelse av god digital hygiene', 'fas fa-laptop', 3),
('data_protection', 'Datahåndtering og Personvern', 'Beskyttelse av sensitiv informasjon og riktig datahåndtering', 'fas fa-database', 4),
('remote_work', 'Hjemmekontor og Nettverkssikkerhet', 'Sikre praksis for hjemmearbeid og offentlige rom', 'fas fa-wifi', 5),
('incident_response', 'Hendelsesrapportering og Respons', 'Gjenkjenne sikkerhetshendelser og vite hvordan man skal respondere', 'fas fa-exclamation-triangle', 6),
('physical_security', 'Fysisk Sikkerhetsbevissthet', 'Forståelse av fysiske trusler og bygningssikkerhet', 'fas fa-building', 7)
ON CONFLICT (id) DO NOTHING;

-- Insert sample questions
INSERT INTO questions (id, category_id, question_text, question_type, weight, scenario, display_order) VALUES
(1, 'password_auth', 'Hva gjør et passord sikkert? (Velg alle som gjelder)', 'multiple', 5, NULL, 1),
(2, 'password_auth', 'Din kollega ber deg dele påloggingsinformasjonen din slik at de kan få tilgang til et system mens du er på ferie. Hva bør du gjøre?', 'single', 5, NULL, 2),
(3, 'email_phishing', 'Du mottar en mistenkelig e-post. Hva bør du gjøre?', 'single', 5, NULL, 3),
(4, 'device_security', 'Hvor ofte bør du installere sikkerhetsoppdateringer på arbeidsdatamaskinen din?', 'single', 4, NULL, 4)
ON CONFLICT (id) DO NOTHING;

-- Insert sample question options
INSERT INTO question_options (question_id, option_value, option_label, is_correct, display_order) VALUES
(1, 'long_complex', 'Langt og komplekst med tall, bokstaver og symboler', true, 1),
(1, 'easy_remember', 'Lett å huske som "passord123"', false, 2),
(1, 'unique_accounts', 'Unikt for hver konto', true, 3),
(1, 'shared_team', 'Delt med teamet for enkel tilgang', false, 4),
(2, 'share_password', 'Dele passordet ditt', false, 1),
(2, 'create_temp', 'Be IT om å opprette en midlertidig konto', true, 2),
(2, 'write_down', 'Skrive ned passordet og legge det på pulten', false, 3),
(3, 'click_link', 'Klikke på lenken for å sjekke', false, 1),
(3, 'report_it', 'Rapportere det til IT-avdelingen', true, 2),
(3, 'delete_ignore', 'Slette e-posten og ignorere den', false, 3),
(4, 'immediately', 'Umiddelbart når de er tilgjengelige', true, 1),
(4, 'monthly', 'En gang i måneden', false, 2),
(4, 'never', 'Aldri, de kan forårsake problemer', false, 3)
ON CONFLICT (question_id, option_value) DO NOTHING;
