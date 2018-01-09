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
                             lattice=True, silent=True, guess=False,
                             area=area_schedule)

    valid_data = [True] * len(raw_schedules)

    # If sch is a schedule, then we format it and add it to format_schedules
    # else it is marked as incorrect in valid_data.
    for i, sch in enumerate(raw_schedules):
        if not sch.empty and sch.iat[0, 0] and sch.iat[0, 0] == "LUNES":
            sch.drop(sch.index[[1, 3, 5, 7, 9, 11]], axis=1, inplace=True)
        else:
            valid_data[i] = False

    for sch in raw_schedules:
        sch.drop(0, inplace=True)
        # Reset indexes is not necessary, all the access operations must be done
        # using .iat[rows, columns]
        # sch.columns = [i for i in range(sch.shape[1])]
        # sch.reset_index(inplace=True, drop=True)

    return raw_schedules, valid_data

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
            raw_data.insert(i - 2, data)

    for data in raw_data:
        data.drop(0, inplace=True)
        data.dropna(axis=1, how='all', inplace=True)

        # GROUP and TYPE separated
        data.insert(2, 't', '')

        for i in range(data.shape[0] - 1):
            data.iat[i, 1], data.iat[i, 2] = data.iat[i, 1].split(' ')

        # TEORY and PRACTICE teachers separated
        data.insert(6, 'p', object)
        for i in range(data.shape[0] - 1):
            tmp = parse_teachers(data.iat[i, 5])
            data.iat[i, 5] = tmp[0]
            data.iat[i, 6] = tmp[1]

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

    # TODO: format raw_schdata, then verify if the data correspond with the
    # schedule, for this use correct_info

def parse_teachers(teachers_str):
    """
    Separates teachers in theory and practice teachers.
    Args:
        teachers_str (str): String containing theacher names and their role.
    Returns:
        Tuple containing:
            list of theory teachers
            list of practice teachers
    """

    teachers = teachers_str.split(', ')
    # teachers = [i for i in teachers if '(' in i]
    prac_tea = [i[:i.find(' (')] for i in teachers if '(Jefe' in i]
    theo_tea = [i[:i.find(' (')] for i in teachers if '(Titular' in i]

    return (theo_tea, prac_tea)
