import pytest
import pandas as pd
import numpy as np
from mtbp3cd.util.gt03summary import pd_df_flag_to_category, crosstab_from_lists, geo_mean_sd_by_group
import unittest

class TestUtilGt03Summary(unittest.TestCase):
    def setUp(self):
        self.df_flags_0 = pd.DataFrame({
            'A_fl': ['N', 'Y', 'Y', 'N', None, 'X'],
            'B_fl': ['', 'Y', 'Y', 'N', None, 'X'],
            'B': [1, 2, 3, 4, 5, 6]
        })
        self.df_flags_1 = pd.DataFrame({
            'A_fl': ['N', 'Y', 'Y', 'N', None, 'X'],
            'B_fl': ['', 'Y', 'Y', 'N', None, 'X'],
            'B': [1, 2, 3, 4, 5, 6]
        })
        pd_df_flag_to_category(self.df_flags_1)
        self.df_flags_2 = pd.DataFrame({
            'A_fl': ['N', 'Y', None, 'Y', 'N', 'X', None],
            'B': [1, 2, 3, 4, 5, 6, 7]
        })
        self.df_crosstab = pd.DataFrame({
            'A': ['foo', 'foo', 'bar', 'bar'],
            'B': ['one', 'two', 'one', 'two'],
            'C': [1, 2, 3, 4]
        })
        self.df_geo = pd.DataFrame({
            'group': ['A', 'A', 'B', 'B'],
            'value': [1, 2, 3, 4]
        })

    def test_1_pd_df_flag_to_category_with_missing_values(self):
        cats = list(self.df_flags_1['A_fl'].cat.categories)
        self.assertIn("Y", cats)
        self.assertIn("N", cats)
        self.assertIn("X", cats)
        self.assertTrue(self.df_flags_1['A_fl'].isnull().sum() == 1)
        self.assertTrue(isinstance(self.df_flags_1['A_fl'].dtype, pd.CategoricalDtype))
        self.assertTrue(isinstance(self.df_flags_1['B_fl'].dtype, pd.CategoricalDtype))
        self.assertTrue(self.df_flags_0['A_fl'].dtype == 'O')
        self.assertEqual(cats[0], 'Y')
        self.assertEqual(cats[1], 'N')

    def test_2_crosstab_from_lists_duplicate_rows_cols(self):
        df = self.df_crosstab.copy()
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A', 'A'], cols=['B'])
        assert str(excinfo.value) == "'rows' must not contain duplicate column names."
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A'], cols=['B', 'B'])
        assert str(excinfo.value) == "'cols' must not contain duplicate column names."
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A','A'], cols=['B', 'B'])
        assert str(excinfo.value) == "'cols' must not contain duplicate column names."

    def test_3_crosstab_from_lists_empty_dataframe(self):
        df = pd.DataFrame({'A': [], 'B': [], 'C': []})
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A'], cols=['B'], perct_within_index=None)
        assert str(excinfo.value) == "'df' must not be empty."

    def test_4_crosstab_from_lists_single_row(self):
        df = pd.DataFrame({'A': ['foo'], 'B': ['one'], 'C': [1]})
        ct = crosstab_from_lists(df, rows=['A'], cols=['B'], perct_within_index=None)
        self.assertEqual(ct['count'].loc['foo', 'one'], 1)

    def test_5_crosstab_from_lists_with_multiple_rows_and_cols(self):
        df = pd.DataFrame({
            'A': ['foo', 'foo', 'bar', 'bar', 'baz'],
            'B': ['one', 'two', 'one', 'two', 'one'],
            'C': [1, 2, 3, 4, 5]
        })
        ct = crosstab_from_lists(df, rows=['A'], cols=['B'], perct_within_index=None)
        self.assertIn('count', ct)
        self.assertIn('percent', ct)
        self.assertIn('report', ct)
        self.assertIn('total', ct)
        self.assertIn('baz', ct['count'].index)
        self.assertIn('one', ct['count'].columns)
        self.assertIn('All', ct['count'].index)
        self.assertIn('All', ct['count'].columns)
        self.assertIsInstance(ct, dict)
        self.assertIsInstance(ct['count'], pd.DataFrame)
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A'], cols=['X'], perct_within_index=None)
        assert str(excinfo.value) == "All elements in 'cols' must be column names of df."
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['X'], cols=['B'], perct_within_index=None)
        assert str(excinfo.value) == "All elements in 'rows' must be column names of df."
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A'], cols=['B'], perct_within_index='A')
        assert str(excinfo.value) == "'perct_within_index' must be a list of column names."
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A'], cols=['B'], perct_within_index=['C'])
        assert str(excinfo.value) == "'C' must be in either 'rows' or 'cols'."
        with pytest.raises(ValueError) as excinfo:
            crosstab_from_lists(df, rows=['A'], cols=['B'], perct_within_index=['X'])
        assert str(excinfo.value) == "'X' must be in either 'rows' or 'cols'."


    def test_6_geo_mean_sd_by_group_with_zero_and_negative(self):
        df = pd.DataFrame({'group': ['A', 'A', 'B', 'B'], 'value': [0, -5, 10, 20]})
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        a_row = result[result['group'] == 'A']
        b_row = result[result['group'] == 'B']
        self.assertTrue(np.isnan(a_row['Geo_mean'].values[0]))
        self.assertFalse(np.isnan(b_row['Geo_mean'].values[0]))

    def test_7_geo_mean_sd_by_group_with_inf(self):
        df = pd.DataFrame({'group': ['A', 'A'], 'value': [np.inf, 10]})
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        self.assertFalse(np.isinf(result['Geo_mean'].values[0]))

    def test_8_geo_mean_sd_by_group_with_all_valid(self):
        df = pd.DataFrame({'group': ['A', 'A', 'A'], 'value': [1, 2, 3]})
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        self.assertAlmostEqual(result['Geo_mean'].values[0], np.exp(np.mean(np.log([1, 2, 3]))))

    def test_9_geo_mean_sd_by_group_with_groupby_none(self):
        df = pd.DataFrame({'group': ['A', 'A', 'B', 'B'], 'value': [1, 2, 3, 4]})
        with pytest.raises(KeyError):
            geo_mean_sd_by_group(df, group_by=123, var='value')
        with pytest.raises(TypeError):
            geo_mean_sd_by_group(df, group_by=None, var='value')

    def test_10_geo_mean_sd_by_group_nan_and_valid(self):
        df = pd.DataFrame({'group': ['A', 'A', 'A'], 'value': [np.nan, 10, 20]})
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        self.assertTrue(result['N_included'].values[0] == 2)
        self.assertFalse(np.isnan(result['Geo_mean'].values[0]))

    def test_11_geo_mean_sd_by_group_groupby_multiple_columns(self):
        df = pd.DataFrame({
            'group1': ['A', 'A', 'B', 'B'],
            'group2': [1, 2, 1, 2],
            'value': [1, 2, 3, 4]
        })
        result = geo_mean_sd_by_group(df, group_by=['group1', 'group2'], var='value')
        self.assertEqual(len(result), 4)
        self.assertIn('Geo_mean', result.columns)

    def test_geo_mean_sd_by_group_basic(self):
        data = {
            'group': ['A', 'A', 'A', 'B', 'B', 'B', 'C','C','C','C'],
            'value': [10, 20, 30, 5, 15, 25, np.nan, 0, -1, 2]
        }
        df = pd.DataFrame(data)
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        self.assertIn('Geo_mean', result.columns)
        self.assertIn('Geo_sd', result.columns)
        self.assertIn('CI_lower', result.columns)
        self.assertIn('CI_upper', result.columns)
        self.assertIn('Alpha', result.columns)
        self.assertIn('N_total', result.columns)
        self.assertIn('N_included', result.columns)
        # Check that group C has nan for Geo_mean (since only 2 is valid)
        c_row = result[result['group'] == 'C']
        self.assertTrue(np.isnan(c_row['Geo_mean'].values[0]) or c_row['N_included'].values[0] == 1)

    def test_geo_mean_sd_by_group_all_nan(self):
        df = pd.DataFrame({'group': ['A', 'A'], 'value': [np.nan, np.nan]})
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        self.assertTrue(np.isnan(result['Geo_mean'].values[0]))

    def test_geo_mean_sd_by_group_all_zero_or_negative(self):
        df = pd.DataFrame({'group': ['A', 'A'], 'value': [0, -1]})
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        assert np.isnan(result['Geo_mean'].values[0])

    def test_geo_mean_sd_by_group_single_value(self):
        df = pd.DataFrame({'group': ['A'], 'value': [10]})
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        self.assertEqual(round(result['Geo_mean'].values[0], 10), 10)

    def test_geo_mean_sd_by_group_multiple_groups(self):
        df = pd.DataFrame({
            'group': ['A', 'A', 'B', 'B'],
            'value': [1, 2, 3, 4]
        })
        result = geo_mean_sd_by_group(df, group_by='group', var='value')
        self.assertEqual(set(result['group']), {'A', 'B'})

if __name__ == "__main__":
    unittest.main()