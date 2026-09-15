
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import puck.code_modules.dot_finding.dot_finder as df
import puck.code_modules.colour_conversion.colour_finding as cf
import puck.code_modules.calibration.calibration as cal
import puck.code_modules.geometry.clockwise_dots as clkwise
import puck.code_modules.permutation_guessing.permutation_guessing as perm_guess

## CONSTANTS
CALIBRATION_MIN_DIST = 30
PROGRAM_MIN_DIST = 170


def main(palette = "custom", results_prefix =  "output/program_recognition_results_", adjustment = "../", adjustment_on = True, cal_loc = "davids", cal_height = "short", dist= False):
    cal_path ="data/images_calibration/" +cal_height +  "/"+ palette+ "/" + cal_loc + "/" + cal_height+"_" + palette + "_" + cal_loc +"_calibration.jpg"
    results_path = (results_prefix + palette + ".csv") if dist == False else (results_prefix + palette + "dist.csv")
    if adjustment_on:
        results_path = adjustment + results_path
        cal_path = adjustment + cal_path
    cal_centers,cal_image = df.find_centers_hough(cal_path, min_dist=CALIBRATION_MIN_DIST)
    colors_and_coords=cf.get_colors_and_coords(cal_centers,side = 25, image =cal_image,colorspace= "RGB")
    black_dot_cal_coords = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")[0]
    calibration_colors =cal.get_calibration_colors(black_dot_cal_coords,colors_and_coords)

    p = Path('../')

    a_paths =[path for path in p.glob("data/images_copy/" + palette + "/*/*/A/*_A*[0-4].jpg")]
    b_paths =[path for path in p.glob("data/images_copy/" + palette + "/*/*/B/*_B*[0-4].jpg")]
    c_paths =[path for path in p.glob("data/images_copy/"+ palette + "/*/*/C/*_C*[0-4].jpg")]
    d_paths =[path for path in p.glob("data/images_copy/"+ palette + "/*/*/D/*_D*[0-4].jpg")]
    # print(a_paths)

    path_perm_dict = {"a": (a_paths, 'afd'),"b": (b_paths, 'ahc'),"c": (c_paths, 'efg'),"d": (d_paths, 'fff') }

    checking_dict =[]
    for k in path_perm_dict.keys():
        paths, true_perm = path_perm_dict.get(k)
        for path in paths:
            centers,image = df.find_centers_hough(path, min_dist=PROGRAM_MIN_DIST)
            colors_and_coords=cf.get_colors_and_coords(centers,side = 25, image =image,colorspace= "RGB")
            if len(colors_and_coords) ==4:
                black_dot = cf.get_black_dot(colors_and_coords=colors_and_coords, colorspace= "rgb")
                # print(colors_and_coords)
                ordered_rectangle= clkwise.order_rectangle(colors_and_coords, black_dot[0])
                perm,luv_detected_colours = perm_guess.get_color_perm_and_dist(ordered_rectangle, calibration_colors,colorspace= "LUV")
                correct = (perm == true_perm)
                overlap =sum([(perm[i] == true_perm[i]) for i in range(0,len(perm))])
            if dist:
                checking_dict.append({"key":k, "path":path, "found_perm": perm, "true_perm": true_perm, "correct": correct, "overlap":overlap, "luv_coords": luv_detected_colours})
            else:
                checking_dict.append({"key":k, "path":path, "found_perm": perm, "true_perm": true_perm, "correct": correct, "overlap":overlap})

    # print(results_path)
    if dist:
            results_df = pd.DataFrame(checking_dict, columns=["key","path", "found_perm", "true_perm", "correct", "overlap", "luv_coords"])
    else:
        results_df = pd.DataFrame(checking_dict, columns=["key","path", "found_perm", "true_perm", "correct", "overlap"])
    results_df.to_csv(results_path)

    print(f"Results of testing the {palette} palette, have been put into a .csv in the output folder.")
    print(f"It can be found at: {results_path}.")
    if dist:
        print("This csv also contains information about the LUV coordinates detected in each image which can be used to see how the detected colours compare to their ground truths.")

    return results_path

if __name__ == "__main__":
    main(palette= "dark",)
        #   adjustment= "/Users/jdreiling/Desktop/puck/puck/")