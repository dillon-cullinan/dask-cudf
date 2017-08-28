import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

import pygdf as gd
import dask_gdf as dgd
import dask.dataframe as dd


def test_from_pygdf():
    np.random.seed(0)

    df = pd.DataFrame({'x': np.random.randint(0, 5, size=10000),
                       'y': np.random.normal(size=10000)})

    gdf = gd.DataFrame.from_pandas(df)

    # Test simple around to/from dask
    ingested = dgd.from_pygdf(gdf, npartitions=2)
    assert_frame_equal(ingested.compute().to_pandas(), df)

    # Test conversion to dask.dataframe
    ddf = ingested.to_dask_dataframe()
    assert_frame_equal(ddf.compute(), df)


def test_query():
    np.random.seed(0)

    df = pd.DataFrame({'x': np.random.randint(0, 5, size=10),
                       'y': np.random.normal(size=10)})
    gdf = gd.DataFrame.from_pandas(df)
    expr = 'x > 2'

    assert_frame_equal(gdf.query(expr).to_pandas(), df.query(expr))

    queried = (dgd.from_pygdf(gdf, npartitions=2).query(expr))

    got = queried.compute().to_pandas()
    expect = gdf.query(expr).to_pandas()

    assert_frame_equal(got, expect)


def test_head():
    np.random.seed(0)
    df = pd.DataFrame({'x': np.random.randint(0, 5, size=100),
                       'y': np.random.normal(size=100)})
    gdf = gd.DataFrame.from_pandas(df)
    dgf = dgd.from_pygdf(gdf, npartitions=2)

    assert_frame_equal(dgf.head().to_pandas(), df.head())


def test_from_dask_dataframe():
    np.random.seed(0)
    df = pd.DataFrame({'x': np.random.randint(0, 5, size=20),
                       'y': np.random.normal(size=20)})
    ddf = dd.from_pandas(df, npartitions=2)
    dgdf = dgd.from_dask_dataframe(ddf)
    got = dgdf.compute().to_pandas()
    expect = df
    # Should the index be matching?
    assert (got.index != expect.index).any()
    np.testing.assert_array_equal(got.x.values, expect.x.values)
    np.testing.assert_array_equal(got.y.values, expect.y.values)