## OCTVol

A package to work with optical coherence tomography .vol raw files from Heidelberg Engineering Spectralis device, providing functionalities to read, write, and crop these files.
 
The codes in this package are primarily derived from their MATLAB implementations, available as part of the open-source segmentation pipeline [SAMIRIX](https://github.com/sahmotamedi/am-SAMIRIX).

In addition to unit tests in the tests directory, extensive testing has been performed on all methods of the OCTVol class.

### Installation 

Install this package using pip:


```commandline
pip install oct-vol
```

### Usage 

Example usage in Python:

```python
from OCTVol import OCTVol
oct_vol = OCTVol(r"</path-to-vol-file.vol>")
oct_vol.crop_vol(crop_size=4)
oct_vol.write_vol(r"</destination-file-path.vol>")
```

### Requirements

The package was developed with Python 3.9.7 and numpy 1.20.3. It has been tested successfully with Python 3.5 and above.

### Contact

For inquiries, please contact Amir Motamedi at seyedamirhosein.motamedi(at)charite.de.

### License

Refer to LICENSE.txt for licensing details.

### Related Projects

Check out OCT-Converter, a package for various OCT file formats from different manufacturers, by Mark Graham at King's College London. Available on [PyPi](https://pypi.org/project/oct-converter/).

