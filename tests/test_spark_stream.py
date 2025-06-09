import unittest
from pyspark.sql import SparkSession
from spark_stream import create_selection_df_from_kafka

class TestSparkStream(unittest.TestCase):
    def setUp(self):
        """
        Set up a Spark session for testing.
        """
        self.spark = SparkSession.builder \
            .appName("TestSpark") \
            .master("local[1]") \
            .getOrCreate()

    def tearDown(self):
        """
        Stop the Spark session after tests.
        """
        self.spark.stop()

    def test_create_selection_df_from_kafka(self):
        """
        Test that the function parses Kafka messages into a structured DataFrame.
        """
        data = [{"value": '{"id": "123", "first_name": "John", "last_name": "Doe", "gender": "male"}'}]
        df = self.spark.createDataFrame(data, schema=["value"])
        result_df = create_selection_df_from_kafka(df)
        self.assertEqual(result_df.count(), 1)  # Ensure one record is parsed
        self.assertIn("id", result_df.columns)  # Ensure 'id' column exists

if __name__ == '__main__':
    unittest.main()