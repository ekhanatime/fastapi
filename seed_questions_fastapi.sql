-- Seed script for FastAPI backend database structure
-- This script adds all questions and options to match the existing schema

-- Insert questions (matching existing FastAPI schema)
INSERT INTO questions (category_id, question_text, question_type, weight, display_order, is_active) VALUES
-- Password and Authentication (4 questions)
('password_auth', 'Hva gjør et passord sikkert? (Velg alle som gjelder)', 'multiple', 5, 1, true),
('password_auth', 'Din kollega ber deg dele påloggingsinformasjonen din slik at de kan få tilgang til et system mens du er på ferie. Hva bør du gjøre?', 'single', 5, 2, true),
('password_auth', 'Hva er flerfaktor-autentisering (MFA)?', 'single', 4, 3, true),
('password_auth', 'Hvilket av disse er det BESTE stedet å lagre arbeidspassordene dine?', 'single', 4, 4, true),

-- Email Security and Phishing (4 questions)
('email_phishing', 'Du mottar denne e-posten. Hva bør du gjøre?', 'single', 5, 5, true),
('email_phishing', 'Hvilke av disse er røde flagg i en mistenkelig e-post? (Velg alle som gjelder)', 'multiple', 4, 6, true),
('email_phishing', 'Lederen din sender deg en haster e-post som ber om lønnsinformasjon for ansatte til et budsjettmøte. E-posten virker litt annerledes enn deres vanlige stil. Hva bør du gjøre?', 'single', 5, 7, true),
('email_phishing', 'Hva bør du gjøre hvis du ved en feil klikker på en mistenkelig lenke i en e-post? (Velg alle som gjelder)', 'multiple', 4, 8, true),

-- Device and Endpoint Security (4 questions)
('device_security', 'Hvor ofte bør du installere sikkerhetsoppdateringer på arbeidsdatamaskinen din?', 'single', 4, 9, true),
('device_security', 'Du jobber med et sensitivt dokument når du må gå fra pulten til et møte. Hva bør du gjøre?', 'single', 4, 10, true),
('device_security', 'Du får en popup som sier "Datamaskinen din er infisert! Ring dette nummeret umiddelbart!" Hva bør du gjøre?', 'single', 5, 11, true),
('device_security', 'Hvilke av disse praksisene hjelper til med å holde arbeidsenheten din sikker? (Velg alle som gjelder)', 'multiple', 4, 12, true),

-- Data Protection and Privacy (4 questions)
('data_protection', 'Hvordan bør du dele konfidensielle bedriftsdokumenter med eksterne partnere?', 'single', 5, 13, true),
('data_protection', 'Du finner en USB-minnepinne på parkeringsplassen med merket "Konfidensielle budsjettfiler". Hva bør du gjøre?', 'single', 5, 14, true),
('data_protection', 'Hvilken informasjon bør du ALDRI inkludere i arbeids-e-poster? (Velg alle som gjelder)', 'multiple', 4, 15, true),
('data_protection', 'Bedriften din bruker skytjenester for å lagre data. Hva er den VIKTIGSTE sikkerhetstiltaken?', 'single', 4, 16, true),

-- Remote Work and Network Security (4 questions)
('remote_work', 'Du jobber hjemmefra og trenger å koble til bedriftens nettverk. Hva er den SIKRESTE måten?', 'single', 5, 17, true),
('remote_work', 'Du er på en kafe og trenger å sjekke arbeids-e-post. Hva bør du gjøre?', 'single', 4, 18, true),
('remote_work', 'Hvilke av disse er gode sikkerhetspraksis for hjemmekontor? (Velg alle som gjelder)', 'multiple', 4, 19, true),
('remote_work', 'Du oppdager at hjemme-WiFi-nettverket ditt ikke har passord. Hva bør du gjøre?', 'single', 4, 20, true),

-- Incident Response (2 questions)
('incident_response', 'Du mistenker at datamaskinen din kan være infisert med skadelig programvare. Hva bør du gjøre FØRST?', 'single', 5, 21, true),
('incident_response', 'Hva bør du gjøre hvis du ved en feil sender konfidensiell informasjon til feil person? (Velg alle som gjelder)', 'multiple', 4, 22, true),

-- Physical Security (2 questions)
('physical_security', 'Noen du ikke kjenner igjen følger deg gjennom en sikker dør som krever kortadgang. Hva bør du gjøre?', 'single', 4, 23, true),
('physical_security', 'Hvilke av disse er god fysisk sikkerhetspraksis? (Velg alle som gjelder)', 'multiple', 3, 24, true)

ON CONFLICT (id) DO NOTHING;

-- Now insert question options (matching existing FastAPI schema with option_text instead of option_label)
-- We need to get the question IDs first, so we'll use a different approach

-- First, let's create a temporary function to get question ID by category and order
CREATE OR REPLACE FUNCTION get_question_id_by_order(cat_id VARCHAR, ord INTEGER) 
RETURNS INTEGER AS $$
DECLARE
    q_id INTEGER;
BEGIN
    SELECT id INTO q_id FROM questions WHERE category_id = cat_id AND display_order = ord;
    RETURN q_id;
END;
$$ LANGUAGE plpgsql;

-- Insert question options using the function
-- Question 1 options (Password security - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('password_auth', 1), 'long_complex', 'Langt og komplekst med tall, bokstaver og symboler', true, 1),
(get_question_id_by_order('password_auth', 1), 'easy_remember', 'Lett å huske som "passord123"', false, 2),
(get_question_id_by_order('password_auth', 1), 'unique_accounts', 'Unikt for hver konto', true, 3),
(get_question_id_by_order('password_auth', 1), 'shared_team', 'Delt med teamet for enkel tilgang', false, 4);

-- Question 2 options (Sharing passwords)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('password_auth', 2), 'share_password', 'Dele passordet ditt', false, 1),
(get_question_id_by_order('password_auth', 2), 'create_temp', 'Be IT om å opprette en midlertidig konto', true, 2),
(get_question_id_by_order('password_auth', 2), 'write_down', 'Skrive ned passordet og legge det på pulten', false, 3);

-- Question 3 options (MFA)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('password_auth', 3), 'extra_password', 'En ekstra passord-lag', false, 1),
(get_question_id_by_order('password_auth', 3), 'multiple_factors', 'Bruk av flere autentiseringsfaktorer (noe du vet, har, eller er)', true, 2),
(get_question_id_by_order('password_auth', 3), 'complex_password', 'Et veldig komplekst passord', false, 3);

-- Question 4 options (Password storage)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('password_auth', 4), 'password_manager', 'En passordbehandler', true, 1),
(get_question_id_by_order('password_auth', 4), 'browser_save', 'Lagret i nettleseren', false, 2),
(get_question_id_by_order('password_auth', 4), 'sticky_note', 'På en lapp på skjermen', false, 3),
(get_question_id_by_order('password_auth', 4), 'excel_file', 'I en Excel-fil på skrivebordet', false, 4);

-- Question 5 options (Suspicious email)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('email_phishing', 5), 'click_link', 'Klikke på lenken for å sjekke', false, 1),
(get_question_id_by_order('email_phishing', 5), 'report_it', 'Rapportere det til IT-avdelingen', true, 2),
(get_question_id_by_order('email_phishing', 5), 'delete_ignore', 'Slette e-posten og ignorere den', false, 3);

-- Question 6 options (Red flags in email - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('email_phishing', 6), 'urgent_language', 'Presserende språk som "HASTER" eller "Umiddelbart"', true, 1),
(get_question_id_by_order('email_phishing', 6), 'suspicious_links', 'Lenker som ikke matcher den påståtte avsenderen', true, 2),
(get_question_id_by_order('email_phishing', 6), 'personal_info_request', 'Forespørsel om personlig eller finansiell informasjon', true, 3),
(get_question_id_by_order('email_phishing', 6), 'professional_design', 'Profesjonelt utseende og design', false, 4);

-- Question 7 options (Boss email request)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('email_phishing', 7), 'send_immediately', 'Sende informasjonen umiddelbart', false, 1),
(get_question_id_by_order('email_phishing', 7), 'verify_first', 'Verifisere forespørselen gjennom en annen kommunikasjonskanal', true, 2),
(get_question_id_by_order('email_phishing', 7), 'ask_colleagues', 'Spørre kollegaer om de har fått samme forespørsel', false, 3);

-- Question 8 options (Clicked suspicious link - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('email_phishing', 8), 'disconnect_network', 'Koble fra nettverket umiddelbart', true, 1),
(get_question_id_by_order('email_phishing', 8), 'change_passwords', 'Endre passord for viktige kontoer', true, 2),
(get_question_id_by_order('email_phishing', 8), 'report_incident', 'Rapportere hendelsen til IT-sikkerhet', true, 3),
(get_question_id_by_order('email_phishing', 8), 'continue_working', 'Fortsette å jobbe som normalt', false, 4);

-- Question 9 options (Security updates)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('device_security', 9), 'immediately', 'Umiddelbart når de er tilgjengelige', true, 1),
(get_question_id_by_order('device_security', 9), 'monthly', 'En gang i måneden', false, 2),
(get_question_id_by_order('device_security', 9), 'never', 'Aldri, de kan forårsake problemer', false, 3);

-- Question 10 options (Leaving workstation)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('device_security', 10), 'leave_as_is', 'La datamaskinen være som den er siden jeg kommer tilbake snart', false, 1),
(get_question_id_by_order('device_security', 10), 'lock_screen', 'Låse skjermen eller logge ut', true, 2),
(get_question_id_by_order('device_security', 10), 'minimize_windows', 'Minimere alle vinduer', false, 3);

-- Continue with remaining questions...
-- Question 11 options (Fake popup)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('device_security', 11), 'call_number', 'Ringe nummeret som vises', false, 1),
(get_question_id_by_order('device_security', 11), 'close_popup', 'Lukke popup-en og kjøre en legitim antivirus-skanning', true, 2),
(get_question_id_by_order('device_security', 11), 'click_fix', 'Klikke på "Fiks nå"-knappen', false, 3);

-- Question 12 options (Device security practices - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('device_security', 12), 'regular_updates', 'Installere oppdateringer regelmessig', true, 1),
(get_question_id_by_order('device_security', 12), 'antivirus_software', 'Bruke antivirus-programvare', true, 2),
(get_question_id_by_order('device_security', 12), 'screen_lock', 'Aktivere skjermlås', true, 3),
(get_question_id_by_order('device_security', 12), 'disable_firewall', 'Deaktivere brannmur for bedre ytelse', false, 4);

-- Question 13 options (Sharing confidential documents)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('data_protection', 13), 'email_attachment', 'Sende som e-postvedlegg', false, 1),
(get_question_id_by_order('data_protection', 13), 'secure_platform', 'Bruke en sikker fildelingsplattform', true, 2),
(get_question_id_by_order('data_protection', 13), 'usb_drive', 'Kopiere til USB-minnepinne', false, 3);

-- Question 14 options (Found USB drive)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('data_protection', 14), 'plug_in_check', 'Plugge den inn for å se hva som er på den', false, 1),
(get_question_id_by_order('data_protection', 14), 'report_security', 'Rapportere funnet til sikkerhetspersonell', true, 2),
(get_question_id_by_order('data_protection', 14), 'take_home', 'Ta den med hjem for sikker oppbevaring', false, 3);

-- Question 15 options (Email information - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('data_protection', 15), 'passwords', 'Passord eller påloggingsinformasjon', true, 1),
(get_question_id_by_order('data_protection', 15), 'personal_data', 'Personopplysninger om kunder', true, 2),
(get_question_id_by_order('data_protection', 15), 'financial_info', 'Finansiell informasjon', true, 3),
(get_question_id_by_order('data_protection', 15), 'meeting_times', 'Møtetidspunkter', false, 4);

-- Question 16 options (Cloud services security)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('data_protection', 16), 'strong_passwords', 'Sterke passord og MFA', true, 1),
(get_question_id_by_order('data_protection', 16), 'public_access', 'Gjøre filene offentlig tilgjengelige', false, 2),
(get_question_id_by_order('data_protection', 16), 'no_encryption', 'Ikke bruke kryptering for raskere tilgang', false, 3);

-- Question 17 options (Remote work connection)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('remote_work', 17), 'vpn_connection', 'Bruke bedriftens VPN', true, 1),
(get_question_id_by_order('remote_work', 17), 'direct_connection', 'Koble direkte til internett', false, 2),
(get_question_id_by_order('remote_work', 17), 'public_wifi', 'Bruke offentlig WiFi', false, 3);

-- Question 18 options (Cafe work)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('remote_work', 18), 'use_cafe_wifi', 'Bruke kafé-WiFi direkte', false, 1),
(get_question_id_by_order('remote_work', 18), 'mobile_hotspot', 'Bruke mobil hotspot eller VPN', true, 2),
(get_question_id_by_order('remote_work', 18), 'wait_until_home', 'Vente til jeg kommer hjem', false, 3);

-- Question 19 options (Home office security - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('remote_work', 19), 'secure_wifi', 'Sikre WiFi-nettverk med sterkt passord', true, 1),
(get_question_id_by_order('remote_work', 19), 'private_workspace', 'Privat arbeidsområde', true, 2),
(get_question_id_by_order('remote_work', 19), 'vpn_usage', 'Bruke VPN for bedriftstilgang', true, 3),
(get_question_id_by_order('remote_work', 19), 'shared_computer', 'Dele datamaskinen med familie', false, 4);

-- Question 20 options (Unsecured home WiFi)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('remote_work', 20), 'add_password', 'Legge til et sterkt passord umiddelbart', true, 1),
(get_question_id_by_order('remote_work', 20), 'continue_using', 'Fortsette å bruke det som det er', false, 2),
(get_question_id_by_order('remote_work', 20), 'hide_network', 'Bare skjule nettverksnavnet', false, 3);

-- Question 21 options (Suspected malware)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('incident_response', 21), 'disconnect_network', 'Koble fra nettverket og kontakte IT/Sikkerhet', true, 1),
(get_question_id_by_order('incident_response', 21), 'restart_continue', 'Starte datamaskinen på nytt og fortsette å jobbe', false, 2),
(get_question_id_by_order('incident_response', 21), 'remove_yourself', 'Prøve å fjerne de mistenkelige programmene selv', false, 3);

-- Question 22 options (Sent wrong information - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('incident_response', 22), 'contact_recipient', 'Kontakte mottakeren umiddelbart', true, 1),
(get_question_id_by_order('incident_response', 22), 'report_incident', 'Rapportere hendelsen til sikkerhetsteamet', true, 2),
(get_question_id_by_order('incident_response', 22), 'document_incident', 'Dokumentere hva som ble sendt', true, 3),
(get_question_id_by_order('incident_response', 22), 'ignore_hope', 'Ignorere det og håpe det går bra', false, 4);

-- Question 23 options (Tailgating)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('physical_security', 23), 'let_them_follow', 'La dem følge med siden de virker snille', false, 1),
(get_question_id_by_order('physical_security', 23), 'politely_stop', 'Høflig stoppe dem og be om identifikasjon', true, 2),
(get_question_id_by_order('physical_security', 23), 'ignore_continue', 'Ignorere dem og fortsette', false, 3);

-- Question 24 options (Physical security practices - multiple choice)
INSERT INTO question_options (question_id, option_value, option_text, is_correct, display_order) VALUES
(get_question_id_by_order('physical_security', 24), 'lock_screen', 'Låse skjermen når du forlater pulten', true, 1),
(get_question_id_by_order('physical_security', 24), 'secure_documents', 'Sikre fysiske dokumenter', true, 2),
(get_question_id_by_order('physical_security', 24), 'visitor_badges', 'Sørge for at besøkende har synlige merker', true, 3),
(get_question_id_by_order('physical_security', 24), 'prop_doors', 'Holde sikkerhetsdører åpne for bekvemmelighet', false, 4);

-- Drop the temporary function
DROP FUNCTION get_question_id_by_order(VARCHAR, INTEGER);
