CREATE TABLE users (
    u_username      CHAR(100) NOT NULL,
    u_pass          CHAR(100) NOT NULL,
    u_email         VARCHAR(255) NOT NULL
);

CREATE TABLE posts (
    p_title         CHAR(100) NOT NULL,
    p_contents      VARCHAR(255) NOT NULL,
    p_date          CHAR(100) NOT NULL,
    p_username      CHAR(100) NOT NULL,
    p_id            INTEGER(10000) NOT NULL
);

CREATE TABLE replies (
    r_contents      VARCHAR(255) NOT NULL,
    r_date          CHAR(100) NOT NULL,
    r_author        CHAR(100) NOT NULL,
    r_id            INTEGER(10000) NOT NULL,
    r_repID         INTEGER(10000) NOT NULL
);

.mode "csv"
.separator ","
.headers off

.save data.sqlite