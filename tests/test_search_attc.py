# -*- coding: utf-8 -*-

####################################################################################
# Integron_Finder - Integron Finder aims at detecting integrons in DNA sequences   #
# by finding particular features of the integron:                                  #
#   - the attC sites                                                               #
#   - the integrase                                                                #
#   - and when possible attI site and promoters.                                   #
#                                                                                  #
# Authors: Jean Cury, Bertrand Neron, Eduardo PC Rocha                             #
# Copyright (c) 2015 - 2018  Institut Pasteur, Paris and CNRS.                     #
# See the COPYRIGHT file for details                                               #
#                                                                                  #
# integron_finder is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation, either version 3 of the License, or                #
# (at your option) any later version.                                              #
#                                                                                  #
# integron_finder is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with this program (COPYING file).                                          #
# If not, see <http://www.gnu.org/licenses/>.                                      #
####################################################################################

import os

import pandas as pd
import pandas.util.testing as pdt

try:
    from tests import IntegronTest
except ImportError as err:
    msg = "Cannot import integron_finder: {0!s}".format(err)
    raise ImportError(msg)

from integron_finder import attc, infernal

"""
Unit tests search_attc function of integron_finder
"""

class TestSearchAttc(IntegronTest):

    def setUp(self):
        """
        Define variables common to all tests
        """
        self.replicon_name = "acba.007.p01.13"
        self.replicon_id = "ACBA.007.P01_13"
        self.length_cm = 47  # length in 'CLEN' (value for model attc_4.cm)
        self.dist_threshold = 4000  # (4kb at least between 2 different arrays)
        self.replicon_size = 20301  # size of acba.007.p01.13

    def test_search_attc_empty(self):
        """
        Test that when there are no attC sites detected, the attc array is empty.
        """
        attc_file = self.find_data(os.path.join("fictive_results", self.replicon_id + "_attc_table-empty.res"))
        # Construct attC dataframe (read from infernal file)
        attc_df = infernal.read_infernal(attc_file, self.replicon_id, self.length_cm)
        attc_array = attc.search_attc(attc_df, True, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 0)
        attc_res = []
        self.assertEqual(attc_array, attc_res)


    def test_search_attc_uniq(self):
        """
        Test that it finds a unique attc array when giving a table with 3 attC sites
        on the same strand and separated by less than 4kb each.
        """
        attc_file = self.find_data(os.path.join("Results_Integron_Finder_{}".format(self.replicon_name),
                                                "tmp_{}".format(self.replicon_id),
                                                "{}_attc_table.res".format(self.replicon_id)))
        # Construct attC dataframe (read from infernal file)
        attc_df = infernal.read_infernal(attc_file, self.replicon_id, self.length_cm)
        # search attC arrays, keeping palindromes
        # 2 attc sites are in the same array if they are on the same strand, and separated by
        # a distance less than 4kb

        attc_array = attc.search_attc(attc_df, True, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 1)

        # Construct expected output:
        attc_res = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                         "pos_beg", "pos_end", "sens", "evalue"], dtype='int')
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 17825,
                                    "pos_end": 17884,
                                    "sens": "-",
                                    "evalue": 1e-9},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19080,
                                    "pos_end": 19149,
                                    "sens": "-",
                                    "evalue": 1e-4},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19618,
                                    "pos_end": 19726,
                                    "sens": "-",
                                    "evalue": 1.1e-7},
                                   ignore_index=True)
        # convert positions to int
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_res[intcols] = attc_res[intcols].astype(int)
        pdt.assert_frame_equal(attc_res, attc_array[0])


    def test_search_attc_diff_strand(self):
        """
        Test that it finds a size 2 attc array when giving a table with 3 attC sites
        on the same strand and 1 on the other strand, all separated by less than 4kb each.
        """
        attc_file = self.find_data(os.path.join("Results_Integron_Finder_{}".format(self.replicon_name),
                                                "tmp_{}".format(self.replicon_id),
                                                "{}_attc_table.res".format(self.replicon_id)))
        # Construct attC dataframe (read from infernal file)
        attc_df = infernal.read_infernal(attc_file, self.replicon_id, self.length_cm)
        # Add another attC on the opposite strand
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 15000,
                                  "pos_end": 16000,
                                  "sens": "+",
                                  "evalue": 0.19},
                                 ignore_index=True)
        # search attC arrays, keeping palindromes
        # 2 attc sites are in the same array if they are on the same strand, and separated by
        # a distance less than 4kb
        attc_array = attc.search_attc(attc_df, True, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 2)

        # Construct expected outputs:
        attc_res = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                         "pos_beg", "pos_end", "sens", "evalue"])
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 17825,
                                    "pos_end": 17884,
                                    "sens": "-",
                                    "evalue": 1e-9},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19080,
                                    "pos_end": 19149,
                                    "sens": "-",
                                    "evalue": 1e-4},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19618,
                                    "pos_end": 19726,
                                    "sens": "-",
                                    "evalue": 1.1e-7},
                                   ignore_index=True)
        attc_res2 = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                          "pos_beg", "pos_end", "sens", "evalue"])
        attc_res2 = attc_res2.append({"Accession_number": self.replicon_id,
                                      "cm_attC": "attC_4",
                                      "cm_debut": 1,
                                      "cm_fin": 47,
                                      "pos_beg": 15000,
                                      "pos_end": 16000,
                                      "sens": "+",
                                      "evalue": 0.19},
                                     ignore_index=True)
        # convert positions to int
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_res[intcols] = attc_res[intcols].astype(int)
        attc_res2[intcols] = attc_res2[intcols].astype(int)
        pdt.assert_frame_equal(attc_res, attc_array[1])
        pdt.assert_frame_equal(attc_res2, attc_array[0])


    def test_search_attc_dist_same_strand(self):
        """
        Test that it finds a size 2 attc arrays when giving a table with 3 attC sites
        on the same strand and separated by less than 4 kb, and another 1 separated from the
        others by more than 4kb.
        """
        attc_file = self.find_data(os.path.join("Results_Integron_Finder_{}".format(self.replicon_name),
                                                "tmp_{}".format(self.replicon_id),
                                                "{}_attc_table.res".format(self.replicon_id)))
        # Construct attC dataframe (read from infernal file)
        attc_df = infernal.read_infernal(attc_file, self.replicon_id, self.length_cm)
        # Add another attC at more than 4kb, same strand
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 12900,
                                  "pos_end": 13800,
                                  "sens": "-",
                                  "evalue": 1e-3},
                                 ignore_index=True)
        attc_df.sort_values(["Accession_number", "pos_beg", "evalue"], inplace=True)
        # search attC arrays, keeping palindromes
        # 2 attc sites are in the same array if they are on the same strand, and separated by
        # a distance less than 4kb
        attc_array = attc.search_attc(attc_df, True, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 2)

        # Construct expected outputs:
        attc_res = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                         "pos_beg", "pos_end", "sens", "evalue"])
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 17825,
                                    "pos_end": 17884,
                                    "sens": "-",
                                    "evalue": 1e-9},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19080,
                                    "pos_end": 19149,
                                    "sens": "-",
                                    "evalue": 1e-4},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19618,
                                    "pos_end": 19726,
                                    "sens": "-",
                                    "evalue": 1.1e-7},
                                   ignore_index=True)
        attc_res2 = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                          "pos_beg", "pos_end", "sens", "evalue"])
        attc_res2 = attc_res2.append({"Accession_number": self.replicon_id,
                                      "cm_attC": "attC_4",
                                      "cm_debut": 1,
                                      "cm_fin": 47,
                                      "pos_beg": 12900,
                                      "pos_end": 13800,
                                      "sens": "-",
                                      "evalue": 1e-03},
                                     ignore_index=True)
        # convert positions to int
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_res[intcols] = attc_res[intcols].astype(int)
        attc_res2[intcols] = attc_res2[intcols].astype(int)
        pdt.assert_frame_equal(attc_res, attc_array[1])
        pdt.assert_frame_equal(attc_res2, attc_array[0])


    def test_search_attc_dist_diff_strand(self):
        """
        Test that it finds a size 3 attc array when giving a table with:
        - 3 attC sites on the same strand (-) and separated by less than 4 kb
        - 2 other attC sites separated by less than 4kb but on the other strand (+)
        - 1 other attC site , also on strand +, but separated by more than 4kb.
        """
        attc_file = self.find_data(os.path.join("Results_Integron_Finder_{}".format(self.replicon_name),
                                                "tmp_{}".format(self.replicon_id),
                                                "{}_attc_table.res".format(self.replicon_id)))
        # Construct attC dataframe (read from infernal file)
        attc_df = infernal.read_infernal(attc_file, self.replicon_id, self.length_cm)
        # Add another attC at more than 4kb, same strand
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 15800,
                                  "pos_end": 16000,
                                  "sens": "+",
                                  "evalue": 1e-3},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 12000,
                                  "pos_end": 12500,
                                  "sens": "+",
                                  "evalue": 1e-3},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 7100,
                                  "pos_end": 8200,
                                  "sens": "+",
                                  "evalue": 1e-3},
                                 ignore_index=True)
        attc_df.sort_values(["Accession_number", "pos_beg", "evalue"], inplace=True)
        # search attC arrays, keeping palindromes
        # 2 attc sites are in the same array if they are on the same strand, and separated by
        # a distance less than 4kb
        attc_array = attc.search_attc(attc_df, True, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 3)

        # Construct expected outputs:
        attc_res = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                         "pos_beg", "pos_end", "sens", "evalue"])
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 17825,
                                    "pos_end": 17884,
                                    "sens": "-",
                                    "evalue": 1e-9},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19080,
                                    "pos_end": 19149,
                                    "sens": "-",
                                    "evalue": 1e-4},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 19618,
                                    "pos_end": 19726,
                                    "sens": "-",
                                    "evalue": 1.1e-7},
                                   ignore_index=True)
        attc_res2 = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                          "pos_beg", "pos_end", "sens", "evalue"])
        attc_res2 = attc_res2.append({"Accession_number": self.replicon_id,
                                      "cm_attC": "attC_4",
                                      "cm_debut": 1,
                                      "cm_fin": 47,
                                      "pos_beg": 12000,
                                      "pos_end": 12500,
                                      "sens": "+",
                                      "evalue": 1e-03},
                                     ignore_index=True)
        attc_res2 = attc_res2.append({"Accession_number": self.replicon_id,
                                      "cm_attC": "attC_4",
                                      "cm_debut": 1,
                                      "cm_fin": 47,
                                      "pos_beg": 15800,
                                      "pos_end": 16000,
                                      "sens": "+",
                                      "evalue": 1e-03},
                                     ignore_index=True)
        attc_res3 = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                          "pos_beg", "pos_end", "sens", "evalue"])
        attc_res3 = attc_res3.append({"Accession_number": self.replicon_id,
                                      "cm_attC": "attC_4",
                                      "cm_debut": 1,
                                      "cm_fin": 47,
                                      "pos_beg": 7100,
                                      "pos_end": 8200,
                                      "sens": "+",
                                      "evalue": 1e-03},
                                     ignore_index=True)
        # convert positions to int
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_res[intcols] = attc_res[intcols].astype(int)
        attc_res2[intcols] = attc_res2[intcols].astype(int)
        attc_res3[intcols] = attc_res3[intcols].astype(int)
        pdt.assert_frame_equal(attc_res, attc_array[2])
        pdt.assert_frame_equal(attc_res2, attc_array[1])
        pdt.assert_frame_equal(attc_res3, attc_array[0])

    def test_search_attc_uniq_circ(self):
        """
        Test that it finds a unique attc array when giving a table with:
        - 2 attC sites at the begining of the genome, separated by less than 4kb
        - 2 attC sites at the end of the genome, separated by less than 4kb from the
        1st attC site of the genome if we take into account its circularity.
        All 3 attC sites are on the strand -
        """
        attc_df = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                        "pos_beg", "pos_end", "sens", "evalue"], dtype='int')
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 1000,
                                  "pos_end": 2000,
                                  "sens": "-",
                                  "evalue": 1e-9},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 3000,
                                  "pos_end": 4000,
                                  "sens": "-",
                                  "evalue": 1e-4},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 16000,
                                  "pos_end": 17000,
                                  "sens": "-",
                                  "evalue": 1.1e-7},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 19815,
                                  "pos_end": 20000,
                                  "sens": "-",
                                  "evalue": 1.1e-7},
                                 ignore_index=True)
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_df[intcols] = attc_df[intcols].astype(int)

        attc_array = attc.search_attc(attc_df, True, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 1)

        # Output of search_attc is ordered as the cluster is:
        # - 2 last attC of genome
        # - 2 first attC of genomes
        # Whereas input was ordered by begin position. Reorder attc_df to compare with output.
        attc_df = attc_df.reindex([2, 3, 0, 1])
        attc_df.reset_index(inplace=True, drop=True)
        pdt.assert_frame_equal(attc_df, attc_array[0])

    def test_search_attc_uniq_circ_plus(self):
        """
        Test that it finds a unique attc array when giving a table with:
        - 2 attC sites at the begining of the genome, separated by less than 4kb
        - 2 attC sites at the end of the genome, separated by less than 4kb from the
        1st attC site of the genome if we take into account its circularity.
        All 3 attC sites are on the same strand +
        """
        attc_df = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                        "pos_beg", "pos_end", "sens", "evalue"], dtype='int')
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 1000,
                                  "pos_end": 2000,
                                  "sens": "+",
                                  "evalue": 1e-9},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 3000,
                                  "pos_end": 4000,
                                  "sens": "+",
                                  "evalue": 1e-4},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 16000,
                                  "pos_end": 17000,
                                  "sens": "+",
                                  "evalue": 1.1e-7},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 19815,
                                  "pos_end": 20000,
                                  "sens": "+",
                                  "evalue": 1.1e-7},
                                 ignore_index=True)
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_df[intcols] = attc_df[intcols].astype(int)

        attc_array = attc.search_attc(attc_df, True, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 1)

        # Output of search_attc is ordered as the cluster is:
        # - 2 last attC of genome
        # - 2 first attC of genomes
        # Whereas input was ordered by begin position. Reorder attc_df to compare with output.
        attc_df = attc_df.reindex([2, 3, 0, 1])
        attc_df.reset_index(inplace=True, drop=True)
        pdt.assert_frame_equal(attc_df, attc_array[0])


    def test_search_attc_drop_pal(self):
        """
        If there is 1 palindrome attC, check that it keeps the one with the highest evalue,
        and that clusters are then found according to it.
        """
        attc_df = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                        "pos_beg", "pos_end", "sens", "evalue"], dtype='int')
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 1000,
                                  "pos_end": 2000,
                                  "sens": "+",
                                  "evalue": 1e-9},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 3000,
                                  "pos_end": 4000,
                                  "sens": "-",
                                  "evalue": 1e-4},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 3000,
                                  "pos_end": 4000,
                                  "sens": "+",
                                  "evalue": 1e-9},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 5500,
                                  "pos_end": 7000,
                                  "sens": "+",
                                  "evalue": 1.1e-7},
                                 ignore_index=True)
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_df[intcols] = attc_df[intcols].astype(int)

        attc_array = attc.search_attc(attc_df, False, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 1)

        # Construct expected outputs:
        attc_res = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                         "pos_beg", "pos_end", "sens", "evalue"])
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 1000,
                                    "pos_end": 2000,
                                    "sens": "+",
                                    "evalue": 1e-9},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 3000,
                                    "pos_end": 4000,
                                    "sens": "+",
                                    "evalue": 1e-9},
                                   ignore_index=True)
        attc_res = attc_res.append({"Accession_number": self.replicon_id,
                                    "cm_attC": "attC_4",
                                    "cm_debut": 1,
                                    "cm_fin": 47,
                                    "pos_beg": 5500,
                                    "pos_end": 7000,
                                    "sens": "+",
                                    "evalue": 1.1e-7},
                                   ignore_index=True)

        attc_res[intcols] = attc_res[intcols].astype(int)
        attc_array[0].reset_index(inplace=True, drop=True)
        pdt.assert_frame_equal(attc_res, attc_array[0])


    def test_search_attc_drop_pal_break(self):
        """
        If there is 1 palindrome attC, check that it keeps the one with the highest evalue,
        and that clusters are then found according to it.
        """
        attc_df = pd.DataFrame(columns=["Accession_number", "cm_attC", "cm_debut", "cm_fin",
                                        "pos_beg", "pos_end", "sens", "evalue"], dtype='int')
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 1000,
                                  "pos_end": 2000,
                                  "sens": "-",
                                  "evalue": 1e-9},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 3000,
                                  "pos_end": 4000,
                                  "sens": "-",
                                  "evalue": 1e-4},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 3000,
                                  "pos_end": 4000,
                                  "sens": "+",
                                  "evalue": 1e-9},
                                 ignore_index=True)
        attc_df = attc_df.append({"Accession_number": self.replicon_id,
                                  "cm_attC": "attC_4",
                                  "cm_debut": 1,
                                  "cm_fin": 47,
                                  "pos_beg": 5500,
                                  "pos_end": 7000,
                                  "sens": "-",
                                  "evalue": 1.1e-7},
                                 ignore_index=True)
        intcols = ["cm_debut", "cm_fin", "pos_beg", "pos_end"]
        attc_df[intcols] = attc_df[intcols].astype(int)

        attc_array = attc.search_attc(attc_df, False, self.dist_threshold, self.replicon_size)
        self.assertEqual(len(attc_array), 3)

        # Construct expected outputs:
        columns = ["Accession_number", "cm_attC", "cm_debut", "cm_fin", "pos_beg",
                   "pos_end", "sens", "evalue"]
        attc_res = pd.DataFrame(data={"Accession_number": self.replicon_id,
                                      "cm_attC": "attC_4",
                                      "cm_debut": 1,
                                      "cm_fin": 47,
                                      "pos_beg": 1000,
                                      "pos_end": 2000,
                                      "sens": "-",
                                      "evalue": 1e-9},
                                index=[0])
        attc_res = attc_res[columns]

        attc_res2 = pd.DataFrame(data={"Accession_number": self.replicon_id,
                                       "cm_attC": "attC_4",
                                       "cm_debut": 1,
                                       "cm_fin": 47,
                                       "pos_beg": 3000,
                                       "pos_end": 4000,
                                       "sens": "+",
                                       "evalue": 1e-9},
                                 index=[0])
        attc_res2 = attc_res2[columns]

        attc_res3 = pd.DataFrame(data={"Accession_number": self.replicon_id,
                                       "cm_attC": "attC_4",
                                       "cm_debut": 1,
                                       "cm_fin": 47,
                                       "pos_beg": 5500,
                                       "pos_end": 7000,
                                       "sens": "-",
                                       "evalue": 1.1e-7},
                                 index=[0])
        attc_res3 = attc_res3[columns]

        attc_res[intcols] = attc_res[intcols].astype(int)
        attc_res2[intcols] = attc_res2[intcols].astype(int)
        attc_res3[intcols] = attc_res3[intcols].astype(int)
        pdt.assert_frame_equal(attc_res2, attc_array[0])
        pdt.assert_frame_equal(attc_res, attc_array[1])
        pdt.assert_frame_equal(attc_res3, attc_array[2])
