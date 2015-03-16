'''
Created on Nov 5, 2014
Convert an antweb file into a csv, which can be uploaded to a PostgreSQL server
@author: John Deyrup
'''
import csv
import re

#Read and return a 2d array of the antweb file
def read_file(file):
    with open(file, 'rt') as f:
        reader = csv.reader(f, delimiter = ',')
        x = True
        line = 0
        out_list = []
        while(x==True):
            try:
                out_list.append(reader.__next__())
            except:
                x=False
                print("error on line ", line)
            line +=1       
    return out_list


#Returns only the columns that begin with words in specimen_talbe            
def get_columns(file_array, navicat_fields):
    first_row = file_array[0]
    columns = []
    #Finds the index of where the word in specimen_table is located in the first row of the csv
    def get_column(in_word):
        return first_row.index(in_word)
    #Gets the column for each word in specimen_table
    for word in navicat_fields:
        columns.append([row[get_column(word)] for row in file_array])
    return columns
 
#Capitalizes the first letter of genus adds "." and merges with species
def merge_genus_species(file_array):
    merged_list = []
    for i in range(len(file_array[7])):
        merged_list.append(file_array[7][i][0].upper()+file_array[7][i][1:]+"."+file_array[8][i])
    return [merged_list]
     
#Replace the first row of our edited table with fields that navicat recognizes
def replace_headings(file_array, fields):
    for i in range(len(fields)):
        file_array[i][0] = fields[i]
    return file_array
 
#Make casent upper case
def make_casent_upper(file_array):
    for i in range(len(file_array[0])):
        file_array[0][i] = re.sub("casent", "CASENT", file_array[0][i])
    return file_array
 
#Fixes dates
def fix_dates(file_array, pos):
    fixed_date = []
    for date in file_array[pos]:
        date_list = date.split("/")
        if(len(date_list)==3):
            year = int(date_list[2])
            if(year>50):
                year = 1900 + year
            else:
                year = 2000 + year
            month = int(date_list[0])
            if(month<10):
                month = "0" + str(month)
            else:
                month = str(month)
            day = int(date_list[1])
            if(day<10):
                day = "0" + str(day)
            else:
                day = str(day)
            fixed_date.append(str(year)+"-"+month+"-"+day)
        else:
            fixed_date.append(date_list[0])
    return [fixed_date]
 
#Changes rows to columns
def rows_to_columns(file_array):
    out_array = []
    for i in range(len(file_array[0])):
        row = []
        for j in range(len(file_array)):
            row.append(file_array[j][i])
        out_array.append(row)
    return(out_array)
 
def write_csv(filename, csv_table):
    with open(filename, 'w', encoding='utf-8', newline = '') as csvfile:
        out_csv = csv.writer(csvfile, delimiter = ',')
        out_csv.writerows(csv_table) 
 
csv_file = read_file("your_filename.csv")
navicat_specimen_fields = ['specimen_code', 'collection_event_code', "located_at", "owned_by", "lifestagesex", 'medium', 'type_status', 'taxon_code', 'determined_by', 'date_identified']
antweb_specimen_field = ["SpecimenCode", "CollectionCode", "LocatedAt", "OwnedBy", "LifeStageSex", "Medium", "TypeStatus", 
                      "Genus", "Species", "DeterminedBy", "DateDetermined"]
columns = get_columns(csv_file, antweb_specimen_field)
columns = columns[0:7] + merge_genus_species(columns) + columns[9:]
columns = replace_headings(columns, navicat_specimen_fields)
columns = make_casent_upper(columns)
preserve_column = ["basis_of_record"] + ["Preserved specimen"] * len(columns[0])
columns = columns[:9] + fix_dates(columns,9) + [preserve_column] 
columns = rows_to_columns(columns)
write_csv("specimen_table.csv", columns)
 
 
antweb_collection_fields = ['CollectionCode', 'CollectedBy', 'DateCollectedStart', 'DateCollectedEnd', 'Method', 'Habitat', 'Microhabitat', 'LocalityCode']
navicat_collection_fields = ['collection_event_code', 'collected_by', 'date_collected_start', 'date_collected_end', 'method', 'habitat', 'microhabitat',  'locality_code',]
cc_columns = get_columns(csv_file, antweb_collection_fields)
cc_columns = replace_headings(cc_columns, navicat_collection_fields)
cc_columns = cc_columns[0:2] + fix_dates(cc_columns,2) + fix_dates(cc_columns,3) + cc_columns[4:]
cc_columns = rows_to_columns(cc_columns)
write_csv('collection_table.csv', cc_columns)
 
antweb_locality_fields = ['LocalityName', 'Adm1', 'Adm2', 'Country', 'Elevation', 'ElevationMaxError', 'LocLatitude', 'LocLongitude', 'LatLonMaxError', 
                          'BiogeographicRegion', 'LocalityCode']
navicat_locality_fields = ['locality_name', 'adm1', 'adm2', 'country', 'elevation', 'elevation_error', 'latitude', 'longitude', 'latlong_error', 
                          'biogeographic_region', 'locality_code']
lo_columns = get_columns(csv_file, antweb_locality_fields)
lo_columns = replace_headings(lo_columns, navicat_locality_fields)
lo_columns = rows_to_columns(lo_columns)
write_csv('locality_table.csv', lo_columns)
 
 
antweb_species_fields = ["Genus", 'Species', "Species group"]
navicat_species_fields = ['taxon_code', 'genus_name', 'species_name', 'species_group']
sp_columns = get_columns(csv_file, antweb_species_fields)