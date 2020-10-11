"""Assignment 2: Modelling CS Education research paper data

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains a new class, PaperTree, which is used to model data on
publications in a particular area of Computer Science Education research.
This data is adapted from a dataset presented at SIGCSE 2019.
You can find the full dataset here: https://www.brettbecker.com/sigcse2019/

Although this data is very different from filesystem data, it is still
hierarchical. This means we are able to model it using a TMTree subclass,
and we can then run it through our treemap visualisation tool to get a nice
interactive graphical representation of this data.

TODO: (Task 6) Complete the steps below
Recommended steps:
1. Start by reviewing the provided dataset in cs1_papers.csv. You can assume
   that any data used to generate this tree has this format,
   i.e., a csv file with the same columns (same column names, same order).
   The categories are all in one column, separated by colons (':').
   However, you should not make assumptions about what the categories are, how
   many categories there are, the maximum number of categories a paper can have,
   or the number of lines in the file.

2. Read through all the docstrings in this file once. There is a lot to take in,
   so don't feel like you need to understand it all the first time.
   Draw some pictures!
   We have provided the headers of the initializer as well as of some helper
   functions we suggest you implement. Note that we will not test any
   private top-level functions, so you can choose not to implement these
   functions, and you can add others if you want to for your solution.
   For this task, we will be testing that you are building the correct tree,
   not that you are doing it in a particular way. We will access your class
   in the same way as in the client code in the visualizer.

3. Plan out what you'll need to do to implement the PaperTree initializer.
   In particular, think about how to use the boolean parameters to do different
   things in setting up the tree. You may also find it helpful to review the
   Python documentation about the csv module, which you are permitted and
   encouraged to use. You should have a good plan, including what your subtasks
   are, before you begin writing any code.

4. Write the code for the PaperTree initializer and any helper functions you
   want to use in your design. You should not make any changes to the public
   interface of this module, or of the PaperTree class, but you can add private
   attributes and helpers as needed.

5. Tidy and test your code, and try it with the visualizer client code. Make
   sure you have documented any new private attributes, and that PyTA passes
   on your code.
"""
import csv
from typing import List, Dict
from tm_trees import TMTree

# Filename for the dataset
DATA_FILE = 'cs1_papers.csv'


class PaperTree(TMTree):
    """A tree representation of Computer Science Education research paper data.

    === Private Attributes ===

    _author:
        This paper's author
    _doi:
        This paper's doi
    These should store information about this paper's <authors> and <doi>.

    === Inherited Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - All TMTree RIs are inherited.
    """

    _author: str
    _doi: str

    def __init__(self, name: str, subtrees: List[TMTree], authors: str = '',
                 doi: str = '', citations: int = 0, by_year: bool = True,
                 all_papers: bool = False) -> None:
        """Initialize a new PaperTree with the given <name> and <subtrees>,
        <authors> and <doi>, and with <citations> as the size of the data.

        If <all_papers> is True, then this tree is to be the root of the paper
        tree. In that case, load data about papers from DATA_FILE to build the
        tree.

        If <all_papers> is False, Do NOT load new data.

        <by_year> indicates whether or not the first level of subtrees should be
        the years, followed by each category, subcategory, and so on. If
        <by_year> is False, then the year in the dataset is simply ignored.
        """
        self._author = authors
        self._doi = doi
        TMTree.__init__(self, name, subtrees, citations)

        if not all_papers:
            pass
        else:
            if not by_year:
                result = _load_data_to_dict(_load_papers_to_dict(False))
                subtree = _load_dict_to_tree(result)
                TMTree.__init__(self, name, subtrees + subtree, citations)

            else:
                data_by_year = _load_papers_to_dict(True)
                result = []
                for data_each_year in data_by_year:
                    sub = _load_dict_to_tree(_load_data_to_dict(data_each_year))
                    result.append(PaperTree(data_each_year[0][2], sub))
                TMTree.__init__(self, name, subtrees + result, citations)

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (paper)'
        else:
            return ' (year or category)'

    def get_separator(self) -> str:
        """Return the category separator for this.
        """
        return '/'


def _load_papers_to_dict(by_year: bool = True) -> List:
    """Return a nested dictionary of the data read from the papers dataset file.

    If <by_year>, then use years as the roots of the subtrees of the root of
    the whole tree. Otherwise, ignore years and use categories only.
    """
    data = []
    with open(DATA_FILE, 'r') as csvfile:
        csvfile.readline()
        reader = csv.reader(csvfile)
        for row in reader:
            year = int(row[2])
            category = row[3].strip('"').split(':')
            citations = int(row[5])
            # row[0] is author
            # row[1] is title
            # row[4] is url(doi)
            each_paper = [row[0], row[1], year, category, row[4], citations]
            data.append(each_paper)
    # now, in data list, each item is a paper, is a list contain info of a paper

    # now we gonna divide these item in data because of different year
    if by_year:
        all_year_list = []
        for each_paper_info in data:
            if each_paper_info[2] not in all_year_list:
                all_year_list.append(each_paper_info[2])
        # now all_year_list is a list contain all year without duplicate
        data_by_year = []
        for each_year in all_year_list:
            each_year_papers = _find_year(data, each_year)

            # accumulate each_year_papers to get data_by_year
            data_by_year.append(each_year_papers)
        # now data_by_year is a list
        # each item in that list contain papers in a specific year :\
        # for example: [[1998 papers info], [1997 papers info], ...[...]]
        # each paper contain info of :\
        # for example: [author, title, year, category, url, citations]
        csvfile.close()
        return data_by_year

    return data


def _find_year(data: List, each_year: int) -> List:
    each_year_papers = []
    for each_paper_info in data:
        if each_paper_info[2] == each_year:
            each_year_papers.append(each_paper_info)
    return each_year_papers


# function above load data file to list of paper info
# return different list depend on whether by_year
# function below load list data to a recursively dictionary
def _load_data_to_dict(data: List) -> Dict:
    """input a list of paper data, out put a recursive dict
    """
    result = {}
    for paper in data:
        _load_each_paper(paper, paper[3], result)
    return result


# function below is a helper function of _load_data_to_dict
# aim is load each paper's info into a given result Dict
# the function above will return this result Dict
def _load_each_paper(paper: List, paper_cate_list: List, result: Dict) -> None:
    """paper is info of one paper, load info in paper to dict
    paper = [author, title, year, category_list, url, citations]
    >>> paper = ['author', 'title', 'year', ['m', 'n', 'f'], 'url', 3]
    >>> paper_cate_list = ['m', 'n', 'f']
    >>> result = {}
    >>> _load_each_paper(paper, paper_cate_list, result)
    >>> result == {'m': {'n': {'f': {'title': \
    ['author', 'title', 'year', ['m', 'n', 'f'], 'url', 3]}}}}
    """
    if len(paper_cate_list) == 1:
        # paper_cate_list = ['m'], load paper info directly under category 'm'
        if not paper_cate_list[0] in result:
            result[paper_cate_list[0]] = {paper[1]: paper}
        else:
            result[paper_cate_list[0]][paper[1]] = paper

    else:
        # paper_cate_list = ['m', 'n', 'f']
        # then load cate_list recursively
        if not paper_cate_list[0] in result:
            result[paper_cate_list[0]] = {}
            _load_each_paper(paper, paper_cate_list[1:],
                             result[paper_cate_list[0]])
        else:
            _load_each_paper(paper, paper_cate_list[1:],
                             result[paper_cate_list[0]])


# make a recursively dict data to list of paper tree
def _load_dict_to_tree(result: Dict) -> List[PaperTree]:
    """Input is the result of _load_data_to_dict
    Return a list of recursively Paper_tree
    """
    trees = []
    for cate in result:
        # cate is the first layer of category
        if isinstance(result[cate], List):
            sub = []
            author = result[cate][0]
            doi = result[cate][4]
            citations = result[cate][5]
            first_layer = PaperTree(cate, sub, author, doi, citations)
            trees.append(first_layer)
        else:
            sub = _load_dict_to_tree(result[cate])
            first_layer = PaperTree(cate, sub)
            trees.append(first_layer)
    return trees


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': ['python_ta', 'typing', 'csv', 'tm_trees'],
        'allowed-io': ['_load_papers_to_dict'],
        'max-args': 8
    })
