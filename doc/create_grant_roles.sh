psql postgres

CREATE USER processread WITH PASSWORD 'jii8ubise';
GRANT USAGE ON SCHEMA process TO processread;
GRANT SELECT ON ALL TABLES IN SCHEMA process TO processread;
GRANT USAGE ON SCHEMA regions TO processread;
GRANT SELECT ON regions.sites, regions.tracts, regions.defregions TO processread;

CREATE USER processmanage WITH PASSWORD '31tjiir8ubise';
GRANT USAGE ON SCHEMA process TO processmanage;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA process TO processmanage;

CREATE USER userread WITH PASSWORD 'jii8iuWH87HUDd';
GRANT USAGE ON SCHEMA userlocale TO userread;
GRANT SELECT ON ALL TABLES IN SCHEMA userlocale TO userread;
GRANT USAGE ON SCHEMA regions TO userread;
GRANT SELECT ON regions.tracts, regions.sites, regions.defregions TO userread;

CREATE USER manageuserproj WITH PASSWORD 'jWe-TW4-80m-JUH-';
GRANT USAGE ON SCHEMA userlocale TO manageuserproj;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA userlocale TO manageuserproj;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA userlocale TO manageuserproj;
GRANT USAGE ON SCHEMA regions TO manageuserproj;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA regions TO manageuserproj;
GRANT USAGE ON SCHEMA system TO manageuserproj;
GRANT SELECT ON system.regions,system.regioncats,system.defregions TO manageuserproj;
GRANT USAGE ON SCHEMA ancillary TO manageuserproj;
GRANT SELECT ON ALL TABLES IN SCHEMA ancillary TO manageuserproj;
GRANT USAGE ON SCHEMA modis TO manageuserproj;
GRANT SELECT ON modis.tilecoords TO manageuserproj;
GRANT SELECT, INSERT, UPDATE, DELETE ON modis.regions TO manageuserproj;


CREATE USER ManageLayout WITH PASSWORD 'jWE-TW4-90m-JUH-';
GRANT USAGE ON SCHEMA layout TO ManageLayout;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA layout TO ManageLayout;

CREATE USER managemodis WITH PASSWORD '95y-tbh-GgG-0BJ';
GRANT USAGE ON SCHEMA modis TO managemodis;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA modis TO managemodis;
GRANT USAGE ON SCHEMA regions TO managemodis;
GRANT SELECT ON ALL TABLES IN SCHEMA regions TO managemodis;
GRANT USAGE ON SCHEMA system TO managemodis;
GRANT SELECT ON ALL TABLES IN SCHEMA system TO managemodis;
GRANT USAGE ON SCHEMA regions TO managemodis;
GRANT SELECT ON ALL TABLES IN SCHEMA regions TO managemodis;
GRANT USAGE ON SCHEMA ancillary TO managemodis;
GRANT SELECT ON ALL TABLES IN SCHEMA ancillary TO managemodis;
GRANT USAGE ON SCHEMA smap TO managemodis;
GRANT SELECT ON ALL TABLES IN SCHEMA smap TO managemodis;
GRANT USAGE ON SCHEMA climateindex TO managemodis;
GRANT SELECT ON ALL TABLES IN SCHEMA climateindex TO managemodis;

CREATE USER manageregion WITH PASSWORD 'w94-388-uhH-5UH';
GRANT USAGE ON SCHEMA regions TO manageregion;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA REGIONS TO manageregion;
GRANT USAGE ON SCHEMA system TO manageregion;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA SYSTEM TO manageregion;
GRANT USAGE ON SCHEMA ancillary TO manageregion;
GRANT SELECT ON ALL TABLES IN SCHEMA ancillary TO manageregion;

CREATE USER manageancillary WITH PASSWORD 'w94-3R8-uhH-5CH';
GRANT USAGE ON SCHEMA system TO manageancillary;
GRANT SELECT ON ALL TABLES IN SCHEMA SYSTEM TO manageancillary;
GRANT USAGE ON SCHEMA ancillary TO manageancillary;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ancillary TO manageancillary;
GRANT USAGE ON SCHEMA climateindex TO manageancillary;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA climateindex TO manageancillary;

CREATE USER formatread WITH PASSWORD 'jii-8ub-ise';
GRANT USAGE ON SCHEMA process TO formatread;
GRANT SELECT ON process.celltypes, process.gdalformat TO formatread;

CREATE USER regionread WITH PASSWORD '84i-oOH-thf-tj1';
GRANT USAGE ON SCHEMA regions TO regionread;
GRANT SELECT ON ALL TABLES IN SCHEMA regions TO regionread;

CREATE USER managesoilmoisture WITH PASSWORD 'w84-3R8-uhH-5DH';
GRANT USAGE ON SCHEMA soilmoisture TO managesoilmoisture;
GRANT SELECT, INSERT, UPDATE, DELETE  ON ALL TABLES IN SCHEMA soilmoisture TO managesoilmoisture;
GRANT USAGE ON SCHEMA climateindex TO manageancillary;
GRANT SELECT ON ALL TABLES IN SCHEMA climateindex TO managesoilmoisture;

CREATE USER managesentinel WITH PASSWORD '95d-tBh-GuG-0mJ';
GRANT USAGE ON SCHEMA sentinel TO managesentinel;
GRANT SELECT, INSERT, UPDATE, DELETE  ON ALL TABLES IN SCHEMA sentinel TO managesentinel;
GRANT USAGE ON SCHEMA regions TO managesentinel;
GRANT SELECT ON ALL TABLES IN SCHEMA regions TO managesentinel;
GRANT USAGE ON SCHEMA system TO managesentinel;
GRANT SELECT ON ALL TABLES IN SCHEMA system TO managesentinel;

CREATE USER managelandsat WITH PASSWORD '95t-gBh-GuG-1RM';

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA landsat TO managelandsat;
GRANT SELECT, INSERT, UPDATE, DELETE  ON ALL TABLES IN SCHEMA landsat TO managelandsat;
GRANT USAGE ON SCHEMA regions TO managelandsat;
GRANT SELECT ON ALL TABLES IN SCHEMA regions TO managelandsat;
GRANT USAGE ON SCHEMA system TO managelandsat;
GRANT SELECT ON ALL TABLES IN SCHEMA system TO managelandsat;
GRANT USAGE ON SCHEMA ancillary TO managelandsat;
GRANT SELECT ON ALL TABLES IN SCHEMA ancillary TO managelandsat;


CREATE USER managesmap WITH PASSWORD '95t-gBh-GuG-6RM';
GRANT USAGE ON SCHEMA smap TO managesmap;
GRANT SELECT, INSERT, UPDATE, DELETE  ON ALL TABLES IN SCHEMA smap TO managesmap;
GRANT USAGE ON SCHEMA regions TO managesmap;
GRANT SELECT ON ALL TABLES IN SCHEMA regions TO managesmap;
GRANT USAGE ON SCHEMA system TO managesmap;
GRANT SELECT ON ALL TABLES IN SCHEMA system TO managesmap;
GRANT USAGE ON SCHEMA ancillary TO managesmap;
GRANT SELECT ON ALL TABLES IN SCHEMA ancillary TO managesmap;

CREATE USER manageexport WITH PASSWORD '98k-gBh-GuB-6RM';
GRANT USAGE ON SCHEMA system TO manageexport;
GRANT SELECT ON ALL TABLES IN SCHEMA system TO manageexport;
GRANT USAGE ON SCHEMA ancillary TO manageexport;
GRANT SELECT ON ALL TABLES IN SCHEMA ancillary TO manageexport;
GRANT USAGE ON SCHEMA smap TO manageexport;
GRANT SELECT  ON ALL TABLES IN SCHEMA smap TO manageexport;
GRANT USAGE ON SCHEMA landsat TO manageexport;
GRANT SELECT  ON ALL TABLES IN SCHEMA modis TO manageexport;
GRANT USAGE ON SCHEMA modis TO manageexport;
GRANT SELECT  ON ALL TABLES IN SCHEMA modis TO manageexport;
GRANT USAGE ON SCHEMA regions TO manageexport;
GRANT SELECT  ON ALL TABLES IN SCHEMA regions TO manageexport;
GRANT USAGE ON SCHEMA layout TO manageexport;
GRANT SELECT  ON ALL TABLES IN SCHEMA layout TO manageexport;
