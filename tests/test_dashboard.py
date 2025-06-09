import unittest
from dashboard import get_cassandra_data

class TestDashboard(unittest.TestCase):
    def test_get_cassandra_data(self):
        """
        Test that the function retrieves data from Cassandra and returns a DataFrame.
        """
        df = get_cassandra_data()
        self.assertIsNotNone(df, "The DataFrame returned is None.")

        if df.empty:
            print("Warning: The DataFrame is empty. This may be because the DAG has not been activated yet.")
        else:
            self.assertIn('id', df.columns, "The 'id' column is missing from the DataFrame.")

if __name__ == '__main__':
    unittest.main()