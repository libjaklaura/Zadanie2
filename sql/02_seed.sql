TRUNCATE accounts, products, lab_users, books, shipments, reviews RESTART IDENTITY CASCADE;
INSERT INTO accounts(username,password,role) VALUES ('administrator','Campus-Admin-2026!','Administrator'),('student','LibraryPass-42','Student');
INSERT INTO products(name,price,description) VALUES ('Northstar Ultra Laptop',899.00,'A fictional 14-inch university laptop with a quiet keyboard and all-day battery.');
INSERT INTO lab_users(username,email,department) VALUES ('mira.ko','mira.ko@example.invalid','Computer Science'),('jonas.reed','jonas.reed@example.invalid','History');
INSERT INTO books(title,author,publication_year,available) VALUES ('The Quiet Protocol','Eleanor Voss',2021,true),('Networks at Dusk','Pavel North',2018,false);
INSERT INTO shipments(tracking_number,status) VALUES ('PT-10001','In transit'),('PT-10002','Delivered');
INSERT INTO reviews(product_id,reviewer_name,review_text) VALUES (1,'Demo visitor','A reliable fictional laptop for coursework.');

