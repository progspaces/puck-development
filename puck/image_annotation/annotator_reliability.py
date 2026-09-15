import json
from image_annotation.krippendorff_alpha import krippendorff_alpha, interval_metric

julias_path = "/puck/data/annotations/annotations_julia.json"
davids_path = "puck/data/annotations/annotations_david.json"
michaels_path = "puck/data/annotations/annotations_michael.json"

with open(julias_path , "r") as json_file_julia:
        julia_dict = dict(json.loads(json_file_julia.read()))

with open(davids_path , "r") as json_file_davids:
        david_dict = dict(json.loads(json_file_davids.read()))

with open(michaels_path , "r") as json_file_michael:
        michael_dict = dict(json.loads(json_file_michael.read()))

a_list = []
b_list = []
c_list = []

for img in list(julia_dict.keys()):
        a = julia_dict.get(img)
        b = david_dict.get(img)
        c = michael_dict.get(img)
        for num in range(0,4,1):
                ## letter [num] gets you back the whole entry
                a_entry = a[num]
                b_entry = b[num]
                c_entry = c[num]
                for ind in range(1,3):
                        # grabs the x and the y as 1 and 2
                        a_list.append(a_entry[ind])
                        b_list.append(b_entry[ind])
                        c_list.append(c_entry[ind])

full = [a_list, b_list, c_list]

print(f"Using the krippendoff interval metric, the inter-annotator reliability for the following annotations, \n \
      {julias_path} \n \
      {davids_path} \n \
      {michaels_path} \n \
is: {krippendorff_alpha(full, interval_metric)}." )
print("This calculation does not create any output files.")

