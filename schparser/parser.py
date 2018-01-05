"""
This module provides functions to extract schedules and their data from a PDF.
This is done using tabula-py package.
"""

from tabula import read_pdf

# Schedule area: 37.0,70.959,422.809,820.501
# It is allways in this area, but the information table could be there too
# (when it is too big it is cut in two pages)

# Information area: 421.551,7.884,582.393,808.937
# Information area is almost always is this area, exepctions are when it is too
# big and appear in next page, in this case this region in empty.

# Information alternative area: 5.256,7.884,404.731,808.937
# This is the alternative information area.

# Or use auto, and split data frame checking the data.
# A better idea: extract all tables in a specific area!!!!

def extract_schedules(path_name):
    """
    Extracts schedules from a PDF.
    Args:
        path_name (str): Path name of the targeted PDF.
    Returns:
        List of schedules, each schedule is a pandas's DataFrame.
        List of booleans, each element represents each page of the PDF. True if
        the data is in the same page of the schedule, False if the page only
        contains data.
    """

    area_schedule = (6.833, 70.959, 424.179, 824.706)

    raw_schedules = read_pdf(path_name, pages='all', multiple_tables=True,
                             spreadsheet=True, silent=True, guess=False,
                             area=area_schedule)
    format_schedules = []

    valid_data = [True] * len(raw_schedules)

    # If sch is a schedule, then we format it and add it to format_schedules
    # else it is marked as incorrect in valid_data.
    for i, sch in enumerate(raw_schedules):
        if not sch.empty and sch.iloc[0][0] and sch.iloc[0][0] == "LUNES":
            format_schedules.append(sch.drop(sch.index[[1, 3, 5, 7, 9, 11]],
                                             axis=1))
        else:
            valid_data[i] = False

    return format_schedules, valid_data

def extract_data(path_name, valid_pages):
    """
    Extracts schedule data from a PDF.
    Args:
        path_name (str): Path name of the targeted PDF.
        valid_pages (list(bool)): Pages that have the data at the same place as
        the schedule. False if the page only contains data.
    Returns:
        List of schedule data, each item is a pandas's DataFrame.
    """

    area_data_norm = (421.551, 7.884, 582.393, 808.937)
    area_data_alt = (5.256, 7.884, 404.731, 808.937)

    # This is used to read the propper data area of each page
    data_sch_pages = []
    only_data_pages = []
    for i, item in enumerate(valid_pages, 1):
        if item:
            data_sch_pages.append(i)
        else:
            only_data_pages.append(i)
            # if the n-th page only contains data, then the (n - 1)-th page
            # doesn't has data
            data_sch_pages.pop()


    raw_data = read_pdf(path_name, pages=data_sch_pages, multiple_tables=True,
                        stream=True, silent=True, guess=False,
                        area=area_data_norm)

    if only_data_pages:
        raw_data_tmp = read_pdf(path_name, pages=only_data_pages,
                                multiple_tables=True, stream=True,
                                silent=True, guess=False, area=area_data_alt)

        for i, data in zip(only_data_pages, raw_data_tmp):
            raw_data.insert(i - 1, data)

    return raw_data




def extract_all(path_name):
    """
    Extracts the schedules and their data from a PDF.
    Args:
        path_name (str): Path name of the targeted PDF.
    Returns:
        List of tuple of two elements, each tuple contains a schedule and
        the related data. Both are pandas's DataFrame.
    """

    # TODO: check this areas
    # TODO: format raw_schdata, then verify if the data correspond with the
    # schedule, for this use correct_info
