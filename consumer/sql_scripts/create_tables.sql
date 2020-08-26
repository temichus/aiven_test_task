

CREATE TABLE monitor.signal_data (
    signal_id integer NOT NULL,
    status smallint,
    response_time real,
    time_code timestamp without time zone NOT NULL,
    regex_found boolean
);


CREATE TABLE monitor.signal_type (
    id integer NOT NULL,
    url_id integer NOT NULL,
    regex character varying(1000)
);



CREATE SEQUENCE monitor.signal_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE monitor.signal_type_id_seq OWNED BY monitor.signal_type.id;


CREATE TABLE monitor.website_url (
    id integer NOT NULL,
    url character varying(1000) NOT NULL
);


CREATE SEQUENCE monitor.website_url_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE monitor.website_url_id_seq OWNED BY monitor.website_url.id;



ALTER TABLE ONLY monitor.signal_type ALTER COLUMN id SET DEFAULT nextval('monitor.signal_type_id_seq'::regclass);



ALTER TABLE ONLY monitor.website_url ALTER COLUMN id SET DEFAULT nextval('monitor.website_url_id_seq'::regclass);


ALTER TABLE ONLY monitor.signal_data
    ADD CONSTRAINT signal_data_pkey PRIMARY KEY (signal_id, time_code);


ALTER TABLE ONLY monitor.signal_type
    ADD CONSTRAINT signal_type_pkey PRIMARY KEY (id);


ALTER TABLE ONLY monitor.website_url
    ADD CONSTRAINT website_url_pkey PRIMARY KEY (id);


ALTER TABLE ONLY monitor.signal_data
    ADD CONSTRAINT fk_signal_type FOREIGN KEY (signal_id) REFERENCES monitor.signal_type(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


ALTER TABLE ONLY monitor.signal_type
    ADD CONSTRAINT fk_website_url FOREIGN KEY (url_id) REFERENCES monitor.website_url(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


