from pyspark.sql import SparkSession


spark = SparkSession.builder.appName('plane_tracker').getOrCreate()