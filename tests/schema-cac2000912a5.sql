CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE people (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	identity VARCHAR(64) NOT NULL, 
	referrer_id VARCHAR(16), 
	privacy VARCHAR(8) DEFAULT 'public' NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(9) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(referrer_id) REFERENCES people (id), 
	UNIQUE (id), 
	UNIQUE (identity), 
	CHECK (status IN ('active', 'disabled', 'suspended'))
);
CREATE TABLE time_zone_name (
	id INTEGER NOT NULL, 
	name VARCHAR(32) NOT NULL, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (id), 
	UNIQUE (name), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE categories (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uid) REFERENCES people (id), 
	UNIQUE (id), 
	CONSTRAINT uniq_category_owner UNIQUE (name, uid), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE contacts (
	id VARCHAR(16) NOT NULL, 
	label VARCHAR(6) DEFAULT 'home' NOT NULL, 
	type VARCHAR(9) DEFAULT 'email' NOT NULL, 
	carrier VARCHAR(16), 
	info VARCHAR(255), 
	muted BOOLEAN DEFAULT 0 NOT NULL, 
	rank INTEGER DEFAULT '1' NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	privacy VARCHAR(8) DEFAULT 'member' NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(11) DEFAULT 'unconfirmed' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	UNIQUE (id), 
	CONSTRAINT uniq_info_type UNIQUE (info, type), 
	CHECK (label IN ('home', 'mobile', 'other', 'work')), 
	CHECK (type IN ('email', 'linkedin', 'location', 'messenger', 'slack', 'sms', 'voice', 'whatsapp')), 
	CHECK (muted IN (0, 1)), 
	CHECK (status IN ('active', 'unconfirmed', 'disabled'))
);
CREATE INDEX ix_contacts_uid ON contacts (uid);
CREATE TABLE grants (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(24) NOT NULL, 
	value VARCHAR(64) NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	expires TIMESTAMP, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	UNIQUE (id), 
	CONSTRAINT uniq_grant_user UNIQUE (name, uid), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE locations (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(255), 
	address VARCHAR(255), 
	city VARCHAR(64) NOT NULL, 
	state VARCHAR(16), 
	postalcode VARCHAR(12), 
	country VARCHAR(2) DEFAULT 'US' NOT NULL, 
	geolat INTEGER, 
	geolong INTEGER, 
	neighborhood VARCHAR(32), 
	privacy VARCHAR(8) DEFAULT 'public' NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	category_id VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uid) REFERENCES people (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	UNIQUE (id), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE directmessages (
	message_id VARCHAR(16) NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (message_id, uid), 
	FOREIGN KEY(message_id) REFERENCES messages (id) ON DELETE CASCADE, 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE
);
CREATE INDEX ix_directmessages_uid ON directmessages (uid);
CREATE TABLE lists (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	description TEXT, 
	privacy VARCHAR(8) DEFAULT 'public' NOT NULL, 
	category_id VARCHAR(16) NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	UNIQUE (id), 
	CONSTRAINT uniq_list_owner UNIQUE (name, uid), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE listmembers (
	uid VARCHAR(16) NOT NULL, 
	list_id VARCHAR(16) NOT NULL, 
	authorization VARCHAR(8) DEFAULT 'member' NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (uid, list_id), 
	FOREIGN KEY(list_id) REFERENCES lists (id) ON DELETE CASCADE, 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE
);
CREATE INDEX ix_listmembers_list_id ON listmembers (list_id);
CREATE TABLE listmessages (
	message_id VARCHAR(16) NOT NULL, 
	list_id VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (message_id, list_id), 
	FOREIGN KEY(list_id) REFERENCES lists (id) ON DELETE CASCADE, 
	FOREIGN KEY(message_id) REFERENCES messages (id) ON DELETE CASCADE
);
CREATE INDEX ix_listmessages_list_id ON listmessages (list_id);
CREATE TABLE accounts (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(32) NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	password BLOB NOT NULL, 
	password_must_change BOOLEAN DEFAULT 0 NOT NULL, 
	totp_secret BLOB, 
	is_admin BOOLEAN DEFAULT 0 NOT NULL, 
	settings_id VARCHAR(16) NOT NULL, 
	last_login TIMESTAMP, 
	invalid_attempts INTEGER DEFAULT '0' NOT NULL, 
	last_invalid_attempt TIMESTAMP, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(settings_id) REFERENCES settings (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	CONSTRAINT uniq_account_user UNIQUE (id, uid), 
	UNIQUE (name), 
	UNIQUE (uid), 
	UNIQUE (id), 
	CHECK (password_must_change IN (0, 1)), 
	CHECK (is_admin IN (0, 1)), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE credentials (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	vendor VARCHAR(32) NOT NULL, 
	type VARCHAR(16), 
	url VARCHAR(64), 
	"key" VARCHAR(128), 
	secret BLOB, 
	otherdata BLOB, 
	expires TIMESTAMP, 
	settings_id VARCHAR(16) NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	FOREIGN KEY(settings_id) REFERENCES settings (id), 
	UNIQUE (id), 
	CONSTRAINT uniq_name_uid UNIQUE (name, uid), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE storageitems (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(32) NOT NULL, 
	prefix VARCHAR(128), 
	bucket VARCHAR(64) NOT NULL, 
	region VARCHAR(16) DEFAULT 'us-east-2', 
	cdn_uri VARCHAR(64), 
	identifier VARCHAR(64), 
	privacy VARCHAR(8) DEFAULT 'public' NOT NULL, 
	credentials_id VARCHAR(16), 
	uid VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(credentials_id) REFERENCES credentials (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	UNIQUE (id), 
	CONSTRAINT uniq_storage_user UNIQUE (name, uid), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE pictures (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	path VARCHAR(64) DEFAULT '' NOT NULL, 
	caption VARCHAR(255), 
	uid VARCHAR(16) NOT NULL, 
	size BIGINT, 
	sha1 BLOB, 
	sha256 BLOB, 
	thumbnail50x50 BLOB, 
	format_original VARCHAR(4), 
	is_encrypted BOOLEAN DEFAULT 0 NOT NULL, 
	duration FLOAT, 
	compression VARCHAR(16), 
	datetime_original TIMESTAMP, 
	gps_altitude FLOAT, 
	geolat INTEGER, 
	geolong INTEGER, 
	height INTEGER, 
	make VARCHAR(16), 
	model VARCHAR(32), 
	orientation SMALLINT, 
	width INTEGER, 
	privacy VARCHAR(8) DEFAULT 'invitee' NOT NULL, 
	category_id VARCHAR(16) NOT NULL, 
	storage_id VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	FOREIGN KEY(storage_id) REFERENCES storageitems (id), 
	FOREIGN KEY(uid) REFERENCES people (id), 
	UNIQUE (id), 
	CHECK (format_original IN ('gif', 'heic', 'heif', 'ico', 'jpeg', 'mov', 'mp4', 'png', 'wmv')), 
	CHECK (is_encrypted IN (0, 1)), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE albums (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	sizes VARCHAR(32) DEFAULT '120,720' NOT NULL, 
	encryption VARCHAR(3), 
	password BLOB, 
	uid VARCHAR(16) NOT NULL, 
	list_id VARCHAR(16), 
	cover_id VARCHAR(16), 
	category_id VARCHAR(16) NOT NULL, 
	privacy VARCHAR(8) DEFAULT 'invitee' NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id), 
	FOREIGN KEY(cover_id) REFERENCES pictures (id), 
	FOREIGN KEY(list_id) REFERENCES lists (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	UNIQUE (id), 
	CONSTRAINT uniq_album_user UNIQUE (name, uid), 
	CHECK (encryption IN ('aes')), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE TABLE IF NOT EXISTS "messages" (
	id VARCHAR(16) NOT NULL, 
	content TEXT NOT NULL, 
	subject VARCHAR(128), 
	sender_id VARCHAR(16) NOT NULL, 
	recipient_id VARCHAR(16), 
	list_id VARCHAR(16), 
	privacy VARCHAR(8) DEFAULT 'secret' NOT NULL, 
	published BOOLEAN, 
	uid VARCHAR(16) NOT NULL, 
	viewed TIMESTAMP, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	album_id VARCHAR(16), 
	PRIMARY KEY (id), 
	CHECK (published IN (0, 1)), 
	CONSTRAINT messages_fk1 FOREIGN KEY(album_id) REFERENCES albums (id), 
	FOREIGN KEY(uid) REFERENCES people (id) ON DELETE CASCADE, 
	FOREIGN KEY(sender_id) REFERENCES people (id), 
	FOREIGN KEY(recipient_id) REFERENCES people (id), 
	UNIQUE (id)
);
CREATE TABLE IF NOT EXISTS "profileitems" (
	id VARCHAR(16) NOT NULL, 
	uid VARCHAR(16) NOT NULL, 
	item VARCHAR(9) NOT NULL, 
	value VARCHAR(32), 
	location_id VARCHAR(16), 
	tz_id INTEGER, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) NOT NULL, 
	album_id VARCHAR(16), 
	PRIMARY KEY (id), 
	CONSTRAINT uniq_itemuid UNIQUE (uid, item), 
	CONSTRAINT albums_fk1 FOREIGN KEY(album_id) REFERENCES albums (id), 
	FOREIGN KEY(uid) REFERENCES people (id), 
	UNIQUE (id), 
	FOREIGN KEY(tz_id) REFERENCES time_zone_name (id), 
	FOREIGN KEY(location_id) REFERENCES locations (id)
);
CREATE TABLE albumcontents (
	album_id VARCHAR(16) NOT NULL, 
	picture_id VARCHAR(16) NOT NULL, 
	rank FLOAT, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (album_id, picture_id), 
	FOREIGN KEY(album_id) REFERENCES albums (id) ON DELETE CASCADE, 
	FOREIGN KEY(picture_id) REFERENCES pictures (id) ON DELETE CASCADE
);
CREATE INDEX ix_albumcontents_picture_id ON albumcontents (picture_id);
CREATE TABLE files (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	path VARCHAR(64) NOT NULL, 
	mime_type VARCHAR(32) DEFAULT 'text/plain' NOT NULL, 
	size BIGINT, 
	sha1 BLOB, 
	sha256 BLOB, 
	storage_id VARCHAR(16), 
	privacy VARCHAR(8) DEFAULT 'member' NOT NULL, 
	list_id VARCHAR(16), 
	uid VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	status VARCHAR(8) DEFAULT 'active' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(storage_id) REFERENCES storageitems (id), 
	FOREIGN KEY(list_id) REFERENCES lists (id), 
	FOREIGN KEY(uid) REFERENCES people (id), 
	UNIQUE (id), 
	CHECK (status IN ('active', 'disabled'))
);
CREATE INDEX ix_files_uid ON files (uid);
CREATE TABLE messagefiles (
	file_id VARCHAR(16) NOT NULL, 
	message_id VARCHAR(16) NOT NULL, 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	PRIMARY KEY (file_id, message_id), 
	FOREIGN KEY(file_id) REFERENCES files (id) ON DELETE CASCADE, 
	FOREIGN KEY(message_id) REFERENCES messages (id) ON DELETE CASCADE
);
CREATE INDEX ix_messagefiles_message_id ON messagefiles (message_id);
CREATE TABLE IF NOT EXISTS "settings" (
	id VARCHAR(16) NOT NULL, 
	name VARCHAR(32) NOT NULL, 
	privacy VARCHAR(8) DEFAULT 'public' NOT NULL, 
	smtp_port INTEGER DEFAULT '587' NOT NULL, 
	smtp_smarthost VARCHAR(255), 
	smtp_credential_id VARCHAR(16), 
	country VARCHAR(2) DEFAULT 'US' NOT NULL, 
	lang VARCHAR(6) DEFAULT 'en_US' NOT NULL, 
	tz_id INTEGER DEFAULT '598' NOT NULL, 
	url VARCHAR(255), 
	window_title VARCHAR(127) DEFAULT 'Example apicrud Application', 
	default_cat_id VARCHAR(16) NOT NULL, 
	administrator_id VARCHAR(16) NOT NULL, 
	default_hostlist_id VARCHAR(16), 
	created TIMESTAMP DEFAULT (CURRENT_TIMESTAMP) NOT NULL, 
	modified TIMESTAMP, 
	default_storage_id VARCHAR(16), 
	PRIMARY KEY (id), 
	CONSTRAINT settings_fk1 FOREIGN KEY(smtp_credential_id) REFERENCES credentials (id), 
	CONSTRAINT settings_fk2 FOREIGN KEY(default_storage_id) REFERENCES storageitems (id), 
	FOREIGN KEY(administrator_id) REFERENCES people (id), 
	UNIQUE (id), 
	FOREIGN KEY(tz_id) REFERENCES time_zone_name (id), 
	FOREIGN KEY(default_cat_id) REFERENCES categories (id), 
	FOREIGN KEY(default_hostlist_id) REFERENCES lists (id)
);
INSERT INTO alembic_version (version_num) values ('cac2000912a5');
pragma foreign_keys=off;
INSERT INTO people VALUES('x-23450001','Example User','example@instantlinux.net',NULL,'public','2020-05-16 16:20:41',NULL,'active');
INSERT INTO categories VALUES('x-3423ceaf','default','x-23450001','2020-05-16 16:20:41',NULL,'active');
INSERT INTO contacts VALUES('x-4566a239','home','email',NULL,'example@instantlinux.net',1,1,'x-23450001','public','2020-05-16 16:20:41',NULL,'active');
INSERT INTO locations VALUES('x-67673434',NULL,'800 Dolores St.','San Francisco','CA',NULL,'US',377565030,-1224256710,'Mission District','public','x-23450001','x-3423ceaf','2020-05-16 16:20:41',NULL,'active');
INSERT INTO accounts VALUES('x-54320001','admin','x-23450001',X'305244354a73755931497636314c4975336c67754833334d697856666f33623144644457373273593448756d64486e6c6977637156582f7a70652b4d5039744e4f664352555852776d6f776f454f4c6b2f78546b467976306b5165413342434c6c48312b6f506857584e453d',0,NULL,1,'x-75023275',NULL,0,NULL,'2020-05-16 16:20:41',NULL,'active');
INSERT INTO settings VALUES('x-75023275','global','public',587,'smtp.gmail.com',NULL,'US','en_US',598,'http://localhost:3000','Example apicrud Application','x-3423ceaf','x-23450001',NULL,'2020-05-16 16:20:41',NULL,NULL);
INSERT INTO time_zone_name VALUES(309,'Asia/Shanghai','active');
INSERT INTO time_zone_name VALUES(315,'Asia/Tehran','active');
INSERT INTO time_zone_name VALUES(319,'Asia/Tokyo','active');
INSERT INTO time_zone_name VALUES(457,'Europe/Moscow','active');
INSERT INTO time_zone_name VALUES(460,'Europe/Paris','active');
INSERT INTO time_zone_name VALUES(464,'Europe/Rome','active');
INSERT INTO time_zone_name VALUES(591,'US/Central','active');
INSERT INTO time_zone_name VALUES(593,'US/Eastern','active');
INSERT INTO time_zone_name VALUES(597,'US/Mountain','active');
INSERT INTO time_zone_name VALUES(598,'US/Pacific','active');
INSERT INTO time_zone_name VALUES(601,'UTC','active');
