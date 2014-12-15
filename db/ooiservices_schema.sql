--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

-- Structure for table arrays (OID = 18401):
SET search_path = public, pg_catalog;

--
-- SEQUENCES
--
CREATE SEQUENCE arrays_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence deployments_id_seq (OID = 18412):
CREATE SEQUENCE deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence instrument_deployments_id_seq (OID = 18420):
CREATE SEQUENCE instrument_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence instruments_id_seq (OID = 18428):
CREATE SEQUENCE instruments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence platform_deployments_id_seq (OID = 18436):
CREATE SEQUENCE platform_deployments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence platforms_id_seq (OID = 18444):
CREATE SEQUENCE platforms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence stream_parameters_id_seq (OID = 18452):
CREATE SEQUENCE stream_parameters_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence streams_id_seq (OID = 18460):
CREATE SEQUENCE streams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence assets_id_seq (OID = 18676):
CREATE SEQUENCE assets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence asset_types_id_seq (OID = 18687):
CREATE SEQUENCE asset_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence organizations_id_seq (OID = 18708):
CREATE SEQUENCE organizations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence stream_parameter_link_id_seq (OID = 18724):
CREATE SEQUENCE stream_parameter_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence installation_record_id_seq (OID = 18743):
CREATE SEQUENCE installation_record_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence asssemblies_id_seq (OID = 18760):
CREATE SEQUENCE asssemblies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence instrument_models_id_seq (OID = 18776):
CREATE SEQUENCE instrument_models_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence inspection_status_id_seq (OID = 18792):
CREATE SEQUENCE inspection_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence files_id_seq (OID = 18808):
CREATE SEQUENCE files_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence asset_file_link_id_seq (OID = 18829):
CREATE SEQUENCE asset_file_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence drivers_id_seq (OID = 18847):
CREATE SEQUENCE drivers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence driver_stream_link_id_seq (OID = 18863):
CREATE SEQUENCE driver_stream_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence datasets_id_seq (OID = 18892):
CREATE SEQUENCE datasets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence dataset_keywords_id_seq (OID = 18904):
CREATE SEQUENCE dataset_keywords_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;
-- Definition for sequence manufacturers_id_seq (OID = 18931):
CREATE SEQUENCE manufacturers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

--
-- TABLES
--
CREATE TABLE arrays (
    id integer DEFAULT nextval('arrays_id_seq'::regclass) NOT NULL,
    array_code text,
    description text,
    geo_location geography(Polygon,4326),
    array_name text
) WITHOUT OIDS;
-- Structure for table deployments (OID = 18409):
CREATE TABLE deployments (
    id integer DEFAULT nextval('deployments_id_seq'::regclass) NOT NULL,
    start_date date,
    end_date date,
    cruise_id integer
) WITHOUT OIDS;
-- Structure for table instrument_deployments (OID = 18414):
CREATE TABLE instrument_deployments (
    id integer DEFAULT nextval('instrument_deployments_id_seq'::regclass) NOT NULL,
    display_name text,
    start_date date,
    end_date date,
    platform_deployment_id integer,
    instrument_id integer,
    reference_designator text,
    depth real,
    geo_location geography(Point,4326)
) WITHOUT OIDS;
-- Structure for table instruments (OID = 18422):
CREATE TABLE instruments (
    id integer DEFAULT nextval('instruments_id_seq'::regclass) NOT NULL,
    instrument_name text,
    description text,
    location_description text,
    instrument_series text,
    serial_number text,
    display_name text,
    model_id integer NOT NULL,
    asset_id integer NOT NULL,
    depth_rating real,
    manufacturer_id integer
) WITHOUT OIDS;
-- Structure for table platform_deployments (OID = 18430):
CREATE TABLE platform_deployments (
    id integer DEFAULT nextval('platform_deployments_id_seq'::regclass) NOT NULL,
    start_date date,
    end_date date,
    platform_id integer,
    reference_designator text NOT NULL,
    array_id integer,
    deployment_id integer,
    display_name text,
    geo_location geography(Point,4326)
) WITHOUT OIDS;
-- Structure for table platforms (OID = 18438):
CREATE TABLE platforms (
    id integer DEFAULT nextval('platforms_id_seq'::regclass) NOT NULL,
    platform_name text,
    description text,
    location_description text,
    platform_series text,
    is_mobile boolean NOT NULL,
    serial_no text,
    asset_id integer NOT NULL,
    manufacturer_id integer
) WITHOUT OIDS;
-- Structure for table stream_parameters (OID = 18446):
CREATE TABLE stream_parameters (
    id integer DEFAULT nextval('stream_parameters_id_seq'::regclass) NOT NULL,
    stream_parameter_name text,
    short_name text,
    long_name text,
    standard_name text,
    units text,
    data_type text
) WITHOUT OIDS;
-- Structure for table streams (OID = 18454):
CREATE TABLE streams (
    id integer DEFAULT nextval('streams_id_seq'::regclass) NOT NULL,
    stream_name text,
    instrument_id integer,
    description text
) WITHOUT OIDS;
-- Structure for table assets (OID = 18678):
CREATE TABLE assets (
    id integer DEFAULT nextval('assets_id_seq'::regclass) NOT NULL,
    asset_type_id integer NOT NULL,
    organization_id integer NOT NULL,
    supplier_id integer NOT NULL,
    deployment_id integer,
    asset_name text NOT NULL,
    model text,
    current_lifecycle_state text,
    part_number text,
    firmware_version text,
    geo_location geography(Point,4326)
) WITHOUT OIDS;
-- Structure for table asset_types (OID = 18689):
CREATE TABLE asset_types (
    id integer DEFAULT nextval('asset_types_id_seq'::regclass) NOT NULL,
    asset_type_name text NOT NULL
) WITHOUT OIDS;
-- Structure for table organizations (OID = 18710):
CREATE TABLE organizations (
    id integer DEFAULT nextval('organizations_id_seq'::regclass) NOT NULL,
    organization_name text NOT NULL
) WITHOUT OIDS;
-- Structure for table stream_parameter_link (OID = 18726):
CREATE TABLE stream_parameter_link (
    id integer DEFAULT nextval('stream_parameter_link_id_seq'::regclass) NOT NULL,
    stream_id integer NOT NULL,
    parameter_id integer NOT NULL
) WITHOUT OIDS;
-- Structure for table installation_record (OID = 18745):
CREATE TABLE installation_record (
    id integer DEFAULT nextval('installation_record_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    assembly_id integer NOT NULL,
    date_installed date,
    date_removed date,
    technician_name text,
    comments text,
    file_id integer
) WITHOUT OIDS;
-- Structure for table asssemblies (OID = 18762):
CREATE TABLE asssemblies (
    id integer DEFAULT nextval('asssemblies_id_seq'::regclass) NOT NULL,
    assembly_name text NOT NULL,
    description text
) WITHOUT OIDS;
-- Structure for table instrument_models (OID = 18778):
CREATE TABLE instrument_models (
    id integer DEFAULT nextval('instrument_models_id_seq'::regclass) NOT NULL,
    instrument_model_name text NOT NULL,
    series_name text,
    class_name text,
    manufacturer_id integer
) WITHOUT OIDS;
-- Structure for table inspection_status (OID = 18794):
CREATE TABLE inspection_status (
    id integer DEFAULT nextval('inspection_status_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer,
    status text,
    technician_name text,
    comments text,
    inspection_date date,
    document text
) WITHOUT OIDS;
-- Structure for table files (OID = 18810):
CREATE TABLE files (
    id integer DEFAULT nextval('files_id_seq'::regclass) NOT NULL,
    user_id integer,
    file_name text NOT NULL,
    file_system_path text,
    file_size text,
    file_permissions text,
    file_type text
) WITHOUT OIDS;
-- Structure for table asset_file_link (OID = 18831):
CREATE TABLE asset_file_link (
    id integer DEFAULT nextval('asset_file_link_id_seq'::regclass) NOT NULL,
    asset_id integer NOT NULL,
    file_id integer NOT NULL
) WITHOUT OIDS;
-- Structure for table drivers (OID = 18849):
CREATE TABLE drivers (
    id integer DEFAULT nextval('drivers_id_seq'::regclass) NOT NULL,
    instrument_id integer,
    driver_name text NOT NULL,
    driver_version text,
    author text
) WITHOUT OIDS;
-- Structure for table driver_stream_link (OID = 18865):
CREATE TABLE driver_stream_link (
    id integer DEFAULT nextval('driver_stream_link_id_seq'::regclass) NOT NULL,
    driver_id integer NOT NULL,
    stream_id integer NOT NULL
) WITHOUT OIDS;
-- Structure for table datasets (OID = 18894):
CREATE TABLE datasets (
    id integer DEFAULT nextval('datasets_id_seq'::regclass) NOT NULL,
    stream_id integer NOT NULL,
    deployment_id integer NOT NULL,
    process_level text,
    is_recovered boolean DEFAULT false NOT NULL
) WITHOUT OIDS;
-- Structure for table dataset_keywords (OID = 18906):
CREATE TABLE dataset_keywords (
    id integer DEFAULT nextval('dataset_keywords_id_seq'::regclass) NOT NULL,
    dataset_id integer NOT NULL,
    concept_name text,
    concept_description text
) WITHOUT OIDS;
-- Structure for table manufacturers (OID = 18933):
CREATE TABLE manufacturers (
    id integer DEFAULT nextval('manufacturers_id_seq'::regclass) NOT NULL,
    manufacturer_name text NOT NULL,
    phone_number text,
    contact_name text,
    web_address text
) WITHOUT OIDS;

--
-- CONSTRAINTS
--
-- Definition for index arrays_pkey (OID = 18470):
ALTER TABLE ONLY arrays
    ADD CONSTRAINT arrays_pkey PRIMARY KEY (id);
-- Definition for index deployments_pkey (OID = 18472):
ALTER TABLE ONLY deployments
    ADD CONSTRAINT deployments_pkey PRIMARY KEY (id);
-- Definition for index instrument_deployments_pkey (OID = 18474):
ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_pkey PRIMARY KEY (id);
-- Definition for index instruments_pkey (OID = 18476):
ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_pkey PRIMARY KEY (id);
-- Definition for index platform_deployments_pkey (OID = 18478):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_pkey PRIMARY KEY (id);
-- Definition for index platforms_pkey (OID = 18480):
ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_pkey PRIMARY KEY (id);
-- Definition for index stream_parameters_pkey (OID = 18482):
ALTER TABLE ONLY stream_parameters
    ADD CONSTRAINT stream_parameters_pkey PRIMARY KEY (id);
-- Definition for index streams_pkey (OID = 18484):
ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_pkey PRIMARY KEY (id);
-- Definition for index instrument_deployments_instrument_id_fkey (OID = 18491):
ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);
-- Definition for index instrument_deployments_platform_deployment_id_fkey (OID = 18496):
ALTER TABLE ONLY instrument_deployments
    ADD CONSTRAINT instrument_deployments_platform_deployment_id_fkey FOREIGN KEY (platform_deployment_id) REFERENCES platform_deployments(id);
-- Definition for index platform_deployments_array_id_fkey (OID = 18501):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_array_id_fkey FOREIGN KEY (array_id) REFERENCES arrays(id);
-- Definition for index platform_deployments_deployment_id_fkey (OID = 18506):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_deployment_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);
-- Definition for index platform_deployments_platform_id_fkey (OID = 18511):
ALTER TABLE ONLY platform_deployments
    ADD CONSTRAINT platform_deployments_platform_id_fkey FOREIGN KEY (platform_id) REFERENCES platforms(id);
-- Definition for index streams_instrument_id_fkey (OID = 18521):
ALTER TABLE ONLY streams
    ADD CONSTRAINT streams_instrument_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);
-- Definition for index assets_pkey (OID = 18685):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);
-- Definition for index asset_types_pkey (OID = 18696):
ALTER TABLE ONLY asset_types
    ADD CONSTRAINT asset_types_pkey PRIMARY KEY (id);
-- Definition for index organizations_pkey (OID = 18717):
ALTER TABLE ONLY organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);
-- Definition for index assets_organization_id_organizations_id_fkey (OID = 18719):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_organization_id_organizations_id_fkey FOREIGN KEY (organization_id) REFERENCES organizations(id);
-- Definition for index stream_parameter_link_pkey (OID = 18730):
ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_pkey PRIMARY KEY (id);
-- Definition for index installation_record_pkey (OID = 18752):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_pkey PRIMARY KEY (id);
-- Definition for index asssemblies_pkey (OID = 18769):
ALTER TABLE ONLY asssemblies
    ADD CONSTRAINT asssemblies_pkey PRIMARY KEY (id);
-- Definition for index instrument_models_pkey (OID = 18785):
ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT instrument_models_pkey PRIMARY KEY (id);
-- Definition for index instruments_model_id.inst_models_id_fkey (OID = 18787):
ALTER TABLE ONLY instruments
    ADD CONSTRAINT "instruments_model_id.inst_models_id_fkey" FOREIGN KEY (model_id) REFERENCES instrument_models(id);
-- Definition for index inspection_status_pkey (OID = 18801):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_pkey PRIMARY KEY (id);
-- Definition for index files_pkey (OID = 18817):
ALTER TABLE ONLY files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);
-- Definition for index asset_file_link_pkey (OID = 18835):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_pkey PRIMARY KEY (id);
-- Definition for index drivers_pkey (OID = 18856):
ALTER TABLE ONLY drivers
    ADD CONSTRAINT drivers_pkey PRIMARY KEY (id);
-- Definition for index driver_stream_link_pkey (OID = 18869):
ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_pkey PRIMARY KEY (id);
-- Definition for index datasets_pkey (OID = 18902):
ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_pkey PRIMARY KEY (id);
-- Definition for index dataset_keywords_pkey (OID = 18913):
ALTER TABLE ONLY dataset_keywords
    ADD CONSTRAINT dataset_keywords_pkey PRIMARY KEY (id);
-- Definition for index manufacturers_pkey (OID = 18940):
ALTER TABLE ONLY manufacturers
    ADD CONSTRAINT manufacturers_pkey PRIMARY KEY (id);
-- Definition for index platforms_manufacturer_id_manufacturers_id_fkey (OID = 18942):
ALTER TABLE ONLY platforms
    ADD CONSTRAINT platforms_manufacturer_id_manufacturers_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);
-- Definition for index instruments_manufacturer_id_manufacturers_id_fkey (OID = 18947):
ALTER TABLE ONLY instruments
    ADD CONSTRAINT instruments_manufacturer_id_manufacturers_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);
-- Definition for index inst_models_manufacturer_id_manufacturer_id_fkey (OID = 18952):
ALTER TABLE ONLY instrument_models
    ADD CONSTRAINT inst_models_manufacturer_id_manufacturer_id_fkey FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id);
-- Definition for index drivers_instrument_id_instruments_id_fkey (OID = 18957):
ALTER TABLE ONLY drivers
    ADD CONSTRAINT drivers_instrument_id_instruments_id_fkey FOREIGN KEY (instrument_id) REFERENCES instruments(id);
-- Definition for index driver_stream_link_driver_id_drivers_id_fkey (OID = 18962):
ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_driver_id_drivers_id_fkey FOREIGN KEY (driver_id) REFERENCES drivers(id);
-- Definition for index driver_stream_link_stream_id_streams_id_fkey (OID = 18967):
ALTER TABLE ONLY driver_stream_link
    ADD CONSTRAINT driver_stream_link_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);
-- Definition for index datasets_deployment_id_deployments_id_fkey (OID = 18972):
ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_deployment_id_deployments_id_fkey FOREIGN KEY (deployment_id) REFERENCES deployments(id);
-- Definition for index datasets_stream_id_streams_id_fkey (OID = 18977):
ALTER TABLE ONLY datasets
    ADD CONSTRAINT datasets_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);
-- Definition for index stream_parameter_link_stream_id_streams_id_fkey (OID = 18982):
ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_stream_id_streams_id_fkey FOREIGN KEY (stream_id) REFERENCES streams(id);
-- Definition for index stream_parameter_link_parameter_id_parameters_id_fkey (OID = 18987):
ALTER TABLE ONLY stream_parameter_link
    ADD CONSTRAINT stream_parameter_link_parameter_id_parameters_id_fkey FOREIGN KEY (parameter_id) REFERENCES stream_parameters(id);
-- Definition for index dataset_keywords_dataset_id_datasets_id_fkey (OID = 18992):
ALTER TABLE ONLY dataset_keywords
    ADD CONSTRAINT dataset_keywords_dataset_id_datasets_id_fkey FOREIGN KEY (dataset_id) REFERENCES datasets(id);
-- Definition for index installation_record_assembly_id_assemblies_id_fkey (OID = 18997):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_assembly_id_assemblies_id_fkey FOREIGN KEY (assembly_id) REFERENCES asssemblies(id);
-- Definition for index installation_record_file_id_files_id_fkey (OID = 19002):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index installation_record_asset_id_assets_id_fkey (OID = 19007):
ALTER TABLE ONLY installation_record
    ADD CONSTRAINT installation_record_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index inspection_status_asset_id_assets_id_fkey (OID = 19012):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index assets_asset_type_id_asset_types_id_fkey (OID = 19017):
ALTER TABLE ONLY assets
    ADD CONSTRAINT assets_asset_type_id_asset_types_id_fkey FOREIGN KEY (asset_type_id) REFERENCES asset_types(id);
-- Definition for index asset_file_link_asset_id_assets_id_fkey (OID = 19022):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_asset_id_assets_id_fkey FOREIGN KEY (asset_id) REFERENCES assets(id);
-- Definition for index asset_file_link_file_id_files_id_fkey (OID = 19027):
ALTER TABLE ONLY asset_file_link
    ADD CONSTRAINT asset_file_link_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);
-- Definition for index inspection_status_file_id_files_id_fkey (OID = 19032):
ALTER TABLE ONLY inspection_status
    ADD CONSTRAINT inspection_status_file_id_files_id_fkey FOREIGN KEY (file_id) REFERENCES files(id);

--
-- COMMENTS
--
COMMENT ON COLUMN assets.deployment_id IS 'Current deployment';
COMMENT ON COLUMN files.file_size IS 'MB';

--
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM luke;
GRANT ALL ON SCHEMA public TO luke;
GRANT ALL ON SCHEMA public TO PUBLIC;
