# simple start-stop gcode for clay extruder

import Rhino.Geometry as rg
from generalFunctions import *
import json


class LinkType(object):

    def __init__(self, link_type = None, global_trim_distance = 0.0, ss_trim_distance = 2.0, cull_distance = 1.0, lift_val = 5.0):

        if link_type == None or link_type == 'start_stop':
            
            self.start_stop = True

        else:

            self.start_stop = False

        self.trim_d = global_trim_distance
        self.ss_trim_d = ss_trim_distance

        self.updateLiftPt(lift_val)

        self.ss_f_rate = 300
        self.ss_e_rate = 100

        self.cull = True
        self.cull_distance = cull_distance

    def updateLiftPt(self, lift):

        self.ss_lift = rg.Point3d(0.0, 0.0, lift)


class PrintSettings(object):

    def __init__(self, feed_rate = 5.0, extrusion_rate = 1.0, extrusion_mode = 'relative', movement_mode = 'relative'):

        self.f_rate = feed_rate * 60.0  # GCode uses speed per min
        self.e_rate = extrusion_rate

        if movement_mode == 'relative':

            self.m_relative = True

            self.m_start_flag = 'G91'

        elif movement_mode == 'absolute':

            self.m_relative = False

            self.m_start_flag = 'G90'

        if extrusion_mode == 'relative':

            self.e_relative = True

            self.e_start_flag = 'M83'       # putting the E axis into relative mode independent of the other axes

        elif extrusion_mode == 'absolute':

            self.e_relative == False

            self.e_start_flag = 'M82'       # putting the E axis into absolute mode independent of the other axes

        self.complex_f_rate = False

    def setComplexFeedrate(self, peak_feed_rate = None, min_h_ramp = (10, 20), max_h_ramp = (120, 130)):

        self.complex_f_rate = True

        self.f_rate_peak = peak_feed_rate * 60.0

        self.start_ramp = False

        self.z_ramp_start_min, self.z_ramp_start_max = min_h_ramp
        self.z_ramp_end_max, self.z_ramp_end_min = max_h_ramp

        if self.z_ramp_start_min == self.z_ramp_start_max:

            self.start_ramp_complex = False

        else:

            self.start_ramp_complex = True

        if self.z_ramp_end_min == self.z_ramp_end_max:

            self.end_ramp_complex = False

        else:

            self.end_ramp_complex = True

        self.f_delta = self.f_rate_peak - self.f_rate
        self.z_delta_start = self.z_ramp_start_max - self.z_ramp_start_min
        self.z_delta_end = self.z_ramp_end_max - self.z_ramp_end_min

    def zBasedFeedrate(self, z):

        if self.complex_f_rate:

            if self.z_ramp_start_min > z:

                return self.f_rate
            
            elif self.z_ramp_start_max > z and self.start_ramp_complex:

                z_norm = ( z - self.z_ramp_start_min ) / self.z_delta_start

                f_interpolate = self.f_rate + self.f_delta * z_norm

                return int(f_interpolate)

            elif self.z_ramp_end_max > z:

                return self.f_rate_peak

            elif self.z_ramp_end_min > z and self.end_ramp_complex:

                z_norm = ( z - self.z_ramp_end_max ) / self.z_delta_end

                f_interpolate = self.f_rate_peak - self.f_delta * z_norm

                return int(f_interpolate)

            else:

                return self.f_rate

        else:

            return self.f_rate


class GCodeSet(object):

    def __init__(self, pt_lists, print_settings = PrintSettings(), link_type = LinkType()):

        self.p_set = print_settings
        self.l_type = link_type

        self.multi_list = False
        self.link_type = link_type

        if isinstance((pt_lists[0]), list):

            print("I am a nested list")

            self.multi_list = True

        # the case where one doesn't need to impliment any start_stop functions
        # lists sets can be cascaded into a single 

        if not(self.l_type.start_stop) and self.multi_list:
            
            self.locations = []

            for pt_list in pt_lists:

                self.locations.extend(pt_list)

        elif not(self.l_type.start_stop):

            self.locations = pt_lists

        # case with start_stop

        elif self.l_type.start_stop:

            self.locations = pt_lists

        # visualization of the path points

        self.path_vis = []


    def locationListGeneration(self, input_list = None, first_pt = True):

        if input_list == None:
            # if no input list givenm assume that the locations list will be used

            input_list = self.locations

        input_list = shortenPolylineSet(input_list, value = self.l_type.trim_d, location = "both")

        if self.l_type.cull:
            # checking whether the first value is too short

            input_list = collapsePolylinePts(input_list, value = self.l_type.cull_distance)

        loc_count = len(input_list)
        output_list = []

        # 2nd point e_val

        distance = input_list[1].DistanceTo(input_list[1 - 1])
        ex_val = self.p_set.e_rate * distance

        if first_pt:
            output_list.append(g_line_gen(input_list[0], f_val = self.p_set.f_rate))
            output_list.append(g_line_gen(input_list[1], ex_val))

            self.path_vis.extend(input_list)

        else:
            output_list.append(g_line_gen(input_list[1], ex_val, f_val = self.p_set.f_rate))

            self.path_vis.extend(input_list[1:])

        for i in range(2, loc_count, 1):

            distance = input_list[i].DistanceTo(input_list[i - 1])
            ex_val = self.p_set.e_rate * distance

            output_list.append(
                g_line_gen(input_list[i],
                ex_val,
                f_val = self.p_set.zBasedFeedrate(input_list[i].Z)
            ))

        return output_list

    def startStopLisGeneration(self):

        self.locations[0] = shortenPolylineSet(self.locations[0], value = self.l_type.trim_d, location = "start")
        self.locations[-1] = shortenPolylineSet(self.locations[-1], value = self.l_type.trim_d, location = "end")

        output_list = []

        for i in range(len(self.locations) - 1):

            self.locations[i] = shortenPolylineSet(self.locations[i], value = self.l_type.ss_trim_d, location = "end")
            
            if self.l_type.cull:
            # checking whether the first value is too short

                self.locations[i] = collapsePolylinePts(self.locations[i], value = self.l_type.cull_distance)

            if i > 0:

                output_list.extend(self.locationListGeneration(self.locations[i], first_pt = False))

            else:

                output_list.extend(self.locationListGeneration(self.locations[i]))
            
            self.locations[i + 1] = shortenPolylineSet(self.locations[i + 1], value = self.l_type.ss_trim_d, location = "start")

            # generating the start stop sequence
            pt_0 = self.locations[i][-1]
            pt_1 = self.locations[i + 1][0]

            output_list.extend([
                g_line_gen(pt_0 + self.l_type.ss_lift, -self.l_type.ss_e_rate, self.l_type.ss_f_rate),
                g_line_gen(pt_1 + self.l_type.ss_lift),
                g_line_gen(pt_1, self.l_type.ss_e_rate)
            ])

            self.path_vis.extend([pt_0 + self.l_type.ss_lift, pt_1 + self.l_type.ss_lift, pt_1])

        # addding the final line

        if self.l_type.cull:
            # checking whether the first value is too short

            self.locations[-1] = collapsePolylinePts(self.locations[i], value = self.l_type.cull_distance)

        output_list.extend(self.locationListGeneration(self.locations[-1], first_pt = False))

        return output_list

    def generateGCode(self):

        print(self.multi_list)

        if self.l_type.start_stop and self.multi_list:

            return self.startStopLisGeneration()

        else:

            return self.locationListGeneration()


def g_line_gen(coordinates, e_val = None, f_val = None):

    # making it so that the coordinates can also be points and vectors

    string_set = ['G1']

    if not(f_val == None):

        string_set.extend([' F', str(f_val)])

    string_set.extend([' X', str(coordinates[0])])
    string_set.extend([' Y', str(coordinates[1])])

    if not(abs(coordinates[2]) < 0.0001):

        string_set.extend([' Z', str(coordinates[2])])

    if not(e_val == None):

        string_set.extend([' E', str(e_val)])

    return ''.join(string_set)

def file_count(nozzle_diameter, json_file):

    nozzle_dia_txt = "{:.1f}".format(nozzle_diameter).replace(".","_")

    with open(json_file, "r+") as read_file:

        current_data = json.load(read_file)

        try:

            current_count = current_data[nozzle_dia_txt]
            current_data[nozzle_dia_txt] += 1

        except:

            current_count = 1
            current_data[nozzle_dia_txt] = 2

        print(current_data)

        read_file.seek(0)  # rewind
        json.dump(current_data, read_file)
        read_file.truncate()

    return "{}.{}".format(nozzle_dia_txt[0], str(current_count))


# def start_stop_sequence(list_a, list_b, extrusion_rate = 2.0, h_shift = 5.0, extrusion_val = -250.0, cut_off_length = 10.0):

#     h_shift_pt = rg.Point3d(0,0,h_shift)

#     end_loc_min1 = list_a[-2]
#     end_loc_prev = list_a[-1]
#     end_loc_safety = end_loc_prev + h_shift_pt
#     start_loc_next = list_b[0]
#     start_loc_safety = start_loc_next + h_shift_pt

#     tmp_pts = [end_loc_prev, end_loc_safety, start_loc_safety, start_loc_next]

#     tmp_g_lines = [
#         g_line_gen([tmp_pts[0].X, tmp_pts[0].Y, tmp_pts[0].Z], extrusion_val),
#         g_line_gen([tmp_pts[1].X, tmp_pts[1].Y, tmp_pts[1].Z], 0.0),
#         g_line_gen([tmp_pts[2].X, tmp_pts[2].Y, tmp_pts[2].Z], 0.0),
#         g_line_gen([tmp_pts[3].X, tmp_pts[3].Y, tmp_pts[3].Z], -extrusion_val)
#     ]

#     segment_length = end_loc_min1.DistanceTo(end_loc_prev)

#     if segment_length > cut_off_length:
#         # checking whether an extra point should be added if the last segment ends up being too long

#         print("previous segment was a bit too long!")
        
#         length_delta = segment_length - cut_off_length

#         mv_pt = (end_loc_prev - end_loc_min1) * (length_delta / segment_length)

#         ex_pt = end_loc_min1 + mv_pt

#         g_line = g_line_gen([ex_pt.X, ex_pt.Y, ex_pt.Z], extrusion_rate * segment_length)

#         tmp_g_lines = [g_line] + tmp_g_lines

#     return tmp_g_lines


# def pathGCodeLooper(list_locs, extrusion_rate, extra_z = 0.0):

#     loc_g_lines = []

#     for i in range(1, len(list_locs), 1):

#         coordinates = [list_locs[i].X, list_locs[i].Y, list_locs[i].Z + extra_z]
#         extrusion_val = list_locs[i].DistanceTo(list_locs[i - 1]) * extrusion_rate

#         loc_g_lines.append(g_line_gen(coordinates, extrusion_val))

#     return loc_g_lines


# def gCodeGenerator(line_list, extrusion_rate, link_type = "start/stop", extra_z = 0.0):

#     line_count =  len(line_list)

#     if line_count == 1:

#         pass




# def gCodeGenerator(lists, extrusion_rate, extra_z = 0.0):

#     print(extra_z)

#     g_lines = []

#     if extra_z > .01:

#         z_shift = True

#         tmp_lists = []

#         for list_locs in lists:

#             tmp_list_locs = []
#             for loc in list_locs:

#                 tmp_pt = rg.Point3d(loc.X, loc.Y, loc.Z + extra_z)

#                 tmp_list_locs.append(tmp_pt)

#             tmp_lists.append(tmp_list_locs)

#         lists = tmp_lists

#     print(z_shift)

#     for list_i, list_locs in enumerate(lists):

#         if z_shift:

#             print(" I am being performed! ")

#         if list_i == 0:
#             # first path

#             coordinates = [list_locs[0].X, list_locs[0].Y, list_locs[0].Z]

#             g_lines.append(g_line_gen(coordinates))

#             g_lines.extend(pathGCodeLooper(list_locs, extrusion_rate, 1))

#         elif list_i == len(lists) - 1:
#             # last path

#             g_lines.extend(start_stop_sequence(lists[list_i - 1], list_locs, extrusion_rate))

#             g_lines.extend(pathGCodeLooper(list_locs, extrusion_rate))

#         else:
#             # other paths

#             g_lines.extend(start_stop_sequence(lists[list_i - 1], list_locs, extrusion_rate))

#             g_lines.extend(pathGCodeLooper(list_locs, extrusion_rate, 1))

#     return g_lines