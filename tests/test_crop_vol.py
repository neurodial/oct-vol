from OCTVol import OCTVol
import numpy as np
from glob import glob
import os


# Test 6mm crop
def test_vertical_6mm():
    mat_crop_dir = r"C:\Amir\data\OCT_test\crop_vol_test\Matlab_cropped_6"
    py_crop_dir = r"C:\Amir\data\OCT_test\crop_vol_test\Python_cropped_6"

    vol_files_list = glob(os.path.join(mat_crop_dir, '*.vol'))

    for vol_file_path in vol_files_list:
        mat_cropped_vol = OCTVol(vol_file_path)
        py_cropped_vol = OCTVol(vol_file_path.replace(mat_crop_dir, py_crop_dir))

        for key in mat_cropped_vol.header:
            if key in ['unconverted_exam_time', 'unconverted_visit_date', 'exam_time', 'visit_date']:
                assert type(mat_cropped_vol.header[key]) == type(py_cropped_vol.header[key])
            elif isinstance(mat_cropped_vol.header[key], np.ndarray):
                assert np.all(mat_cropped_vol.header[key] == py_cropped_vol.header[key])
                assert mat_cropped_vol.header[key].dtype == py_cropped_vol.header[key].dtype
            else:
                assert mat_cropped_vol.header[key] == py_cropped_vol.header[key]
                assert type(mat_cropped_vol.header[key]) == type(py_cropped_vol.header[key])

        assert np.all(mat_cropped_vol.slo == py_cropped_vol.slo)
        assert mat_cropped_vol.slo.dtype == py_cropped_vol.slo.dtype

        for key in mat_cropped_vol.b_scan_header:
            if isinstance(mat_cropped_vol.b_scan_header[key], np.ndarray):
                assert np.all(mat_cropped_vol.b_scan_header[key] == py_cropped_vol.b_scan_header[key])
                assert mat_cropped_vol.b_scan_header[key].dtype == py_cropped_vol.b_scan_header[key].dtype
            else:
                assert mat_cropped_vol.b_scan_header[key] == py_cropped_vol.b_scan_header[key]
                assert type(mat_cropped_vol.b_scan_header[key]) == type(py_cropped_vol.b_scan_header[key])

        assert np.all(mat_cropped_vol.b_scans == py_cropped_vol.b_scans)
        assert mat_cropped_vol.b_scans.dtype == py_cropped_vol.b_scans.dtype


# Test 3.5mm crop
def test_vertical_3_5mm():
    mat_crop_dir = r"C:\Amir\data\OCT_test\crop_vol_test\Matlab_cropped_3.5"
    py_crop_dir = r"C:\Amir\data\OCT_test\crop_vol_test\Python_cropped_3.5"

    vol_files_list = glob(os.path.join(mat_crop_dir, '*.vol'))

    for vol_file_path in vol_files_list:
        mat_cropped_vol = OCTVol(vol_file_path)
        py_cropped_vol = OCTVol(vol_file_path.replace(mat_crop_dir, py_crop_dir))

        for key in mat_cropped_vol.header:
            if key in ['unconverted_exam_time', 'unconverted_visit_date', 'exam_time', 'visit_date']:
                assert type(mat_cropped_vol.header[key]) == type(py_cropped_vol.header[key])
            elif isinstance(mat_cropped_vol.header[key], np.ndarray):
                assert np.all(mat_cropped_vol.header[key] == py_cropped_vol.header[key])
                assert mat_cropped_vol.header[key].dtype == py_cropped_vol.header[key].dtype
            else:
                assert mat_cropped_vol.header[key] == py_cropped_vol.header[key]
                assert type(mat_cropped_vol.header[key]) == type(py_cropped_vol.header[key])

        assert np.all(mat_cropped_vol.slo == py_cropped_vol.slo)
        assert mat_cropped_vol.slo.dtype == py_cropped_vol.slo.dtype

        for key in mat_cropped_vol.b_scan_header:
            if isinstance(mat_cropped_vol.b_scan_header[key], np.ndarray):
                assert np.all(mat_cropped_vol.b_scan_header[key] == py_cropped_vol.b_scan_header[key])
                assert mat_cropped_vol.b_scan_header[key].dtype == py_cropped_vol.b_scan_header[key].dtype
            else:
                assert mat_cropped_vol.b_scan_header[key] == py_cropped_vol.b_scan_header[key]
                assert type(mat_cropped_vol.b_scan_header[key]) == type(py_cropped_vol.b_scan_header[key])

        assert np.all(mat_cropped_vol.b_scans == py_cropped_vol.b_scans)
        assert mat_cropped_vol.b_scans.dtype == py_cropped_vol.b_scans.dtype

        for key in mat_cropped_vol.thickness_grid:
            if isinstance(mat_cropped_vol.thickness_grid[key], np.ndarray):
                assert np.all(mat_cropped_vol.thickness_grid[key] == py_cropped_vol.thickness_grid[key])
                assert mat_cropped_vol.thickness_grid[key].dtype == py_cropped_vol.thickness_grid[key].dtype
            else:
                assert mat_cropped_vol.thickness_grid[key] == py_cropped_vol.thickness_grid[key]
                assert type(mat_cropped_vol.thickness_grid[key]) == type(py_cropped_vol.thickness_grid[key])
