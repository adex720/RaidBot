CREATE TABLE manager_roles (id integer);

CREATE TABLE members (
    name mediumtext,
    tag mediumtext,
    hours integer,
    user_id mediumtext
);

CREATE TABLE memory (
    last_updated mediumtext,
    update_frequency mediumtext,
    info_channel mediumtext,
    reminder_channel mediumtext
);

CREATE TABLE missing(
    tag mediumtext,
    times integer,
    updated bool
);

INSERT INTO members (last_updated, update_frequency, info_channel, reminder_channel)
VALUES (0, 24, -1, -1);
