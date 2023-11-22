"""
A module to read, write, and crop optical coherence tomography images from Heidelberg Engineering written in the .vol file format.
"""

import numpy as np
import datetime


class OCTVol:
    """
    The OCTVol object contains an optical coherence tomography (OCT) image with its information read from Heidelberg
    Engineering (HE) *.vol file format.

    Parameters
    ----------
    vol_path : str
         Path to the vol file.

     Attributes
     ----------
     vol_path : str
        The path to the vol file.
     header : dict
        A dictionary containing the vol file information e.g. 'num_b_scans', 'size_x', 'exam_time', etc.
    slo : numpy.ndarray
        The SLO image enclosed in the vol file.
    b_scan_header : dict
        A dictionary containing B scan specific information and segmentation e.g. 'quality', 'boundary_1', etc.
    b_scans : numpy.ndarray
        The OCT image with the shape (size_z, size_x, num_b_scans).
    thickness_grid : dict
        A dictionary containing the thickness map and related information e.g. 'grid_type', 'central_thk', etc.

    Class Attributes
    ----------------
    EXAM_TIME_OFFSET : int
        The time origin change from python origin to exam_time origin of the vol file 1/1/1601 in seconds (needed for
        conversion from timestamp).
    VISIT_DATE_DOB_OFFSET : int
        The offset needs to convert visit_date and dob (date of birth) from int to time.

    Raises
    ------
    ValueError
        if the file does not contain .vol in the file name.

    Notes
    -----
    1-An OCTVol object is created according to the structure of HE vol files. Please see the documentation that comes
      with .vol export license for more information.
    2-The header attribute has three data in addition to the ones mentioned in the .vol documentation,
      'unconverted_exam_time', 'unconverted_dob', and 'unconverted_visit_date' which are the raw numbers for the dates
      before conversion, used in write_vol method.

    :Authors:
        Seyedamirhosein Motamedi, Charité - Universitätsmedizin Berlin,
        seyedamirhosein.motamedi@charite.de

    """
    EXAM_TIME_OFFSET = (datetime.date.toordinal(datetime.date(1970, 1, 1)) -
                        datetime.date.toordinal(datetime.date(1601, 1, 1))) * 24 * 60 * 60
    VISIT_DATE_DOB_OFFSET = (datetime.date.toordinal(datetime.date(1970, 1, 1)) -
                             datetime.date.toordinal(datetime.date(1899, 12, 30))) * 24 * 60 * 60

    def __init__(self, vol_path):
        if '.vol' not in vol_path:
            raise ValueError('The file path does not point to a .vol file. Please check the path and make sure that the full path is given including the file .vol extension.')
        self.vol_path = vol_path
        self.header, self.slo, self.b_scan_header, self.b_scans, self.thickness_grid = OCTVol._open_vol(vol_path)

    @classmethod
    def _open_vol(cls, vol_path):
        """"
        Read (open) OCT .vol files.

        Parameters
        -----------
        vol_path : str
            Path to the vol file.

        Returns
        -------
        tuple
            header, slo, b_scan_header, b_scans, thickness_grid read from the oct vol file.

        Notes
        -----
        This is an internal class method. Strongly recommend creating an OCTVOL object instead of calling this function
        directly.

        """
        # Open the file and read header, slo image, B scan header (segmentation), B scans, and thickness grid
        with open(vol_path, mode='rb') as vf:

            # Read Header
            header = dict(version="".join(map(chr, vf.read(12))).rstrip("\0"),
                          size_x=np.fromfile(vf, dtype='int32', count=1)[0],
                          num_b_scans=np.fromfile(vf, dtype='int32', count=1)[0],
                          size_z=np.fromfile(vf, dtype='int32', count=1)[0],
                          scale_x=np.fromfile(vf, dtype='float64', count=1)[0],
                          distance=np.fromfile(vf, dtype='float64', count=1)[0],
                          scale_z=np.fromfile(vf, dtype='float64', count=1)[0],
                          size_x_slo=np.fromfile(vf, dtype='int32', count=1)[0],
                          size_y_slo=np.fromfile(vf, dtype='int32', count=1)[0],
                          scale_x_slo=np.fromfile(vf, dtype='float64', count=1)[0],
                          scale_y_slo=np.fromfile(vf, dtype='float64', count=1)[0],
                          field_size_slo=np.fromfile(vf, dtype='int32', count=1)[0],
                          scan_focus=np.fromfile(vf, dtype='float64', count=1)[0],
                          scan_position="".join(map(chr, vf.read(4))).rstrip("\0"),
                          unconverted_exam_time=np.fromfile(vf, dtype='uint64', count=1)[0],
                          scan_pattern=np.fromfile(vf, dtype='int32', count=1)[0],
                          b_scan_hdr_size=np.fromfile(vf, dtype='int32', count=1)[0],
                          id="".join(map(chr, vf.read(16))).rstrip("\0"),
                          reference_id="".join(map(chr, vf.read(16))).rstrip("\0"),
                          pid=np.fromfile(vf, dtype='int32', count=1)[0],
                          patient_id="".join(map(chr, vf.read(21))).rstrip("\0"),
                          padding=np.fromfile(vf, dtype='int8', count=3),
                          unconverted_dob=np.fromfile(vf, dtype='float64', count=1)[0],
                          vid=np.fromfile(vf, dtype='int32', count=1)[0],
                          visit_id="".join(map(chr, vf.read(24))).rstrip("\0"),
                          unconverted_visit_date=np.fromfile(vf, dtype='float64', count=1)[0],
                          grid_type=np.fromfile(vf, dtype='int32', count=1)[0],
                          grid_offset=np.fromfile(vf, dtype='int32', count=1)[0],
                          spare=np.fromfile(vf, dtype='int8', count=1832))
            header['exam_time'] = datetime.datetime.utcfromtimestamp(header['unconverted_exam_time']/1e7 - OCTVol.EXAM_TIME_OFFSET)
            header['dob'] = (datetime.datetime.utcfromtimestamp(0) + datetime.timedelta(seconds=header['unconverted_dob']*24*60*60 - OCTVol.VISIT_DATE_DOB_OFFSET)).date()
            header['visit_date'] = datetime.datetime.utcfromtimestamp(header['unconverted_visit_date']*24*60*60 - OCTVol.VISIT_DATE_DOB_OFFSET)

            # Read SLO image
            vf.seek(2048)
            slo = np.fromfile(vf, dtype='uint8', count=header['size_x_slo']*header['size_y_slo']).reshape((header['size_y_slo'], header['size_x_slo']))

            # Create B scan and B scan header objects
            b_scan_header = dict(version=np.full((12, header['num_b_scans']), "\0", dtype='U'),
                                 b_scan_hdr_size=np.full(header['num_b_scans'], np.nan, dtype='int32'),
                                 start_x=np.full(header['num_b_scans'], np.nan, dtype='float64'),
                                 start_y=np.full(header['num_b_scans'], np.nan, dtype='float64'),
                                 end_x=np.full(header['num_b_scans'], np.nan, dtype='float64'),
                                 end_y=np.full(header['num_b_scans'], np.nan, dtype='float64'),
                                 num_seg=np.full(header['num_b_scans'], np.nan, dtype='int32'),
                                 off_seg=np.full(header['num_b_scans'], np.nan, dtype='int32'),
                                 quality=np.full(header['num_b_scans'], np.nan, dtype='float32'),
                                 shift=np.full(header['num_b_scans'], np.nan, dtype='int32'),
                                 spare=np.full((192, header['num_b_scans']), np.nan, dtype='int8'))
            b_scans = np.full((header['size_z'], header['size_x'], header['num_b_scans']), np.nan, dtype='float32')

            # Read B scan and B scan header (incl. segmentation)
            for i_b_scan in range(header['num_b_scans']):
                # go to the position of the B scan header on the file
                vf.seek(2048 + header['size_x_slo'] * header['size_y_slo'] + i_b_scan * (header['b_scan_hdr_size'] + header['size_x'] * header['size_z'] * 4))

                # Read B scan header (except segmentation)
                b_scan_header['version'][:, i_b_scan] = [*map(chr, vf.read(12))]
                b_scan_header['b_scan_hdr_size'][i_b_scan] = np.fromfile(vf, dtype='int32', count=1)
                b_scan_header['start_x'][i_b_scan] = np.fromfile(vf, dtype='float64', count=1)
                b_scan_header['start_y'][i_b_scan] = np.fromfile(vf, dtype='float64', count=1)
                b_scan_header['end_x'][i_b_scan] = np.fromfile(vf, dtype='float64', count=1)
                b_scan_header['end_y'][i_b_scan] = np.fromfile(vf, dtype='float64', count=1)
                b_scan_header['num_seg'][i_b_scan] = np.fromfile(vf, dtype='int32', count=1)
                b_scan_header['off_seg'][i_b_scan] = np.fromfile(vf, dtype='int32', count=1)
                b_scan_header['quality'][i_b_scan] = np.fromfile(vf, dtype='float32', count=1)
                b_scan_header['shift'][i_b_scan] = np.fromfile(vf, dtype='int32', count=1)
                b_scan_header['spare'][:, i_b_scan] = np.fromfile(vf, dtype='int8', count=192)

                # Create boundaries items now that we know the number of segmentation lines from the first iteration
                if i_b_scan == 0:
                    for i_boundary in range(b_scan_header['num_seg'][0]):
                        b_scan_header['boundary_{}'.format(i_boundary + 1)] = np.full((header['num_b_scans'], header['size_x']), np.nan, dtype='float32')

                # Read segmentation
                vf.seek(2048 + header['size_x_slo'] * header['size_y_slo'] + b_scan_header['off_seg'][i_b_scan] + i_b_scan * (header['b_scan_hdr_size'] + header['size_x'] * header['size_z'] * 4))
                for i_boundary in range(b_scan_header['num_seg'][i_b_scan]):
                    b_scan_header['boundary_{}'.format(i_boundary+1)][i_b_scan, :] = np.fromfile(vf, dtype='float32', count=header['size_x'])

                # Read B scans
                vf.seek(2048 + header['size_x_slo'] * header['size_y_slo'] + header['b_scan_hdr_size'] + i_b_scan * (header['b_scan_hdr_size'] + header['size_x'] * header['size_z'] * 4))
                b_scans[:, :, i_b_scan] = np.fromfile(vf, dtype='float32', count=header['size_x'] * header['size_z']).reshape((header['size_z'], header['size_x']))

            # Read the thickness info if it exists
            if header['grid_type'] != 0:
                vf.seek(header['grid_offset'])

                # Read the thickness grid up to the sector part
                thickness_grid = dict(type=np.fromfile(vf, dtype='int32', count=1)[0],
                                      diameter=np.fromfile(vf, dtype='float64', count=3),
                                      center_pos=np.fromfile(vf, dtype='float64', count=2),
                                      central_thk=np.fromfile(vf, dtype='float32', count=1)[0],
                                      min_central_thk=np.fromfile(vf, dtype='float32', count=1)[0],
                                      max_central_thk=np.fromfile(vf, dtype='float32', count=1)[0],
                                      total_volume=np.fromfile(vf, dtype='float32', count=1)[0])

                # Read sectors information
                for i_sector in range(9):
                    thickness_grid['sector_{}'.format(i_sector+1)] = dict(thickness=np.fromfile(vf, dtype='float32', count=1)[0],
                                                                          volume=np.fromfile(vf, dtype='float32', count=1)[0])
            else:
                thickness_grid = dict()

        return header, slo, b_scan_header, b_scans, thickness_grid

    def write_vol(self, write_vol_path):
        """
        Write the OCTVol object, which contains an OCT image and its information, into a .vol file.

        Parameters
        ----------
        write_vol_path : str
            The path where the vol file is written to.

        """
        with open(write_vol_path if '.vol' in write_vol_path else write_vol_path + '.vol', 'wb') as vf:
            # Write the header
            vf.write(self.header['version'].encode() + (12 - len(self.header['version'])) * b'\0')
            self.header['size_x'].tofile(vf)
            self.header['num_b_scans'].tofile(vf)
            self.header['size_z'].tofile(vf)
            self.header['scale_x'].tofile(vf)
            self.header['distance'].tofile(vf)
            self.header['scale_z'].tofile(vf)
            self.header['size_x_slo'].tofile(vf)
            self.header['size_y_slo'].tofile(vf)
            self.header['scale_x_slo'].tofile(vf)
            self.header['scale_y_slo'].tofile(vf)
            self.header['field_size_slo'].tofile(vf)
            self.header['scan_focus'].tofile(vf)
            vf.write(self.header['scan_position'].encode() + (4 - len(self.header['scan_position'])) * b'\0')
            self.header['unconverted_exam_time'].tofile(vf)
            self.header['scan_pattern'].tofile(vf)
            self.header['b_scan_hdr_size'].tofile(vf)
            vf.write(self.header['id'].encode() + (16 - len(self.header['id'])) * b'\0')
            vf.write(self.header['reference_id'].encode() + (16 - len(self.header['reference_id'])) * b'\0')
            self.header['pid'].tofile(vf)
            vf.write(self.header['patient_id'].encode() + (21 - len(self.header['patient_id'])) * b'\0')
            self.header['padding'].tofile(vf)
            self.header['unconverted_dob'].tofile(vf)
            self.header['vid'].tofile(vf)
            vf.write(self.header['visit_id'].encode() + (24 - len(self.header['visit_id'])) * b'\0')
            self.header['unconverted_visit_date'].tofile(vf)
            self.header['grid_type'].tofile(vf)
            self.header['grid_offset'].tofile(vf)
            self.header['spare'].tofile(vf)

            # Write the slo image
            vf.seek(2048)
            self.slo.reshape(-1).tofile(vf)

            # Write BScan and BScan header
            for i_b_scan in range(self.header['num_b_scans']):
                vf.seek(2048 + self.header['size_x_slo']*self.header['size_y_slo'] + i_b_scan*(self.header['b_scan_hdr_size']+self.header['size_x']*self.header['size_z']*4))
                np.vectorize(str.encode)(self.b_scan_header['version'][:, i_b_scan]).tofile(vf)
                self.b_scan_header['b_scan_hdr_size'][i_b_scan].tofile(vf)
                self.b_scan_header['start_x'][i_b_scan].tofile(vf)
                self.b_scan_header['start_y'][i_b_scan].tofile(vf)
                self.b_scan_header['end_x'][i_b_scan].tofile(vf)
                self.b_scan_header['end_y'][i_b_scan].tofile(vf)
                self.b_scan_header['num_seg'][i_b_scan].tofile(vf)
                self.b_scan_header['off_seg'][i_b_scan].tofile(vf)
                self.b_scan_header['quality'][i_b_scan].tofile(vf)
                self.b_scan_header['shift'][i_b_scan].tofile(vf)
                self.b_scan_header['spare'][:, i_b_scan].tofile(vf)
                vf.seek(2048 + self.header['size_x_slo']*self.header['size_y_slo'] + i_b_scan*(self.header['b_scan_hdr_size']+self.header['size_x']*self.header['size_z']*4) + self.b_scan_header['off_seg'][i_b_scan])
                for i_boundary in range(self.b_scan_header['num_seg'][i_b_scan]):
                    self.b_scan_header['boundary_{}'.format(i_boundary+1)][i_b_scan, :].tofile(vf)
                vf.seek(2048 + self.header['size_x_slo']*self.header['size_y_slo'] + i_b_scan*(self.header['b_scan_hdr_size']+self.header['size_x']*self.header['size_z']*4) + self.header['b_scan_hdr_size'])
                self.b_scans[:, :, i_b_scan].reshape(-1).tofile(vf)

            # Write the thickness grid if it exists
            vf.seek(self.header['grid_offset'])
            if self.header['grid_type'] != 0:
                self.thickness_grid['type'].tofile(vf)
                self.thickness_grid['diameter'].tofile(vf)
                self.thickness_grid['center_pos'].tofile(vf)
                self.thickness_grid['central_thk'].tofile(vf)
                self.thickness_grid['min_central_thk'].tofile(vf)
                self.thickness_grid['max_central_thk'].tofile(vf)
                self.thickness_grid['total_volume'].tofile(vf)
                for i_sector in range(9):
                    self.thickness_grid['sector_{}'.format(i_sector+1)]['thickness'].tofile(vf)
                    self.thickness_grid['sector_{}'.format(i_sector+1)]['volume'].tofile(vf)

    def crop_vol(self, crop_size=6):
        """
        Crop the volume of an OCTVol object and update its corresponding information.

        Parameters
        ----------
        crop_size : float | int, optional
            The crop size which will be applied to both A-scan (x) and B-scan (y) directions. Defaults to 6 (ETDRS area).

        Returns
        -------
        None
            This method operates in-place, modifying the OCTVol object directly to store the result.

        Notes
        -----
        When a 6mm crop is selected, the grid type is updated to ETDRS, and the sector parameters are reset accordingly.
        This update is particularly useful when using programs like OCTMarker or SAMIRIX for segmentation correction.
        It allows users to easily determine whether they are within the ETDRS map or not.

        """
        # Find the position of the fovea (center) on the volume
        slo_volume_angle = np.math.atan((self.b_scan_header['end_y'][0]-self.b_scan_header['end_y'][-1]) / (self.b_scan_header['end_x'][0]-self.b_scan_header['end_x'][-1]))
        if self.b_scan_header['end_x'][-1] > self.b_scan_header['end_x'][0]:
            slo_volume_angle += np.pi
        center_position_x_mm = -(self.thickness_grid['center_pos'][0] - self.b_scan_header['end_x'][-1]) * np.math.sin(slo_volume_angle) + (self.thickness_grid['center_pos'][1] - self.b_scan_header['end_y'][-1]) * np.math.cos(slo_volume_angle)
        center_position_y_mm = (self.thickness_grid['center_pos'][0] - self.b_scan_header['end_x'][-1]) * np.math.cos(slo_volume_angle) + (self.thickness_grid['center_pos'][1] - self.b_scan_header['end_y'][-1]) * np.math.sin(slo_volume_angle)
        center_position_a_scan = self.header['size_x'] - np.round(center_position_x_mm / self.header['scale_x'] * 2)/2
        center_position_b_scan = self.header['num_b_scans'] - np.round(center_position_y_mm / self.header['distance'] * 2)/2

        # Find the boundaries for the cropping (these are the number of the A scans and B scans and not their index)
        first_a_scan = np.maximum(int(np.ceil(center_position_a_scan - (crop_size / self.header['scale_x'] / 2))), 1)
        last_a_scan = np.minimum(int(np.floor(center_position_a_scan + (crop_size / self.header['scale_x'] / 2))), self.header['size_x'])
        first_b_scan = np.maximum(int(np.ceil(center_position_b_scan - (crop_size / self.header['distance'] / 2))), 1)
        last_b_scan = np.minimum(int(np.floor(center_position_b_scan + (crop_size / self.header['distance'] / 2))), self.header['num_b_scans'])

        # Crop the boundary segmentation in the b_scan_header
        for i_boundary in range(self.b_scan_header['num_seg'][0]):
            self.b_scan_header['boundary_{}'.format(i_boundary+1)] = self.b_scan_header['boundary_{}'.format(i_boundary+1)][first_b_scan-1:last_b_scan, first_a_scan-1:last_a_scan]

        # Crop B scans
        self.b_scans = self.b_scans[:, first_a_scan-1:last_a_scan, first_b_scan-1:last_b_scan]

        # Recalculate the start and end of each B scan
        self.b_scan_header['start_x'] = self.b_scan_header['start_x'] + (first_a_scan - 1) * self.header['scale_x'] * np.math.cos(3 * np.pi / 2 + slo_volume_angle)
        self.b_scan_header['start_y'] = self.b_scan_header['start_y'] + (first_a_scan - 1) * self.header['scale_x'] * np.math.sin(3 * np.pi / 2 + slo_volume_angle)
        self.b_scan_header['end_x'] = self.b_scan_header['end_x'] + (self.header['size_x'] - last_a_scan) * self.header['scale_x'] * np.math.cos(np.pi / 2 + slo_volume_angle)
        self.b_scan_header['end_y'] = self.b_scan_header['end_y'] + (self.header['size_x'] - last_a_scan) * self.header['scale_x'] * np.math.sin(np.pi / 2 + slo_volume_angle)

        # Update the size_x and num_b_scans in the header
        self.header['size_x'] = last_a_scan - first_a_scan + 1
        self.header['num_b_scans'] = last_b_scan - first_b_scan + 1

        # Update the grid_offset in the header
        self.header['grid_offset'] = 2048 + self.header['size_x_slo'] * self.header['size_y_slo'] + self.header['num_b_scans'] * (self.header['b_scan_hdr_size'] + self.header['size_x'] * self.header['size_z'] * 4)

        # Crop the rest of the b_scan_header
        self.b_scan_header['version'] = self.b_scan_header['version'][:, first_b_scan-1:last_b_scan]
        self.b_scan_header['b_scan_hdr_size'] = self.b_scan_header['b_scan_hdr_size'][first_b_scan-1:last_b_scan]
        self.b_scan_header['start_x'] = self.b_scan_header['start_x'][first_b_scan-1:last_b_scan]
        self.b_scan_header['start_y'] = self.b_scan_header['start_y'][first_b_scan-1:last_b_scan]
        self.b_scan_header['end_x'] = self.b_scan_header['end_x'][first_b_scan-1:last_b_scan]
        self.b_scan_header['end_y'] = self.b_scan_header['end_y'][first_b_scan-1:last_b_scan]
        self.b_scan_header['num_seg'] = self.b_scan_header['num_seg'][first_b_scan-1:last_b_scan]
        self.b_scan_header['off_seg'] = self.b_scan_header['off_seg'][first_b_scan-1:last_b_scan]
        self.b_scan_header['quality'] = self.b_scan_header['quality'][first_b_scan-1:last_b_scan]
        self.b_scan_header['shift'] = self.b_scan_header['shift'][first_b_scan-1:last_b_scan]
        self.b_scan_header['spare'] = self.b_scan_header['spare'][:, first_b_scan-1:last_b_scan]

        # Update grid type to ETDRS and reset the sector parameters, in case 6mm crop was selected. This helps later
        # when using programs like OCTMarker to correct because the volume is cropped to 6mm usually to cover ETDRS.
        if crop_size == 6:
            self.thickness_grid['type'] = np.int32(3)
            self.thickness_grid['diameter'] = np.array([1, 3, 6], dtype='float64')
            self.thickness_grid['central_thk'] = np.float32(0)
            self.thickness_grid['min_central_thk'] = np.float32(0)
            self.thickness_grid['max_central_thk'] = np.float32(0)
            self.thickness_grid['total_volume'] = np.float32(0)
            for i_sector in range(9):
                self.thickness_grid['sector_{}'.format(i_sector+1)]['thickness'] = np.float32(0)
                self.thickness_grid['sector_{}'.format(i_sector+1)]['volume'] = np.float32(0)
