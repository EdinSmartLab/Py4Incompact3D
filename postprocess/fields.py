# Copyright 2018 Georgios Deskos
# Copyright 2018 Paul Bartholomew

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import numpy as np

class Field():

    def __init__(self, instance_dictionary):

        super().__init__()

        self.name = instance_dictionary["name"]
        self.description = instance_dictionary["description"]

        properties = instance_dictionary["properties"]
        self.file_root = properties["filename"]
        self.direction = properties["direction"]
        if "precision" in "properties":
            if properties["precision"] == "single":
                self.dtype = np.float32
            else:
                self.dtype = np.float64
        else: # Default to double precision
            self.dtype = np.float64

        self.data = {}

    def _read(self, filename, nx, ny, nz, dtype=np.float64):
        """ Reads a datafile generated by Incompact3D into a (3D) numpy array. 
        
        :param filename: The file to read.
        :param nx: The mesh x resolution.
        :param ny: The mesh y resolution.
        :param nz: The mesh z resolution.
        :param dtype:
        """
        
        N = nx * ny * nz
        with open(filename, "rb") as bindat:
            fldat = np.fromfile(bindat, dtype)
            assert(len(fldat) == N)
            
        return np.reshape(fldat, (nx, ny, nz), "F")
        
    def load(self, mesh, time=-1):
        """ Loads a datafield timeseries.

        :param mesh: The mesh the data is stored on.
        :param time: Time(s) to load data, default value -1 means load all times.

        :type mesh: Py4Incompact3D.postprocess.mesh.Mesh
        :type time: int or list of int
        """

        # Find all files to load
        if time == -1:
            load_times = range(1000) # This corresponds to 4-digit timestamp
        elif isinstance(time, int):
            load_times = [time]
        elif isinstance(time, list):
            load_times = time
        else:
            raise ValueError

        for t in load_times:
            zeros = ""
            read_success = False
            while (not read_success) and (len(zeros) < 10):
                try:
                    filename = self.file_root + zeros + str(t)
                    self.data[t] = self._read(filename, mesh.Nx, mesh.Ny, mesh.Nz, self.dtype)
                except:
                    zeros += "0"
                else:
                    read_success = True
                    
            if not read_success:
                raise RuntimeError

    def write(self, time, timestamp_len=3):
        """"""

        if time == -1:
            write_times = self.data.keys()
        elif isinstance(time, int):
            write_times = [time]
        elif isinstance(time, list):
            write_times = time
        else:
            raise ValueError

        for t in write_times:
            timestamp = str(t)
            timestamp = "0" * (timestamp_len - len(timestamp)) + timestamp
            filename = self.file_root + timestamp

            # Dump to raw binary, numpy writes in 'C' order so we need to shuffle our
            # array so that 'C' order looks like 'Fortran' order...
            self.data[t] = np.swapaxes(self.data[t], 0, 2)
            self.data[t].tofile(filename)

            # Shuffle back to 'C' order incase we want to keep working with the array
            self.data[t] = np.swapaxes(self.data[t], 2, 0)

    def clear(self):
        """ Cleanup data. """
        self.data= {}
        
