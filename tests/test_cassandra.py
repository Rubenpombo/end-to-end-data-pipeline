import unittest
from cassandra.cluster import Cluster
from spark_stream import create_keyspace, create_table

class TestCassandra(unittest.TestCase):
    def setUp(self):
        """
        Set up a Cassandra connection for testing.
        """
        self.cluster = Cluster(['localhost'], port=9042)
        self.session = self.cluster.connect()

    def tearDown(self):
        """
        Close the Cassandra connection after tests.
        """
        self.cluster.shutdown()

    def test_create_keyspace(self):
        """
        Test that the keyspace is created successfully.
        """
        create_keyspace(self.session)
        keyspaces = list(self.cluster.metadata.keyspaces.keys())
        self.assertIn('spark_streams', keyspaces)

    def test_create_table(self):
        """
        Test that the table is created successfully.
        """
        create_table(self.session)
        tables = self.cluster.metadata.keyspaces['spark_streams'].tables
        self.assertIn('created_users', tables)

if __name__ == '__main__':
    unittest.main()