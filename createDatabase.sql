CREATE TABLE users (
    u_username      CHAR(100) NOT NULL,
    u_pass          CHAR(100) NOT NULL
);

CREATE TABLE posts (
    p_title         CHAR(100) NOT NULL,
    p_contents      CHAR(100) NOT NULL,
    p_date          VARCHAR(500) NOT NULL,
    p_username      CHAR(100) NOT NULL,
    p_id            INTEGER(10000) NOT NULL
);

.mode "csv"
.separator ","
.headers off

.save data.sqlite