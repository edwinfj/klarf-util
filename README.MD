#klarf utilities

.klarf is a standard format of a result from a defect inspection tool in semiconductor industry.
This repo serves as a collection of the utilities I created for manipulating klarf files.

- read_attr_from_klarf(klarf_file, attr_name): extract values of a attribute from a klarf file
- write_attr_to_klarf(klarf_file, defect_IDs, attr_values, target_file, attr_name): write values to an attribute in a klarf file, and save as a different file

===
requirements: python3.5, numpy

===
Copyright (c) 2016 by Jing Fang and KLA-Tencor Corp.

All rights reserved.
