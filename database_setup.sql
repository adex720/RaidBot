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
