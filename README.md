# 3DPNet-DICOM
  3DPNet-DICOM is an application software used to print DICOM files (from CT-Scan) using a 3D printer automatically 
(without User Interface during the process). 3DPNet-DICOM based on cloud.The object of the medical image is focused on the bone. 

  3DPNet-DICOM can be used seperately or in other applications. Feel free to add it to your application. 
But please take note of the License.

# License
  3DPNet-DICOM is released under terms of the GNU GPL v3 License. Terms of the license can be found in the LICENSE file. 
Or at http://www.gnu.org/licenses/gpl-3.0txt.

# Internal
  3DPNet-DICOM structure consist of two main programs, namely app.py (convert DICOM file to stereolithography file) 
and 3d_print.py (send stereolithography file to the 3D Printer). The programming language uses Python ver. 3.x.
  
  The algorithm of app.py is:
  1. Upload DICOM file in zip format, using web application.
  2. Extract a zip DICOM file.
  3. Bone Segmentation and Reconstruction from DICOM file, using Improved Marching Cube Algorithm (G.L. Masala, B. Golosio, 
     and P. Oliva, "An ImprovedMarching Cube Algorithm for 3D Data Segmentation", Computer Physics Communication, vol. 184, 
     no. 3, pp. 777-782, March 2013).
  4. Confert to stereolithography file and save to history stl folder and temporary stl folder.

  The algorithm of 3d_print.py is:
  Loop:
  1. Connect 3D Printer status.
  2. If (3D Printer is ready) and (temporay stl folder has contents) then read previous stl file.
  3. Slicing stl file using API CuraEngine 15.04.6 <https://github.com/Ultimaker/CuraEngine>
  4. Resize 3D image dimension with the working area of 3D Printer.
  5. Convert to GCode file.
  6. Send GCode file to 3D Printer, heating, and printing process.
  7. If printing process is finish the send notification to customer order (doctor / patient) via email.
  End Loop.
  
  Note: 
  1. Communication 3D Printer with computer using OctoPrint remote system <https://github.com/OctoPrint). 
  2. Receiver communication with 3D Printer using Raspberry Pi 3.
  3. SSH Client used to connect to a remote server using PuTTY <https://www.putty.org>.
