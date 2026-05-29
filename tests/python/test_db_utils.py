import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../analytics'))
from db_utils import query_to_df

def test_query_to_df(db_conn):
    df = query_to_df("SELECT COUNT(*) FROM users")
    assert df.shape[0] == 1
    assert int(df.iloc[0,0]) >= 0