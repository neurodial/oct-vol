from OCTVol import OCTVol
import numpy as np
import pytest
import os


@pytest.fixture
def orig_vol():
    return OCTVol(r'C:\Amir\data\OCT_test\write_vol_test\EYE00023_8370.vol')


@pytest.fixture
def written_vol(orig_vol):
    temp_save_path = r'C:\Amir\data\OCT_test\write_vol_test\test.vol'
    orig_vol.write_vol(temp_save_path)
    yield OCTVol(temp_save_path)
    os.remove(temp_save_path)


def test_header(orig_vol, written_vol):
    for key in orig_vol.header:
        if isinstance(orig_vol.header[key], np.ndarray):
            assert np.all(written_vol.header[key] == orig_vol.header[key])
        else:
            assert written_vol.header[key] == orig_vol.header[key]


def test_slo(orig_vol, written_vol):
    assert np.all(orig_vol.slo == written_vol.slo)


def test_b_scan_header(orig_vol, written_vol):
    for key in orig_vol.b_scan_header:
        if isinstance(orig_vol.b_scan_header[key], np.ndarray):
            assert np.all(written_vol.b_scan_header[key] == orig_vol.b_scan_header[key])
        else:
            assert written_vol.b_scan_header[key] == orig_vol.b_scan_header[key]


def test_b_scans(orig_vol, written_vol):
    assert np.all(orig_vol.b_scans == written_vol.b_scans)


def test_thickness_grid(orig_vol, written_vol):
    for key in orig_vol.thickness_grid:
        if isinstance(orig_vol.thickness_grid[key], np.ndarray):
            assert np.all(written_vol.thickness_grid[key] == orig_vol.thickness_grid[key])
        else:
            assert written_vol.thickness_grid[key] == orig_vol.thickness_grid[key]

