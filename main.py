#this script rips subtitles from a mp4 into the srt format
#required: mp4box, subtitle edit
#author: Owen Russell-Lanning


from tkinter import Tk     
from tkinter.filedialog import askopenfilename
import os
from pathlib import Path
import shutil
import subprocess

Tk().withdraw() 

#command list images
#mp4box -raw 3 (name)
#SubtitleEdit /convert (name) srt

#command list srt
#mp4box -srt (channel #) (name)

#returns a list of tracks and there language [number, lang] which contains subtitles within the mp4 file at the given path
def get_subtitle_track_numbers(file_path):
    #capture file info
    output = str(subprocess.check_output("mp4box -info \""+file_path+"\"", stderr=subprocess.STDOUT))
    #get track sections
    line_sections = output.split("\\r")
    sections = []
    current_section = ""
    for line_section in line_sections:
        if line_section == "\\n":
            sections.append(current_section.replace("\\n","\n").replace("\\t", "\t"))
            current_section = ""
        else:
            current_section = current_section + line_section
    #sections found
    #look for sub tracks
    sub_tracks = []
    for section in sections:
        if "Type \"subp:mp4s\"" in section: #track is subtitles
            #get track number
            number = section[9:][:1]
            #get track language
            starting_pos = section.find("Language")
            rest_str = section[starting_pos:]
            rest_str = rest_str[rest_str.find("\"")+1:]
            language = rest_str[:rest_str.find("\"")]
            sub_tracks.append([number, language])
    return sub_tracks

def rip_image_subs_from_video_file(filename, track, language):
    print("Getting subtitles from "+filename+" in " + language)
    os.system("mp4box -raw "+track+" \"" + filename +"\"") #get idx and sub file
    parent_folder = os.path.dirname(filename)
    filename_without_extension = Path(filename).stem

    sub_file = os.path.join(parent_folder, filename_without_extension +"_track"+track+".sub")
    idx_file = os.path.join(parent_folder, filename_without_extension +"_track"+track+".idx")
    cwd = os.getcwd()

    if os.path.isfile(sub_file) and os.path.isfile(idx_file): #copy files to working dir
        new_sub = os.path.join(cwd, "subs.sub")
        new_idx = os.path.join(cwd, "subs.idx")
        shutil.move(sub_file, new_sub)
        shutil.move(idx_file, new_idx)

        #convert to srt file
        print("Converting to SRT")
        os.system("SubtitleEdit /convert \""+ new_sub +"\" srt")

        #copy new srt to original mp4 location
        shutil.move(os.path.join(cwd, "subs.srt"), os.path.join(parent_folder, language + ".srt"))
    



    else:
        print("Error getting sub and idx")
        exit()



    


#get user to select a method either image based subtitle or text based
print("Select a method")
print("1 - Image Based Subtitles")
print("2 - Text Based Subtitles")
method =  input("Method: ")
while  method != "1" and method != "2":
    print("Method not recognized. Try again.")
    method = input("Method: ")
    
print("Method found")
print("Select video file")

filename = askopenfilename(initialdir = "/",title = "Select video file",filetypes = (("MP4","*.mp4"),("M4V","*.m4v"))) 
print("Selected: "  + filename)

if filename == "" or not os.path.isfile(filename):
    print("File not found")
    exit()
elif method == "1": #image based subtitles
    tracks = get_subtitle_track_numbers(filename)
    for track in tracks:     
        rip_image_subs_from_video_file(filename, track[0], track[1])
    print("Finished")


elif method == "2": #text based subtitles
     os.system("mp4box -srt 3 \"" + filename +"\"") #get idx and sub file
     print("Finished")
     
     
