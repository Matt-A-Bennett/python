"""Connected clusters cluster size thresholding."""

import os
import argparse
import numpy as np
from nibabel import load, save, Nifti1Image
from skimage.measure import label

parser = argparse.ArgumentParser()

parser.add_argument('filename',  metavar='path',
                    help="Path to nii file with image data")

parser.add_argument("--threshold", "-t", metavar='float',
                    required=False, type=float,
                    help="Binarization threshold for the input data (assign \
                    zero to anything below the number and 1 to above).")

parser.add_argument("--cluster_size", "-c", metavar='26',
                    required=False, default=26, type=int,
                    help="Minimum cluster size (voxels)")

parser.add_argument("--connectivity", "-cn", metavar='2',
                    required=False, default=2, type=int,
                    help="Maximum number of orthogonal hops to consider a \
                          pixel/voxel as a neighbor. Accepted values are \
                          ranging from 1 to input.ndim.")

parser.add_argument("--binarize_labels", "-bl",  metavar='1',
                    required=False, default=1, type=int,
                    help="Return binarized(1) or unbinarized(0) labels.")
args = parser.parse_args()

print('============================')
print('Connected clusters threshold')
print('============================')

nii = load(args.filename)
basename = nii.get_filename().split(os.extsep, 1)[0]
data = nii.get_data()
thr = args.threshold
c_thr = args.cluster_size

# binarize
if thr:
    print('Data will be intensity thresholded (' + str(thr) + ').')
    data = np.where(data <= thr, 0, 1)
else:
    print('Data will not be intensity thresholded.')

# connected clusters
data = label(data, connectivity=args.connectivity)
labels, counts = np.unique(data, return_counts=True)
print(str(labels.size) + ' clusters are found.')

print('Applying connected clusters threshold (' + str(c_thr) + ' voxels).')
for i, (i_label, i_count) in enumerate(zip(labels[1:], counts[1:])):
    if i_count < c_thr:
        data[data == i_label] = 0
data[data != 0] = 1

# output binarized or cluster connectedness thresholded data.
if args.binarize_labels == 1:
    print('Binarizing cluster labels.')
    out = Nifti1Image(data, header=nii.get_header(), affine=nii.get_affine())
    out_name = basename + '_thr' + str(thr) + '_c' + str(c_thr) + '_bin.nii.gz'
elif args.binarize_labels == 0:
    print('Not binarizing cluster labels.')
    orig = nii.get_data()
    orig[data == 0] = 0
    out = Nifti1Image(orig, header=nii.get_header(), affine=nii.get_affine())
    out_name = basename + '_thr' + str(thr) + '_c' + str(c_thr) + '.nii.gz'
else:
    print( "Incorrect binarization value. Enter 1 or 0.")

save(out, out_name)
print('\nSaved as: ' + out_name + '\n')
