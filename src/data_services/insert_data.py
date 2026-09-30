from src.data_services.sparkutil import spark
from pyspark.sql import functions as F
from src.api.api_client import get_data
from pyspark.sql.types import *
from src.db_settings.connection import WorkwithDB
from psycopg2.extras import execute_values


class InsertData:
    def extract_data(self):
        self.data = get_data()
        self.time = self.data["time"]
        return self.data

    
    def data_frame_normalize(self, data = None, path = None):
        if data is None:
            data = self.extract_data()
        
        
        def normalize(r):
            '''в будущем переделать на spark'''
            float_index = [5, 6, 7, 9, 10, 11, 13]
            r = list(r)
            if len(r) != 17:
                raise IndexError
            r[0] = r[0].strip().lower() if r[0] is not None else r[0]
            r[1] = r[1].strip().lower() if r[1] is not None else r[1]
            r[2] = r[2].strip().lower() if r[2] is not None else r[2]
            for i in float_index:
                if r[i] is not None:
                    r[i] = float(r[i])
            return r
        
        self.schema = StructType([
                            StructField("icao24", StringType()),
                            StructField("callsign", StringType()),
                            StructField("origin_country", StringType()),
                            StructField("time_position", LongType()),
                            StructField("last_contact", LongType()),
                            StructField("longitude", DoubleType()),
                            StructField("latitude", DoubleType()),
                            StructField("baro_altitude", DoubleType()),
                            StructField("on_ground", BooleanType()),
                            StructField("velocity", DoubleType()),
                            StructField("true_track", DoubleType()),
                            StructField("vertical_rate", DoubleType()),
                            StructField("sensors", ArrayType(IntegerType())),
                            StructField("geo_altitude", DoubleType()),
                            StructField("squawk", StringType()),
                            StructField("spi", BooleanType()),
                            StructField("position_source", IntegerType()),
                        ])
        rows = [normalize(r) for r in data["states"]]
        df1 = spark.createDataFrame(rows, schema=self.schema)
        df_normalize = (
            df1
            .select(
                "icao24", "callsign", "origin_country",
                F.col("time_position").cast("timestamp").alias("time_position"),
                F.col("last_contact").cast("timestamp").alias("last_contact"),
                "longitude", "latitude", "geo_altitude",
                F.col("velocity").cast("decimal(6,2)").alias("velocity"),
                "true_track",
                F.round("vertical_rate").cast("int").alias("vertical_rate"),
                F.col("squawk").alias("squawk_name"),
                "on_ground")
            .filter(
                F.col("icao24").isNotNull() & (F.length("icao24") == 6)
                &
                F.col('time_position').isNotNull()
                &
                F.col('last_contact').isNotNull()
                &
                F.col('longitude').isNotNull()
                &
                F.col('latitude').isNotNull()
                &
                F.col('longitude').between(-180, 180)
                &
                F.col('latitude').between(-90, 90)
            )).distinct()
        if path:
            return df_normalize.write.mode('overwrite').parquet(path)
        else:
            return df_normalize

    def inserttodb(self, df_data = None, path = None, time = None):
        if path is None:
            df_data = self.data_frame_normalize().collect()
        else:
            df_data = spark.read.parquet(path).collect()
        if time is None:
            time = self.time
        con = WorkwithDB().con
        try:
            with con:
                with con.cursor() as cur:
                    #api_get
                    cur.execute(
                        "insert into api_get (api_time) values (to_timestamp(%s)) returning id",
                        (time, ),
                    )
                    api_id = cur.fetchone()[0]

                    
                    #aircraft
                    aircraft = [(i['icao24'], i['origin_country']) for i in df_data]
                    execute_values(
                        cur,
                        "insert into aircraft (icao24, origin_country) values %s on conflict (icao24) do nothing",
                        aircraft,
                    )

                    #squawk_status
                    squawks = [(i['squawk_name'], 'иной код') for i in df_data if i['squawk_name']]
                    execute_values(
                        cur,
                        "insert into squawk_status (squawk_name, sq_status) values %s on conflict (squawk_name) do nothing",
                        squawks,
                    )
                    cur.execute("select squawk_name, id from squawk_status")
                    sq_id = dict(cur.fetchall())


                    #aircraft_states
                    data_states = [(
                                api_id,
                                i['icao24'],
                                i['callsign'],
                                i['time_position'],
                                i['last_contact'],
                                i['longitude'],
                                i['latitude'],
                                i['geo_altitude'],
                                i['velocity'],
                                i['true_track'],
                                i['vertical_rate'],
                                sq_id.get(i['squawk_name']),
                                i['on_ground']) for i in df_data]
                    execute_values(
                        cur,
                        """insert into aircraft_states
                            (api_id, icao24, callsign, time_position, last_contact,
                            longitude, latitude, geo_altitude, velocity,
                            true_track, vertical_rate, squawk_id, on_ground) values %s""",
                            data_states,
                            page_size=1000
                    )
        finally:
            con.close()






            
