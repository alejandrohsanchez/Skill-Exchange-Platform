CREATE TABLE users (
    u_username      CHAR(100) NOT NULL,
    u_pass          CHAR(100) NOT NULL
);

CREATE TABLE files (
    f_name          CHAR(100) NOT NULL,
    f_username      CHAR(100) NOT NULL,
    f_id            INTEGER(10000) NOT NULL
);

CREATE TABLE posts (
    p_name          CHAR(100) NOT NULL,
    p_header        CHAR(100) NOT NULL,
    p_summary       VARCHAR(500) NOT NULL,
    p_date          CHAR(100) NOT NULL,
    p_username      CHAR(100) NOT NULL,
    p_id            INTEGER(10000) NOT NULL
);

.mode "csv"
.separator ","
.headers off

.save data.sqlite